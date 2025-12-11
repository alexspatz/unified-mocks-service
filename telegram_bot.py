import os
import asyncio
from typing import Optional
from datetime import datetime, timezone
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler
)
from models import ServiceMode, ServiceConfig, SequenceConfig
from storage import storage

# Environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_ADMIN_IDS = [int(id.strip()) for id in os.getenv("TELEGRAM_ADMIN_IDS", "").split(",") if id.strip()]
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Conversation states
SELECT_SERVICE, SELECT_MODE, INPUT_SEQUENCE = range(3)


def is_admin(user_id: int) -> bool:
    return user_id in TELEGRAM_ADMIN_IDS


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Access denied")
        return

    await update.message.reply_text(
        "🤖 *Unified Mocks Service*\n\n"
        "Available commands:\n"
        "/status - Service status\n"
        "/status\\_detailed - Detailed status\n"
        "/config - Configure services\n"
        "/config\\_all - Configure all services\n"
        "/logs - View recent logs\n"
        "/help - Help",
        parse_mode="Markdown"
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show brief status of all services"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Access denied")
        return

    configs = storage.get_all_configs()

    status_text = "📊 *Services Status*\n\n"

    for service_name, config in configs.items():
        emoji = "✅" if config.mode == ServiceMode.AUTO_SUCCESS else "❌" if config.mode == ServiceMode.AUTO_FAILURE else "👤" if config.mode == ServiceMode.MANUAL else "🔄"
        status_text += f"{emoji} *{service_name.upper()}*: {config.mode.value}\n"

    await update.message.reply_text(status_text, parse_mode="Markdown")


async def status_detailed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show detailed status with sequence information"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Access denied")
        return

    configs = storage.get_all_configs()

    status_text = "📊 *Detailed Services Status*\n\n"

    for service_name, config in configs.items():
        emoji = "✅" if config.mode == ServiceMode.AUTO_SUCCESS else "❌" if config.mode == ServiceMode.AUTO_FAILURE else "👤" if config.mode == ServiceMode.MANUAL else "🔄"
        status_text += f"{emoji} *{service_name.upper()}*\n"
        status_text += f"  Mode: `{config.mode.value}`\n"
        status_text += f"  Delay: {config.delay_seconds}s\n"
        status_text += f"  Timeout: {config.timeout_seconds}s\n"
        status_text += f"  Default: {config.default_response}\n"

        if config.mode == ServiceMode.SEQUENCE and config.sequence_config:
            seq = config.sequence_config
            status_text += f"  Sequence: {seq.success_count} success, {seq.failure_count} failure\n"
            status_text += f"  Remaining: {len(seq.remaining)} responses\n"

        status_text += "\n"

    await update.message.reply_text(status_text, parse_mode="Markdown")


