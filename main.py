from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk.errors import SlackApiError

from audit import AuditSession
import os
from db import update_users, create_tables, get_users

SLACK_BOT_TOKEN = os.environ['SLACK_BOT_TOKEN']
SLACK_APP_TOKEN = os.environ['SLACK_APP_TOKEN']


class AuditBot:
    create_tables()

    def __init__(self, slack_bot_token: str, slack_app_token: str):

        self.debug = False
        self.app = App(token=slack_bot_token)
        self.audit_session = None
        self.admins = [user.id for user in get_users('/admin_show')]
        # for future setup where audit name will be set from bot
        self.audit_name = "user_location"  # will be None

        # Define bot commands and event handlers
        # Audit control
        self.app.command("/audit_start")(self.admin_check(self.start_audit))
        self.app.command("/audit_stop")(self.admin_check(self.close_audit))
        self.app.command("/audit_unanswered")(self.admin_check(self.show_users))

        # User commands
        self.app.command("/answer")(self.collect_answer)
        self.app.command("/user_help")(self.show_user_help)
        self.app.command("/admin_show")(self.show_users)
        self.app.message()(self.shadow_answer)

        # Admin commands
        self.app.command("/users_update")(self.admin_check(self.update_users))
        self.app.command("/ignore_show")(self.admin_check(self.show_users))
        self.app.command("/ignore_update")(self.admin_check(self.update_ignore))

        # Not implemeted commands
        self.app.command("/audits_show")(self.admin_check(self.not_implemented))
        self.app.command("/audit_get")(self.admin_check(self.not_implemented))

        # Socket mode handler to connect the bot to Slack
        self.handler = SocketModeHandler(self.app, slack_app_token)

    def admin_check(self, func):
        """Decorator to check if the command is issued by an admin."""
        def wrapper(ack, body, say, *args, **kwargs):
            user_id = body["user_id"]
            if user_id not in self.admins:
                say("You are not authorized to perform this action.")
                return
            ack()
            return func(ack, body, say, *args, **kwargs)
        return wrapper

    def not_implemented(self, ack, body, say):
        ack()
        say("Command not implemented, yet.")

    def start_audit(self, ack, body, say):
        audit_message = body.get("text")
        say(f"Users will receive next message: \n{audit_message}")
        ack()  # Acknowledge the command
        if self.audit_session is not True:
            self.audit_session = AuditSession(self.audit_name, self.send_message)
            self.audit_session.open_session(audit_message)
        else:
            say("There is already an active audit session.")

    def send_message(self, user_id, message):
        if not self.debug:
            try:
                response = self.app.client.conversations_open(users=user_id)
                dm_channel_id = response["channel"]["id"]

                self.app.client.chat_postMessage(
                    channel=dm_channel_id,
                    text=message
                )
                print("yep, slack sent it")

            except SlackApiError as e:
                print(f"Error sending message: {e.response['error']}")
        else:
            print('Try to send message. Message not sent - debug enabled')


    def collect_answer(self, ack, body, say):
        ack()  # Acknowledge the command

        data = {
            'id': body['user_id'],
            'name': body.get('user_name'),
            'answer': body['text']
        }

        if self.audit_session.is_active:
            self.audit_session.add_response(data)
            say(f"Thank you <@{body['user_id']}>! Your response '{body['text']}' has been recorded.")
        else:
            say("No active audit session. Please wait until an audit is started.")

    def close_audit(self, ack, body, say):
        ack()  # Acknowledge the command
        channel_id = body.get('channel_id')
        # Close the global audit session
        if self.audit_session is not None:
            if self.audit_session.is_active:
                self.audit_session.close_session()
                audit_summary = self.audit_session.get_audit_summary()
                self.app.client.files_upload_v2(
                    channels=channel_id,
                    initial_comment="Audit closed!\nHere's report file :smile:",
                    file=audit_summary,
                )
                self.audit_session = None
            else:
                say("No active audit session to close.")
        else:
            say("No active audit session to close.")

    def update_users(self, ack, body, say):
        users = self.app.client.users_list()['members']
        update_users(users)
        say("Users updated")

    def update_ignore(self, ack, body, say):
        ack()
        users_to_ignore = body.get('text')
        users_to_ignore = users_to_ignore.split(' ')
        result = update_users(users_to_ignore, to_ignore=True, by_name=True)
        text = "Ignore list updated"
        if result:
            text += f"\nCould not find the following users: {', '.join(result)}"
        say(text)

    def update_admin(self, ack, body, say):
        ack()
        users_to_ignore = body.get('text')
        users_to_ignore = users_to_ignore.split(' ')
        update_users(users_to_ignore, to_admin=True, by_name=True)
        say("Admin list updated")

    def show_users(self, ack, body, say):
        ack()
        command_mapping = {
            "/ignore_show": "Ignored users:",
            "/admin_show": "Admin users:",
            "/audit_unanswered": "Audit unanswered:",
        }
        command_name = body.get('command')
        if not self.audit_session and command_name == "/audit_unanswered":
            say("There is no active audit session")
        else:
            users_to_show = get_users(command_name)
            if isinstance(users_to_show, str):
                say(users_to_show)
            else:
                users_to_show = '\n'.join(f'<@{user.id}>' for user in users_to_show)
                text = f"{command_mapping.get(command_name, 'Users:')}\n{users_to_show}"
                say(text)

    def show_user_help(self, ack, body, say):
        return (f'Use next command to answer:\n /answer <your_location>'
                f'For example:\n /answer Paris')

    def shadow_answer(self, ack, body, say):

        say(text='Sorry, do not understand. Use /help command or ask Inna.',
            channel=body.get('event').get('channel'),
            thread_ts=body.get('event').get('ts'))

    def start(self):
        self.handler.start()


if __name__ == "__main__":
    bot = AuditBot(slack_bot_token=SLACK_BOT_TOKEN, slack_app_token=SLACK_APP_TOKEN)
    bot.start()
