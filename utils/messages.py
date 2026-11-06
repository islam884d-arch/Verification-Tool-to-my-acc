"""English message templates for the bot."""
from config import CHANNEL_URL, VERIFY_COST, HELP_NOTION_URL


def get_welcome_message(full_name: str, invited_by: bool = False) -> str:
    """Build the welcome message."""
    msg = (
        f"🎉 Welcome, {full_name}!\n"
        "Your registration is complete. You received 1 point.\n"
    )
    if invited_by:
        msg += "Thanks for joining through an invite link. The inviter received 2 points.\n"
    msg += (
        "\nThis bot automates SheerID verification.\n"
        "Quick start:\n"
        "/about - Learn about the bot\n"
        "/balance - Check your points\n"
        "/help - View all commands\n\n"
        "Get more points:\n"
        "/qd - Daily check-in\n"
        "/invite - Invite a friend\n"
        f"Join the channel: {CHANNEL_URL}"
    )
    return msg


def get_about_message() -> str:
    """Build the about message."""
    return (
        "🤖 SheerID Verification Bot\n\n"
        "Features:\n"
        "- Automates SheerID student and teacher verification\n"
        "- Supports Gemini One Pro, ChatGPT Teacher K12, Spotify Student, YouTube Student, and Bolt.new Teacher\n\n"
        "Earn points:\n"
        "- Get 1 point when you register\n"
        "- Daily check-in: +1 point\n"
        "- Invite a friend: +2 points per person\n"
        "- Redeem a key according to its terms\n"
        f"- Join the channel: {CHANNEL_URL}\n\n"
        "How to use:\n"
        "1. Start verification on the website and copy the full verification link.\n"
        "2. Send /verify, /verify2, /verify3, /verify4, or /verify5 with the link.\n"
        "3. Wait for processing and check the result.\n"
        "4. Bolt.new codes are retrieved automatically. To check manually, use /getV4Code <verification_id>.\n\n"
        "Send /help to see more commands."
    )


def get_help_message(is_admin: bool = False) -> str:
    """Build the help message."""
    msg = (
        "📖 SheerID Verification Bot - Help\n\n"
        "User commands:\n"
        "/start - Register and get started\n"
        "/about - Learn about the bot\n"
        "/balance - Check your points\n"
        "/qd - Daily check-in (+1 point)\n"
        "/invite - Create an invite link (+2 points per person)\n"
        "/use <key> - Redeem a key for points\n"
        f"/verify <link> - Gemini One Pro verification (-{VERIFY_COST} points)\n"
        f"/verify2 <link> - ChatGPT Teacher K12 verification (-{VERIFY_COST} points)\n"
        f"/verify3 <link> - Spotify Student verification (-{VERIFY_COST} points)\n"
        f"/verify4 <link> - Bolt.new Teacher verification (-{VERIFY_COST} points)\n"
        f"/verify5 <link> - YouTube Student Premium verification (-{VERIFY_COST} points)\n"
        "/getV4Code <verification_id> - Get a Bolt.new verification code\n"
        "/help - Show this help message\n"
        f"Troubleshooting: {HELP_NOTION_URL}\n"
    )
    if is_admin:
        msg += (
            "\nAdmin commands:\n"
            "/addbalance <user_id> <points> - Add points to a user\n"
            "/block <user_id> - Block a user\n"
            "/white <user_id> - Unblock a user\n"
            "/blacklist - View blocked users\n"
            "/genkey <key> <points> [uses] [days] - Generate a redemption key\n"
            "/listkeys - View redemption keys\n"
            "/broadcast <text> - Send a message to all users\n"
        )
    return msg


def get_insufficient_balance_message(current_balance: int) -> str:
    """Build the insufficient balance message."""
    return (
        f"Not enough points. You need {VERIFY_COST}, and you have {current_balance}.\n\n"
        "Ways to earn points:\n"
        "- Daily check-in: /qd\n"
        "- Invite a friend: /invite\n"
        "- Redeem a key: /use <key>"
    )


def get_verify_usage_message(command: str, service_name: str) -> str:
    """Build verification command instructions."""
    return (
        f"Usage: {command} <SheerID link>\n\n"
        "Example:\n"
        f"{command} https://services.sheerid.com/verify/xxx/?verificationId=xxx\n\n"
        "How to get a verification link:\n"
        f"1. Visit the {service_name} verification page.\n"
        "2. Start the verification process.\n"
        "3. Copy the full URL from your browser's address bar.\n"
        f"4. Submit it with the {command} command."
    )
