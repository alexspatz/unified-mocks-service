from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ServiceMode(str, Enum):
    AUTO_SUCCESS = "AUTO_SUCCESS"
    AUTO_FAILURE = "AUTO_FAILURE"
    MANUAL = "MANUAL"
    SEQUENCE = "SEQUENCE"


class ResponseStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    UNAVAILABLE = "UNAVAILABLE"


class SequenceConfig(BaseModel):
    success_count: int
    failure_count: int
    remaining: List[str] = []


class ServiceConfig(BaseModel):
    mode: ServiceMode
    timeout_seconds: int = 30
    default_response: str = "SUCCESS"
    sequence_config: Optional[SequenceConfig] = None


class PaymentRequest(BaseModel):
    kiosk_id: str
    order_id: int
    sum: int


class PaymentResponse(BaseModel):
    payment_id: int
    order_id: int
    session_id: str
    status: str
    auth_code: Optional[str] = None
    rrn: Optional[str] = None
    transaction_id: str
    terminal_id: str
    merchant_id: str
    response_code: str
    response_message: str
    amount: int
    currency_code: str
    payment_date: str
    completed_at: str
    receipt_available: bool
    field_90_raw: str
    customer_receipt: Optional[str] = None
    merchant_receipt: Optional[str] = None


# Old fiscal models (kept for backwards compatibility)
class FiscalItem(BaseModel):
    item_id: int
    item_description: str
    item_price_net: int
    item_price_gross: int
    item_vat_value: int
    quantity: int


class FiscalRequest(BaseModel):
    order_id: int
    kiosk_id: str
    items: List[FiscalItem]
    total_net: int
    total_vat: int
    total_gross: int
    payment_method: str


class FiscalReceiptItem(BaseModel):
    item_id: int
    description: str
    quantity: int
    price_net: int
    vat: int
    price_gross: int


class FiscalReceipt(BaseModel):
    ofd_reg_number: str
    fiscal_document_number: str
    fn_number: str
    order_id: int
    issued_at: str
    items: List[FiscalReceiptItem]
    total_net: int
    total_vat: int
    total_gross: int
    message: str


class FiscalSuccessResponse(BaseModel):
    status: str = "OK"
    fiscal_receipt: FiscalReceipt


class FiscalFailureResponse(BaseModel):
    status: str = "NOT_OK"
    error_code: str
    error_message: str


# New fiscal models (matching real API format)
class NewFiscalParams(BaseModel):
    total: float
    fnNumber: str
    registrationNumber: str
    fiscalDocumentNumber: int
    fiscalReceiptNumber: int
    fiscalDocumentSign: str
    fiscalDocumentDateTime: str
    shiftNumber: int
    fnsUrl: str


class NewFiscalError(BaseModel):
    code: int
    message: str


class NewFiscalSuccessResponse(BaseModel):
    success: bool = True
    error: Optional[Any] = None
    fiscalParams: NewFiscalParams


class NewFiscalFailureResponse(BaseModel):
    success: bool = False
    error: NewFiscalError
    fiscalParams: Optional[Any] = None


# Printer models
class PrinterSuccessResponse(BaseModel):
    success: bool = True
    error: Optional[Any] = None


class PrinterFailureResponse(BaseModel):
    success: bool = False
    error: str


class KDSItem(BaseModel):
    item_id: int
    description: str
    quantity: int


class KDSRequest(BaseModel):
    order_id: int
    kiosk_id: str
    items: List[KDSItem]


class KDSSuccessResponse(BaseModel):
    status: str = "OK"
    kds_ticket_id: str
    received_at: str


class KDSFailureResponse(BaseModel):
    status: str = "NOT_OK"
    error_code: str
    error_message: str


class LogEntry(BaseModel):
    timestamp: str
    service: str
    request: Dict[str, Any]
    response: Dict[str, Any]
    mode: str
    status: str


class ConfigUpdateRequest(BaseModel):
    payment: Optional[ServiceConfig] = None
    fiscal: Optional[ServiceConfig] = None
    kds: Optional[ServiceConfig] = None
    printer: Optional[ServiceConfig] = None


class PendingRequest(BaseModel):
    request_id: str
    service: str
    request_data: Dict[str, Any]
    created_at: datetime
    message_id: Optional[int] = None