async def config_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start configuration conversation"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Access denied")
        return ConversationHandler.END

    keyboard = [
        [InlineKeyboardButton("💳 Payment", callback_data="service_payment")],
        [InlineKeyboardButton("🧾 Fiscal", callback_data="service_fiscal")],
        [InlineKeyboardButton("🖨 Printer", callback_data="service_printer")],
        [InlineKeyboardButton("🍽 KDS", callback_data="service_kds")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "⚙️ *Service Configuration*\n\nSelect service to configure:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

    return SELECT_SERVICE


async def select_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle service selection"""
    query = update.callback_query
    await query.answer()

    if query.data == "cancel":
        await query.edit_message_text("❌ Configuration cancelled")
        return ConversationHandler.END

    service = query.data.replace("service_", "")
    context.user_data["selected_service"] = service

    keyboard = [
        [InlineKeyboardButton("✅ Always Success", callback_data="mode_AUTO_SUCCESS")],
        [InlineKeyboardButton("❌ Always Failure", callback_data="mode_AUTO_FAILURE")],
        [InlineKeyboardButton("👤 Manual Mode", callback_data="mode_MANUAL")],
        [InlineKeyboardButton("🔄 Sequence", callback_data="mode_SEQUENCE")],
        [InlineKeyboardButton("« Back", callback_data="back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        f"⚙️ *Configure {service.upper()}*\n\nSelect mode:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

    return SELECT_MODE


async def select_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle mode selection"""
    query = update.callback_query
    await query.answer()

    if query.data == "back":
        return await config_start(update, context)

    mode = query.data.replace("mode_", "")
    service = context.user_data["selected_service"]

    if mode == "SEQUENCE":
        await query.edit_message_text(
            "🔄 *Sequence Configuration*\n\n"
            "Enter sequence in format: `success_count,failure_count`\n"
            "Example: `5,2` (5 successes, 2 failures)",
            parse_mode="Markdown"
        )
        context.user_data["selected_mode"] = mode
        return INPUT_SEQUENCE

    # Update configuration
    config = ServiceConfig(
        mode=ServiceMode(mode),
        timeout_seconds=30,
        default_response="SUCCESS" if service in ["payment", "fiscal", "printer"] else "OK"
    )
    storage.update_config(service, config)

    await query.edit_message_text(
        f"✅ *{service.upper()}* configured\n\n"
        f"Mode: `{mode}`",
        parse_mode="Markdown"
    )

    return ConversationHandler.END


async def input_sequence(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle sequence input"""
    service = context.user_data["selected_service"]

    try:
        success_count, failure_count = map(int, update.message.text.split(","))

        config = ServiceConfig(
            mode=ServiceMode.SEQUENCE,
            timeout_seconds=30,
            default_response="SUCCESS" if service in ["payment", "fiscal", "printer"] else "OK",
            sequence_config=SequenceConfig(
                success_count=success_count,
                failure_count=failure_count
            )
        )
        storage.update_config(service, config)

        await update.message.reply_text(
            f"✅ *{service.upper()}* configured\n\n"
            f"Mode: SEQUENCE\n"
            f"Success: {success_count}\n"
            f"Failure: {failure_count}",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(
            f"❌ Invalid format. Use: `success_count,failure_count`\n"
            f"Example: `5,2`",
            parse_mode="Markdown"
        )
        return INPUT_SEQUENCE

    return ConversationHandler.END


async def config_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Configure all services at once"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Access denied")
        return

    keyboard = [
        [InlineKeyboardButton("✅ All Success", callback_data="all_AUTO_SUCCESS")],
        [InlineKeyboardButton("❌ All Failure", callback_data="all_AUTO_FAILURE")],
        [InlineKeyboardButton("👤 All Manual", callback_data="all_MANUAL")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "⚙️ *Configure All Services*\n\nSelect mode for all:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def config_all_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle config all callback"""
    query = update.callback_query
    await query.answer()

    if query.data == "cancel":
        await query.edit_message_text("❌ Configuration cancelled")
        return

    mode = query.data.replace("all_", "")

    for service in ["payment", "fiscal", "kds", "printer"]:
        config = ServiceConfig(
            mode=ServiceMode(mode),
            timeout_seconds=30,
            default_response="SUCCESS" if service in ["payment", "fiscal", "printer"] else "OK"
        )
        storage.update_config(service, config)

    await query.edit_message_text(
        f"✅ *All services configured*\n\n"
        f"Mode: `{mode}`",
        parse_mode="Markdown"
    )


async def logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show recent logs"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Access denied")
        return

    limit = 10
    if context.args and context.args[0].isdigit():
        limit = min(int(context.args[0]), 50)

    log_entries = storage.get_logs(limit)

    if not log_entries:
        await update.message.reply_text("📋 No logs available")
        return

    logs_text = f"📋 *Last {len(log_entries)} logs*\n\n"

    for log in log_entries:
        emoji = "✅" if log.status in ["SUCCESS", "OK"] else "❌"
        time = datetime.fromisoformat(log.timestamp).strftime("%H:%M:%S")
        logs_text += f"{emoji} `{time}` {log.service.upper()} - {log.status}\n"

    await update.message.reply_text(logs_text, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help"""
    await update.message.reply_text(
        "🤖 *Unified Mocks Service Help*\n\n"
        "*Commands:*\n"
        "/status - Brief service status\n"
        "/status\\_detailed - Detailed status with sequences\n"
        "/config - Configure individual service\n"
        "/config\\_all - Configure all services\n"
        "/delay - Set response delay for services\n"
        "/logs \\[N\\] - Show last N logs (default 10, max 50)\n"
        "/help - This help message\n\n"
        "*Modes:*\n"
        "✅ AUTO\\_SUCCESS - Always return success\n"
        "❌ AUTO\\_FAILURE - Always return failure\n"
        "👤 MANUAL - Manual approval via Telegram\n"
        "🔄 SEQUENCE - Configurable success/failure sequence",
        parse_mode="Markdown"
    )


async def delay_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set delay for services"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Access denied")
        return

    keyboard = [
        [InlineKeyboardButton("💳 Payment", callback_data="delay_payment")],
        [InlineKeyboardButton("🧾 Fiscal", callback_data="delay_fiscal")],
        [InlineKeyboardButton("🖨 Printer", callback_data="delay_printer")],
        [InlineKeyboardButton("🍽 KDS", callback_data="delay_kds")],
        [InlineKeyboardButton("🌐 All Services", callback_data="delay_all")],
        [InlineKeyboardButton("❌ Cancel", callback_data="delay_cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Show current delays
    configs = storage.get_all_configs()
    delays_text = "\n".join([f"  {s.upper()}: {c.delay_seconds}s" for s, c in configs.items()])

    await update.message.reply_text(
        f"⏱ *Response Delay Configuration*\n\n"
        f"*Current delays:*\n{delays_text}\n\n"
        f"Select service to configure:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def delay_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle delay configuration callback"""
    query = update.callback_query
    await query.answer()

    if query.data == "delay_cancel":
        await query.edit_message_text("❌ Delay configuration cancelled")
        return

    # Extract service from callback
    service = query.data.replace("delay_", "")
    context.user_data["delay_service"] = service

    keyboard = [
        [
            InlineKeyboardButton("0s", callback_data="setdelay_0"),
            InlineKeyboardButton("5s", callback_data="setdelay_5"),
            InlineKeyboardButton("10s", callback_data="setdelay_10")
        ],
        [
            InlineKeyboardButton("15s", callback_data="setdelay_15"),
            InlineKeyboardButton("30s", callback_data="setdelay_30"),
            InlineKeyboardButton("45s", callback_data="setdelay_45")
        ],
        [
            InlineKeyboardButton("60s", callback_data="setdelay_60"),
            InlineKeyboardButton("90s", callback_data="setdelay_90"),
            InlineKeyboardButton("120s", callback_data="setdelay_120")
        ],
        [InlineKeyboardButton("« Back", callback_data="delay_back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    service_name = "All Services" if service == "all" else service.upper()
    await query.edit_message_text(
        f"⏱ *Set Delay for {service_name}*\n\n"
        f"Select delay duration:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def setdelay_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle setting the actual delay value"""
    query = update.callback_query
    await query.answer()

    if query.data == "delay_back":
        # Go back to service selection
        return await delay_command(update, context)

    delay = int(query.data.replace("setdelay_", ""))
    service = context.user_data.get("delay_service", "all")

    if service == "all":
        services = ["payment", "fiscal", "kds", "printer"]
    else:
        services = [service]

    for svc in services:
        config = storage.get_config(svc)
        config.delay_seconds = delay
        storage.update_config(svc, config)

    service_name = "All Services" if service == "all" else service.upper()
    await query.edit_message_text(
        f"✅ *Delay Updated*\n\n"
        f"Service: {service_name}\n"
        f"Delay: {delay} seconds",
        parse_mode="Markdown"
    )


async def handle_manual_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle manual response from inline button"""
    query = update.callback_query
    await query.answer()

    # Parse callback data: "manual_<request_id>_<response>"
    parts = query.data.split("_")
    if len(parts) != 3:
        return

    request_id = parts[1]
    response = parts[2]

    pending = storage.get_pending_request(request_id)
    if not pending:
        await query.edit_message_text("⚠️ Request expired or already processed")
        return

    # Store response for the waiting request
    response_key = f"manual_response_{request_id}"
    storage.manual_responses[response_key] = response

    emoji = "✅" if response == "SUCCESS" else "❌"
    await query.edit_message_text(
        f"{emoji} *Manual Response Recorded*\n\n"
        f"Service: {pending.service.upper()}\n"
        f"Response: {response}",
        parse_mode="Markdown"
    )


async def send_manual_request_notification(service: str, request_id: str, request_data: dict):
    """Send notification to Telegram for manual handling"""
    if not TELEGRAM_CHAT_ID or not TELEGRAM_BOT_TOKEN:
        return

    keyboard = [
        [
            InlineKeyboardButton("✅ Success", callback_data=f"manual_{request_id}_SUCCESS"),
            InlineKeyboardButton("❌ Failure", callback_data=f"manual_{request_id}_FAILURE")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = (
        f"👤 *Manual Request - {service.upper()}*\n\n"
        f"Request ID: `{request_id}`\n"
        f"Time: {datetime.now(timezone.utc).strftime('%H:%M:%S')}\n\n"
        f"Choose response:"
    )

    # This would be sent via the bot application
    # Implementation depends on how the bot is integrated with FastAPI


def create_bot_application() -> Application:
    """Create and configure the bot application"""
    if not TELEGRAM_BOT_TOKEN:
        return None

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("status_detailed", status_detailed))
    application.add_handler(CommandHandler("logs", logs))
    application.add_handler(CommandHandler("help", help_command))

    # Config conversation handler
    from telegram.ext import MessageHandler, filters

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("config", config_start)],
        states={
            SELECT_SERVICE: [CallbackQueryHandler(select_service)],
            SELECT_MODE: [CallbackQueryHandler(select_mode)],
            INPUT_SEQUENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_sequence)]
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)],
        per_message=False,
        per_chat=True,
        per_user=True,
        allow_reentry=True
    )
    application.add_handler(conv_handler)

    # Config all handler
    application.add_handler(CommandHandler("config_all", config_all))
    application.add_handler(CallbackQueryHandler(config_all_callback, pattern="^all_"))

    # Delay handlers
    application.add_handler(CommandHandler("delay", delay_command))
    application.add_handler(CallbackQueryHandler(delay_callback, pattern="^delay_"))
    application.add_handler(CallbackQueryHandler(setdelay_callback, pattern="^setdelay_"))

    # Manual response handler
    application.add_handler(CallbackQueryHandler(handle_manual_response, pattern="^manual_"))

    return application


# Global bot application
bot_application: Optional[Application] = None


async def start_bot():
    """Start the bot"""
    global bot_application

    if not TELEGRAM_BOT_TOKEN:
        print("⚠️ TELEGRAM_BOT_TOKEN not set, bot disabled")
        return

    if not TELEGRAM_ADMIN_IDS:
        print("⚠️ TELEGRAM_ADMIN_IDS not set, bot will not work properly")

    print(f"🤖 Starting Telegram bot...")
    print(f"   Token: {TELEGRAM_BOT_TOKEN[:20]}...")
    print(f"   Admin IDs: {TELEGRAM_ADMIN_IDS}")

    bot_application = create_bot_application()
    await bot_application.initialize()
    await bot_application.start()
    await bot_application.updater.start_polling()
    print("✅ Telegram bot started successfully")


async def stop_bot():
    """Stop the bot"""
    global bot_application

    if bot_application:
        await bot_application.updater.stop()
        await bot_application.stop()
        await bot_application.shutdown()


def get_bot_application() -> Optional[Application]:
    """Get the current bot application instance"""
    return bot_application
