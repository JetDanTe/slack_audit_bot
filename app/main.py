from slack_bot import AuditBot
from admin.slash_commands import SlashCommandVerificator

if __name__ == "__main__":
    bot = AuditBot(debug=False)
    if SlashCommandVerificator(bot.app).verify():
        print("Slack Audit Bot Verified")
    else:
        print("Slack Audit Bot Not Verified\nNot all slash commands were installed")
        exit(1)

    bot.start()
