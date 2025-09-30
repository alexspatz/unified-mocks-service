from datetime import datetime, timezone
import uuid
import random
import asyncio
from typing import Union
from models import (
    PaymentRequest, PaymentResponse,
    FiscalRequest, FiscalSuccessResponse, FiscalFailureResponse, FiscalReceipt, FiscalReceiptItem,
    KDSRequest, KDSSuccessResponse, KDSFailureResponse,
    ServiceMode, LogEntry, PendingRequest
)
from storage import storage

# Global reference to bot for sending messages
_bot_app = None

def set_bot_application(app):
    global _bot_app
    _bot_app = app


def generate_session_id(order_id: int) -> str:
    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y%m%dT%H%M%SZ")
    return f"{order_id}-{timestamp}"


def generate_field_90_raw(amount: int, response_code: str, response_message: str, auth_code: str = None, rrn: str = None) -> str:
    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y%m%d%H%M%S")

    if response_code == "00":  # Success
        return f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?><response><field id="0">{amount}</field><field id="4">643</field><field id="6">{timestamp}</field><field id="13">{auth_code}</field><field id="14">{rrn}</field><field id="15">{response_code}</field><field id="19">{response_message}</field><field id="21">{timestamp}</field><field id="23">0</field><field id="25">1</field><field id="26">0</field><field id="27">00092240</field><field id="28">11111111</field><field id="39">00</field></response>'''
    else:  # Failure
        return f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?><response><field id="0">{amount}</field><field id="4">643</field><field id="6">{timestamp}</field><field id="15">{response_code}</field><field id="19">{response_message}</field><field id="21">{timestamp}</field><field id="23">0</field><field id="25">1</field><field id="26">0</field><field id="27">00092240</field><field id="28">0</field><field id="39">53</field></response>'''


def generate_receipt_text() -> str:
    return """<html><body>
    <div style='font-family: monospace;'>
    ===========================<br>
    ТЕСТОВЫЙ ЧЕК<br>
    ===========================<br>
    Дата: """ + datetime.now(timezone.utc).strftime("%d.%m.%Y %H:%M") + """<br>
    Терминал: 00092240<br>
    ===========================<br>
    ОПЛАТА ОДОБРЕНА<br>
    ===========================<br>
    </div></body></html>"""


async def handle_payment_request(request: PaymentRequest) -> PaymentResponse:
    config = storage.get_config("payment")

    # Determine response type based on mode
    should_succeed = await determine_response("payment", config, request.dict())

    payment_id = storage.get_next_payment_id()
    session_id = generate_session_id(request.order_id)
    now = datetime.now(timezone.utc)
    payment_date = now.isoformat()
    completed_at = now.isoformat()

    if should_succeed:
        auth_code = str(random.randint(100000, 999999))
        rrn = f"{random.randint(1, 999999):012d}"
        response = PaymentResponse(
            payment_id=payment_id,
            order_id=request.order_id,
            session_id=session_id,
            status="SUCCESS",
            auth_code=auth_code,
            rrn=rrn,
            transaction_id="0",
            terminal_id="00092240",
            merchant_id="11111111",
            response_code="00",
            response_message="ОДОБРЕНО",
            amount=request.sum,
            currency_code="643",
            payment_date=payment_date,
            completed_at=completed_at,
            receipt_available=True,
            field_90_raw=generate_field_90_raw(request.sum, "00", "ОДОБРЕНО", auth_code, rrn),
            customer_receipt=generate_receipt_text(),
            merchant_receipt=generate_receipt_text()
        )
    else:
        response = PaymentResponse(
            payment_id=payment_id,
            order_id=request.order_id,
            session_id=session_id,
            status="DECLINED",
            auth_code=None,
            rrn=None,
            transaction_id="0",
            terminal_id="00092240",
            merchant_id="0",
            response_code="ER3",
            response_message="ОПЕРАЦИЯ ПРЕРВАНА^TERMINATED.JPG~",
            amount=request.sum,
            currency_code="643",
            payment_date=payment_date,
            completed_at=completed_at,
            receipt_available=False,
            field_90_raw=generate_field_90_raw(request.sum, "ER3", "ОПЕРАЦИЯ ПРЕРВАНА^TERMINATED.JPG~"),
            customer_receipt=None,
            merchant_receipt=None
        )

    # Log the request
    log = LogEntry(
        timestamp=now.isoformat(),
        service="payment",
        request=request.dict(),
        response=response.dict(),
        mode=config.mode.value,
        status=response.status
    )
    storage.add_log(log)

    # Send instant notification
    await send_log_notification(log)

    return response


async def handle_fiscal_request(request: FiscalRequest) -> Union[FiscalSuccessResponse, FiscalFailureResponse]:
    config = storage.get_config("fiscal")

    should_succeed = await determine_response("fiscal", config, request.dict())

    now = datetime.now(timezone.utc)

    if should_succeed:
        items = [
            FiscalReceiptItem(
                item_id=item.item_id,
                description=item.item_description,
                quantity=item.quantity,
                price_net=item.item_price_net,
                vat=item.item_vat_value,
                price_gross=item.item_price_gross
            )
            for item in request.items
        ]

        receipt = FiscalReceipt(
            ofd_reg_number="1234567890",
            fiscal_document_number=storage.get_next_fiscal_doc_number(),
            fn_number="TEST-FN-0000000000000",
            order_id=request.order_id,
            issued_at=now.isoformat(),
            items=items,
            total_net=request.total_net,
            total_vat=request.total_vat,
            total_gross=request.total_gross,
            message="Fiscal receipt generated (test)"
        )

        response = FiscalSuccessResponse(fiscal_receipt=receipt)
        status = "OK"
    else:
        response = FiscalFailureResponse(
            error_code="FISCAL_ERR_01",
            error_message="Fiscalization failed: OFD communication error (simulated)"
        )
        status = "NOT_OK"

    # Log the request
    log = LogEntry(
        timestamp=now.isoformat(),
        service="fiscal",
        request=request.dict(),
        response=response.dict(),
        mode=config.mode.value,
        status=status
    )
    storage.add_log(log)

    # Send instant notification
    await send_log_notification(log)

    return response


