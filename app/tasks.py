"""Background tasks using Celery."""

import logging
from celery import current_task
from app.core.celery import celery_app
from services.slack_service import SlackService
from services.telegram_service import TelegramService
from services.sheets_service import SheetsService

logger = logging.getLogger(__name__)


@celery_app.task
def health_check():
    """Periodic health check task."""
    logger.info("Performing health check")
    return {"status": "healthy", "task": "health_check"}


@celery_app.task
def send_message_async(service: str, **kwargs):
    """Send message asynchronously to specified service."""
    try:
        if service == "slack":
            slack_service = SlackService()
            result = slack_service.send_message(
                channel=kwargs.get("channel"),
                text=kwargs.get("text"),
                thread_ts=kwargs.get("thread_ts")
            )
        elif service == "telegram":
            telegram_service = TelegramService()
            result = telegram_service.send_message(
                chat_id=kwargs.get("chat_id"),
                text=kwargs.get("text"),
                parse_mode=kwargs.get("parse_mode", "HTML"),
                reply_to_message_id=kwargs.get("reply_to_message_id")
            )
        else:
            return {"success": False, "error": f"Unknown service: {service}"}
        
        logger.info(f"Async message sent via {service}: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error in async message task: {str(e)}")
        return {"success": False, "error": str(e)}


@celery_app.task
def append_to_sheet_async(spreadsheet_id: str, range_name: str, values: list):
    """Append data to Google Sheet asynchronously."""
    try:
        sheets_service = SheetsService()
        result = sheets_service.append_row(
            spreadsheet_id=spreadsheet_id,
            range_name=range_name,
            values=values
        )
        
        logger.info(f"Async sheet append completed: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error in async sheet task: {str(e)}")
        return {"success": False, "error": str(e)}


@celery_app.task
def process_webhook_data(webhook_type: str, data: dict):
    """Process webhook data asynchronously."""
    try:
        logger.info(f"Processing {webhook_type} webhook data")
        
        # Here you could implement webhook processing logic
        # For example, storing messages, triggering notifications, etc.
        
        if webhook_type == "slack":
            # Process Slack webhook
            event = data.get("event", {})
            if event.get("type") == "message":
                logger.info(f"Processing Slack message: {event.get('text', '')}")
        
        elif webhook_type == "telegram":
            # Process Telegram webhook
            message = data.get("message", {})
            if message:
                logger.info(f"Processing Telegram message: {message.get('text', '')}")
        
        return {"success": True, "processed": True}
        
    except Exception as e:
        logger.error(f"Error processing webhook data: {str(e)}")
        return {"success": False, "error": str(e)}
