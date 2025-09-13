import json
import os
import typing as tp
from typing import Any
from slack_sdk.web.slack_response import SlackResponse


class SlashCommandVerificator:
    # ToDo: check how provide credentials correctly
    app_id = os.environ.get("SLACK_APP_ID")
    app_token = os.environ.get("SLACK_BOT_OWNER_TOKEN")

    def __init__(self, app):
        self.app = app
        self.config_path = os.environ.get("SLACK_SLACK_COMMANDS_CONFIG_PATH")
        self._config = None
        self._manifest = None

    def verify(self) -> bool:
        """Main verification method that returns structured results"""
        manifest = self._fetch_app_manifest()
        commands_from_bot = self._extract_commands(manifest)
        commands_from_config = self._load_config()
        existed, absent = self._compare_commands(commands_from_bot, commands_from_config)
        if not absent:
            return True
        else:
            return False




    def _load_config(self) -> dict:
        """Load slash commands configuration"""
        with open(self.config_path, "r") as f:
            return json.load(f)

    def _fetch_app_manifest(self) -> SlackResponse:
        """Fetch app manifest from Slack API"""
        return self.app.client.apps_manifest_export(app_id=self.app_id, token=self.app_token)

    def _extract_commands(self, manifest: SlackResponse) -> dict:
        """Extract commands from Slack API"""
        return manifest.data.get('manifest').get('features').get('slash_commands')

    def _compare_commands(self, from_bot, from_config) -> tuple[list[tp.Dict[str, str]], list[tp.Dict[str, str]]]:
        """Compare bot`s commands vs configured commands"""
        existed_commands = []
        absent_commands = []
        for command in from_bot:
            command = command['command'][1:]
            if command in from_config:
                existed_commands.append(from_config.pop(command))
                print(f"command {command} exists")
            else:
                absent_commands.append(from_config.pop(command))
                print(f"command {command} does not exist")
        absent_commands.extend([command for command in from_config.values()])
        return existed_commands, absent_commands