async def handle_kds_request(request: KDSRequest) -> Union[KDSSuccessResponse, KDSFailureResponse]:
    config = storage.get_config("kds")

    should_succeed = await determine_response("kds", config, request.dict())

    now = datetime.now(timezone.utc)

    if should_succeed:
        response = KDSSuccessResponse(
            kds_ticket_id=storage.get_next_kds_ticket_id(),
            received_at=now.isoformat()
        )
        status = "OK"
    else:
        response = KDSFailureResponse(
            error_code="KDS_ERR_01",
            error_message="KDS reject: kitchen busy (simulated)"
        )
        status = "NOT_OK"

    # Log the request
    log = LogEntry(
        timestamp=now.isoformat(),
        service="kds",
        request=request.dict(),
        response=response.dict(),
        mode=config.mode.value,
        status=status
    )
    storage.add_log(log)

    # Send instant notification
    await send_log_notification(log)

    return response


async def determine_response(service: str, config, request_data: dict = None) -> bool:
    """Determine if the response should be successful based on the service mode"""
    if config.mode == ServiceMode.AUTO_SUCCESS:
        return True
    elif config.mode == ServiceMode.AUTO_FAILURE:
        return False
    elif config.mode == ServiceMode.SEQUENCE:
        response = storage.get_next_sequence_response(service)
        return response == "SUCCESS"
    elif config.mode == ServiceMode.MANUAL:
        # Create pending request for manual handling
        request_id = str(uuid.uuid4())
        pending = PendingRequest(
            request_id=request_id,
            service=service,
            request_data=request_data or {},
            created_at=datetime.now(timezone.utc)
        )
        storage.add_pending_request(pending)

        # Send notification to Telegram
        if _bot_app:
            await send_manual_request_notification(service, request_id, request_data or {})

        # Wait for response with timeout
        timeout = config.timeout_seconds
        start_time = datetime.now(timezone.utc)

        while (datetime.now(timezone.utc) - start_time).total_seconds() < timeout:
            # Check if response received
            response_key = f"manual_response_{request_id}"
            if response_key in storage.manual_responses:
                response = storage.manual_responses[response_key]
                del storage.manual_responses[response_key]
                storage.remove_pending_request(request_id)
                return response == "SUCCESS" or response == "OK"

            await asyncio.sleep(0.5)

        # Timeout - use default response
        storage.remove_pending_request(request_id)
        return config.default_response == "SUCCESS" or config.default_response == "OK"

    return True


async def send_manual_request_notification(service: str, request_id: str, request_data: dict):
    """Send notification to Telegram for manual handling"""
    if not _bot_app:
        print("⚠️ Bot application not set")
        return

    from telegram_bot import TELEGRAM_ADMIN_IDS
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup

    if not TELEGRAM_ADMIN_IDS:
        print("⚠️ No admin IDs configured")
        return

    keyboard = [
        [
            InlineKeyboardButton("✅ Success", callback_data=f"manual_{request_id}_SUCCESS"),
            InlineKeyboardButton("❌ Failure", callback_data=f"manual_{request_id}_FAILURE")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Format request data
    data_str = "\n".join([f"  {k}: {v}" for k, v in request_data.items()])

    text = (
        f"👤 *Manual Request - {service.upper()}*\n\n"
        f"Request ID: `{request_id}`\n"
        f"Time: {datetime.now(timezone.utc).strftime('%H:%M:%S UTC')}\n\n"
        f"*Request Data:*\n{data_str}\n\n"
        f"Choose response:"
    )

    # Send to all admins
    for admin_id in TELEGRAM_ADMIN_IDS:
        try:
            await _bot_app.bot.send_message(
                chat_id=admin_id,
                text=text,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
            print(f"✅ Sent manual request to admin {admin_id}")
        except Exception as e:
            print(f"❌ Error sending manual request notification to {admin_id}: {e}")


async def send_log_notification(log: LogEntry):
    """Send log notification to admin via Telegram"""
    if not _bot_app:
        return

    from telegram_bot import TELEGRAM_ADMIN_IDS

    if not TELEGRAM_ADMIN_IDS:
        return

    emoji = "✅" if log.status in ["SUCCESS", "OK"] else "❌"
    time = datetime.fromisoformat(log.timestamp).strftime("%H:%M:%S")

    text = (
        f"{emoji} *{log.service.upper()}* - {log.status}\n"
        f"Time: `{time}`\n"
        f"Mode: `{log.mode}`"
    )

    # Send to all admins
    for admin_id in TELEGRAM_ADMIN_IDS:
        try:
            await _bot_app.bot.send_message(
                chat_id=admin_id,
                text=text,
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"Error sending log notification to {admin_id}: {e}")
