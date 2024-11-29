import time
import datetime
import os
import pandas as pd

from db import create_audit_table, get_users, check_if_table_exist, add_row, select_table


class AuditSession:
    def __init__(self, table_name, send_message, reminder=None):
        self.is_active = False
        # self.app = app
        self.responses = {}
        self.admins = None
        self.reminder_time = self._format_time("2h") if not reminder else reminder
        self.today = datetime.datetime.now().strftime('%d%m%Y')
        self.table_name = f"{table_name}_{self.today}"
        self.author = None
        self.reminder_message = "Kindly reminder!:arrow-up:"
        self.send_message = send_message
        self.audits_folder = 'audit_files'
        self.create_audit_folder()

    def create_audit_folder(self):
        if not os.path.exists(self.audits_folder):
            os.makedirs(self.audits_folder)

    def get_target_users(self, command):
        return get_users(command, second_table=self.table)

    def start_audit(self, audit_message):
        self.table = check_if_table_exist(self.table_name)
        if self.table is None:
            create_audit_table(self.table_name)
            self.table = check_if_table_exist(self.table_name)
        while self.is_active:
            target_users = get_users('/audit_unanswered', self.table)
            target_users = [user.id for user in target_users]
            for user in target_users:
                self.send_message(user, audit_message)
            audit_message = self.reminder_message
            time.sleep(self.reminder_time)

    def add_response(self, data: dict):
        if self.is_active:
            add_row(self.table, data)
        else:
            raise ValueError("No active audit session")

    def open_session(self, audit_message: str):
        self.is_active = True
        self.start_audit(audit_message)

    def close_session(self):
        self.is_active = False

    def get_audit_summary(self):
        table = select_table(self.table)
        file_name = os.path.join(self.audits_folder, self.table_name + '.xlsx')
        columns = ['Name', 'Location']
        data = [(tuple(row)[1], tuple(row)[2]) for row in table]
        df = pd.DataFrame(data, columns=columns)
        df.to_excel(file_name, index=False)
        return file_name

    def _format_time(self, time_str):
        number = int(time_str[:-1])
        unit = time_str[-1]

        if unit == 'h':
            return number * 3600
        elif unit == 'm':
            return number * 60
        elif unit == 's':
            return number
        else:
            print(ValueError("Unsupported time unit!\nUse default 2h value"))
            return number * 3600


if __name__ == '__main__':
    audit = AuditSession()
