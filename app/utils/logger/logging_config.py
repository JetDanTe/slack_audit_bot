import logging
import logging.config
import os
import sys
from datetime import datetime


def setup_logging():
    """Configure logging for the entire application"""

    # Log level from environment
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()

    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)

    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'detailed': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            },
            'simple': {
                'format': '%(levelname)s - %(name)s - %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': log_level,
                'formatter': 'detailed',
                'stream': sys.stdout  # Important for Docker
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': log_level,
                'formatter': 'detailed',
                'filename': f'logs/slack_audit_{datetime.now().strftime("%Y%m%d")}.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5
            }
        },
        'loggers': {
            'slack_audit_bot': {  # Your app's root logger
                'level': log_level,
                'handlers': ['console', 'file'],
                'propagate': False
            },
            'slack_sdk': {  # Slack SDK logs
                'level': 'WARNING',  # Less verbose for external lib
                'handlers': ['console', 'file'],
                'propagate': False
            }
        },
        'root': {
            'level': log_level,
            'handlers': ['console']
        }
    }

    logging.config.dictConfig(logging_config)
    return logging.getLogger('slack_audit_bot')

def get_logger(name: str) -> logging.Logger:
    """Get a logger for any module - call this in each file"""
    return logging.getLogger(f'slack_audit_bot.{name}')