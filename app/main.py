from slack_bot import AuditBot
from admin.slash_commands import SlashCommandVerificator
from utils.logger.logging_config import setup_logging, get_logger
import os
import slack_sdk.errors as slack_errors
from cli import get_args

setup_logging()
logger = get_logger('main')

if __name__ == "__main__":
    args = get_args()
    logger.info("Starting Slack Audit Bot")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")

    try:
        logger.info("Initializing AuditBot")
        bot = AuditBot(debug=False)

        if args.verify_slash_commands:
            logger.info("Starting slash command verification")
            verificator = SlashCommandVerificator(bot.app)
            results = verificator.verify()

            if results['success']:
                logger.info("All slash commands verified successfully")
            else:
                logger.warning(f"Verification issues found: {len(results['missing_commands'])} missing commands")
                logger.debug(f"Missing commands: {results['missing_commands']}")
                exit(1)

        logger.info("Starting bot")
        bot.start()




    except KeyboardInterrupt:
        logger.info("Bot stopped by user")

    except Exception as e:
        logger.critical(f"Application failed to start: {e}", exc_info=True)
        raise
