import argparse

def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="CLI interface for Slack Audit Bot"
    )

    # Positional argument
    parser.add_argument(
        "--verify_slash_commands",
        help="Verify slash commands before usage",
        action="store_true"
    )


    args = parser.parse_args()

    return args
