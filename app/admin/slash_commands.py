import json
import os
import sys
import typing as tp
from typing import Any
from slack_sdk.web.slack_response import SlackResponse
from pathlib import Path
import logging
import slack_sdk.errors as slack_errors



app_path = Path(__file__).parent
sys.path.append(str(app_path))

from utils.logger.logging_config import setup_logging



class SlashCommandVerificator:
    # ToDo: check how provide credentials correctly
    app_id = os.environ.get("SLACK_APP_ID")
    app_token = os.environ.get("SLACK_BOT_OWNER_TOKEN")

    def __init__(self, app):
        self.app = app
        self.config_path = os.environ.get("SLACK_SLACK_COMMANDS_CONFIG_PATH")
        self.logger = logging.getLogger('slack_audit_bot.verificator')
        self._config = None
        self._manifest = None

    def verify(self) -> dict[str, bool | list[dict[str, str]] | int]:
        """Main verification method that returns structured results"""
        self.logger.info("Starting slash command verification")

        try:
            manifest = self._fetch_app_manifest()
            commands_from_bot = self._extract_commands(manifest)
            commands_from_config = self._load_config()
            existed, absent = self._compare_commands(commands_from_bot, commands_from_config)
            return {
                'success': not absent,
                'existed_commands': existed,
                'missing_commands': absent,
                'total_configured': len(commands_from_config),
                'total_declared': len(commands_from_bot)
            }
        except Exception as e:
            self.logger.error(f"Verification failed: {e}", exc_info=True)
            raise



    def _load_config(self) -> dict:
        """Load slash commands configuration"""
        try:
            with open(self.config_path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise ValueError(f"Config loading failed: {e}")

    def _fetch_app_manifest(self) -> SlackResponse:
        """Fetch app manifest from Slack API"""
        return self.app.client.apps_manifest_export(app_id=self.app_id, token=self.app_token)

    def _extract_commands(self, manifest: SlackResponse) -> dict:
        """Extract commands from Slack API"""
        try:
            manifest = manifest.data.get('manifest').get('features').get('slash_commands')
            return manifest
        except slack_errors.SlackApiError:
            self.logger.warning("App configuration token is expired")


    def _compare_commands(self, from_bot, from_config) -> tuple[list[tp.Dict[str, str]], list[tp.Dict[str, str]]]:
        """Compare bot`s commands vs configured commands"""
        config_copy = from_config.copy()  # Don't modify original
        existed_commands = []
        absent_commands = []
        for command_data in from_bot:
            command = command_data['command'][1:]
            if command in config_copy:
                existed_commands.append(config_copy.pop(command))
                self.logger.debug(f"Command '{command}' exists in config")
            else:
                absent_commands.append(command_data)
                self.logger.warning(f"Command '{command}' not found in config")

        for remaining_cmd in config_copy.values():
            self.logger.warning(f"Configured command '{remaining_cmd}' not declared in bot")

        absent_commands.extend(list(config_copy.values()))
        return existed_commands, absent_commands
