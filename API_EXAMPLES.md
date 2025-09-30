# API Examples - Unified Mocks Service

Полная документация всех эндпоинтов с примерами запросов и возможных ответов для настройки киоска.

---

## 1. Payment Edge Mock

### Endpoint
```
POST /mocks/payment
```

### Request
```json
{
  "kiosk_id": "kiosk_001",
  "order_id": 9999995,
  "sum": 57000
}
```

### Success Response (200 OK)
```json
{
  "payment_id": 1810,
  "order_id": 9999995,
  "session_id": "9999995-20250930T180348Z",
  "status": "SUCCESS",
  "auth_code": "873793",
  "rrn": "000010001446",
  "transaction_id": "0",
  "terminal_id": "00092240",
  "merchant_id": "11111111",
  "response_code": "00",
  "response_message": "ОДОБРЕНО",
  "amount": 57000,
  "currency_code": "643",
  "payment_date": "2025-09-30T18:03:48.057043+00:00",
  "completed_at": "2025-09-30T18:04:07.401415+00:00",
  "receipt_available": true,
  "field_90_raw": "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?><response><field id=\"0\">57000</field><field id=\"4\">643</field><field id=\"6\">20250930180321</field><field id=\"13\">873793</field><field id=\"14\">000010001446</field><field id=\"15\">00</field><field id=\"19\">ОДОБРЕНО</field><field id=\"21\">20250930180321</field><field id=\"23\">0</field><field id=\"25\">1</field><field id=\"26\">0</field><field id=\"27\">00092240</field><field id=\"28\">11111111</field><field id=\"39\">00</field></response>",
  "customer_receipt": "<html><body>\n    <div style='font-family: monospace;'>\n    ===========================<br>\n    ТЕСТОВЫЙ ЧЕК<br>\n    ===========================<br>\n    Дата: 30.09.2025 18:04<br>\n    Терминал: 00092240<br>\n    ===========================<br>\n    ОПЛАТА ОДОБРЕНА<br>\n    ===========================<br>\n    </div></body></html>",
  "merchant_receipt": "<html><body>\n    <div style='font-family: monospace;'>\n    ===========================<br>\n    ТЕСТОВЫЙ ЧЕК<br>\n    ===========================<br>\n    Дата: 30.09.2025 18:04<br>\n    Терминал: 00092240<br>\n    ===========================<br>\n    ОПЛАТА ОДОБРЕНА<br>\n    ===========================<br>\n    </div></body></html>"
}
```

### Failure Response - Client Didn't Pay (200 OK)
```json
{
  "payment_id": 1809,
  "order_id": 9999995,
  "session_id": "9999995-20250930T180127Z",
  "status": "DECLINED",
  "auth_code": null,
  "rrn": null,
  "transaction_id": "0",
  "terminal_id": "00092240",
  "merchant_id": "0",
  "response_code": "ER3",
  "response_message": "ОПЕРАЦИЯ ПРЕРВАНА^TERMINATED.JPG~",
  "amount": 57000,
  "currency_code": "643",
  "payment_date": "2025-09-30T18:01:27.460992+00:00",
  "completed_at": "2025-09-30T18:01:58.686168+00:00",
  "receipt_available": false,
  "field_90_raw": "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?><response><field id=\"0\">57000</field><field id=\"4\">643</field><field id=\"6\">20250930180321</field><field id=\"15\">ER3</field><field id=\"19\">ОПЕРАЦИЯ ПРЕРВАНА^TERMINATED.JPG~</field><field id=\"21\">20250930180321</field><field id=\"23\">0</field><field id=\"25\">1</field><field id=\"26\">0</field><field id=\"27\">00092240</field><field id=\"28\">0</field><field id=\"39\">53</field></response>",
  "customer_receipt": null,
  "merchant_receipt": null
}
```

### Service Unavailable (503)
```json
{
  "detail": "Service Unavailable"
}
```

### Internal Server Error (500)
```json
{
  "detail": "Internal Server Error"
}
```

---

## 2. Fiscal Edge Mock

### Endpoint
```
POST /mocks/fiscal
```

### Request
```json
{
  "order_id": 9999996,
  "kiosk_id": "kiosk_001",
  "items": [
    {
      "item_id": 123,
      "item_description": "Cappuccino 250ml",
      "item_price_net": 30000,
      "item_price_gross": 36000,
      "item_vat_value": 6000,
      "quantity": 1
    },
    {
      "item_id": 124,
      "item_description": "Bagel with cream cheese",
      "item_price_net": 15000,
      "item_price_gross": 18000,
      "item_vat_value": 3000,
      "quantity": 2
    }
  ],
  "total_net": 60000,
  "total_vat": 12000,
  "total_gross": 72000,
  "payment_method": "CARD"
}
```

### Success Response (200 OK)
```json
{
  "status": "OK",
  "fiscal_receipt": {
    "ofd_reg_number": "1234567890",
    "fiscal_document_number": "FD-TEST-0001",
    "fn_number": "TEST-FN-0000000000000",
    "order_id": 9999996,
    "issued_at": "2025-09-30T18:05:30+00:00",
    "items": [
      {
        "item_id": 123,
        "description": "Cappuccino 250ml",
        "quantity": 1,
        "price_net": 30000,
        "vat": 6000,
        "price_gross": 36000
      },
      {
        "item_id": 124,
        "description": "Bagel with cream cheese",
        "quantity": 2,
        "price_net": 15000,
        "vat": 3000,
        "price_gross": 18000
      }
    ],
    "total_net": 60000,
    "total_vat": 12000,
    "total_gross": 72000,
    "message": "Fiscal receipt generated (test)"
  }
}
```

### Failure Response (200 OK)
```json
{
  "status": "NOT_OK",
  "error_code": "FISCAL_ERR_01",
  "error_message": "Fiscalization failed: OFD communication error (simulated)"
}
```

### Service Unavailable (503)
```json
{
  "detail": "Service Unavailable"
}
```

### Internal Server Error (500)
```json
{
  "detail": "Internal Server Error"
}
```

---

## 3. KDS (Kitchen Display System) Mock

### Endpoint
```
POST /mocks/kds
```

### Request
```json
{
  "order_id": 9999996,
  "kiosk_id": "kiosk_001",
  "items": [
    {
      "item_id": 123,
      "description": "Cappuccino 250ml",
      "quantity": 1
    },
    {
      "item_id": 124,
      "description": "Bagel",
      "quantity": 2
    },
    {
      "item_id": 125,
      "description": "Croissant",
      "quantity": 1
    }
  ]
}
```

### Success Response (200 OK)
```json
{
  "status": "OK",
  "kds_ticket_id": "KDS-TEST-0001",
  "received_at": "2025-09-30T18:06:00+00:00"
}
```

### Failure Response (200 OK)
```json
{
  "status": "NOT_OK",
  "error_code": "KDS_ERR_01",
  "error_message": "KDS reject: kitchen busy (simulated)"
}
```

### Service Unavailable (503)
```json
{
  "detail": "Service Unavailable"
}
```

### Internal Server Error (500)
```json
{
  "detail": "Internal Server Error"
}
```

---

## 4. Configuration API

### Get Current Configuration
```
GET /mocks/config
```

#### Response (200 OK)
```json
{
  "payment": {
    "mode": "AUTO_SUCCESS",
    "timeout_seconds": 30,
    "default_response": "SUCCESS",
    "sequence_config": null
  },
  "fiscal": {
    "mode": "MANUAL",
    "timeout_seconds": 45,
    "default_response": "OK",
    "sequence_config": null
  },
  "kds": {
    "mode": "SEQUENCE",
    "timeout_seconds": 30,
    "default_response": "OK",
    "sequence_config": {
      "success_count": 5,
      "failure_count": 2,
      "remaining": ["SUCCESS", "SUCCESS", "FAILURE", "SUCCESS", "FAILURE", "SUCCESS", "SUCCESS"]
    }
  }
}
```

### Update Configuration
```
POST /mocks/config
```

#### Request - Set All to Success
```json
{
  "payment": {
    "mode": "AUTO_SUCCESS",
    "timeout_seconds": 30,
    "default_response": "SUCCESS"
  },
  "fiscal": {
    "mode": "AUTO_SUCCESS",
    "timeout_seconds": 30,
    "default_response": "OK"
  },
  "kds": {
    "mode": "AUTO_SUCCESS",
    "timeout_seconds": 30,
    "default_response": "OK"
  }
}
```

#### Request - Set All to Failure
```json
{
  "payment": {
    "mode": "AUTO_FAILURE",
    "timeout_seconds": 30,
    "default_response": "FAILURE"
  },
  "fiscal": {
    "mode": "AUTO_FAILURE",
    "timeout_seconds": 30,
    "default_response": "NOT_OK"
  },
  "kds": {
    "mode": "AUTO_FAILURE",
    "timeout_seconds": 30,
    "default_response": "NOT_OK"
  }
}
```

#### Request - Set Payment to Sequence Mode
```json
{
  "payment": {
    "mode": "SEQUENCE",
    "timeout_seconds": 30,
    "default_response": "SUCCESS",
    "sequence_config": {
      "success_count": 7,
      "failure_count": 3
    }
  }
}
```

#### Request - Set Fiscal to Manual Mode
```json
{
  "fiscal": {
    "mode": "MANUAL",
    "timeout_seconds": 60,
    "default_response": "OK"
  }
}
```

#### Response (200 OK)
```json
{
  "status": "ok",
  "updated": ["payment", "fiscal"],
  "message": "Configuration updated for: payment, fiscal"
}
```

---

## 5. Logs API

### Get Recent Logs
```
GET /mocks/logs?limit=10
```

#### Response (200 OK)
```json
{
  "logs": [
    {
      "timestamp": "2025-09-30T18:06:00+00:00",
      "service": "payment",
      "request": {
        "kiosk_id": "kiosk_001",
        "order_id": 9999995,
        "sum": 57000
      },
      "response": {
        "payment_id": 1810,
        "status": "SUCCESS",
        "amount": 57000
      },
      "mode": "AUTO_SUCCESS",
      "status": "SUCCESS"
    },
    {
      "timestamp": "2025-09-30T18:07:15+00:00",
      "service": "fiscal",
      "request": {
        "order_id": 9999996,
        "kiosk_id": "kiosk_001",
        "total_gross": 72000
      },
      "response": {
        "status": "OK",
        "fiscal_document_number": "FD-TEST-0001"
      },
      "mode": "MANUAL",
      "status": "OK"
    },
    {
      "timestamp": "2025-09-30T18:08:30+00:00",
      "service": "kds",
      "request": {
        "order_id": 9999996,
        "kiosk_id": "kiosk_001"
      },
      "response": {
        "status": "NOT_OK",
        "error_code": "KDS_ERR_01"
      },
      "mode": "SEQUENCE",
      "status": "NOT_OK"
    }
  ]
}
```

---

## 6. Service Status Endpoints

### Payment Status
```
GET /mocks/payment/status
```

#### Response (200 OK)
```json
{
  "service": "payment",
  "mode": "AUTO_SUCCESS",
  "timeout_seconds": 30,
  "default_response": "SUCCESS"
}
```

### Fiscal Status
```
GET /mocks/fiscal/status
```

#### Response (200 OK)
```json
{
  "service": "fiscal",
  "mode": "MANUAL",
  "timeout_seconds": 45,
  "default_response": "OK"
}
```

### KDS Status
```
GET /mocks/kds/status
```

#### Response (200 OK)
```json
{
  "service": "kds",
  "mode": "SEQUENCE",
  "timeout_seconds": 30,
  "default_response": "OK"
}
```

---

## 7. Health Check

### Endpoint
```
GET /health
```

#### Response (200 OK)
```json
{
  "status": "ok"
}
```

---

## Operation Modes Summary

### AUTO_SUCCESS
- Всегда возвращает успешный ответ
- Используется для тестирования "happy path"

### AUTO_FAILURE
- Всегда возвращает неуспешный ответ
- Используется для тестирования обработки ошибок

### MANUAL
- Запрос отправляется админу в Telegram
- Админ выбирает ответ через inline кнопки:
  - ✅ Success
  - ❌ Failure
  - ⚠️ Service Unavailable (503)
- Если нет ответа в течение timeout - возвращается default_response

### SEQUENCE
- Последовательность успешных и неуспешных ответов
- Настраивается через `success_count` и `failure_count`
- Последовательность генерируется случайно и повторяется
- Пример: 5 успешных, 2 неуспешных = `[S,S,F,S,S,F,S,S,S,F,...]`

---

## Error Responses

### 422 Validation Error
Возвращается при неверном формате запроса.

```json
{
  "detail": [
    {
      "loc": ["body", "sum"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error
Возвращается при внутренней ошибке сервера.

```json
{
  "detail": "Internal Server Error"
}
```

### 503 Service Unavailable
Возвращается когда в MANUAL режиме админ выбирает "Service Unavailable".

```json
{
  "detail": "Service Unavailable"
}
```

---

## cURL Examples for Testing

### Test Payment Success
```bash
curl -X POST https://your-service.railway.app/mocks/payment \
  -H "Content-Type: application/json" \
  -d '{
    "kiosk_id": "kiosk_001",
    "order_id": 123456,
    "sum": 57000
  }'
```

### Test Fiscal Success
```bash
curl -X POST https://your-service.railway.app/mocks/fiscal \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": 123456,
    "kiosk_id": "kiosk_001",
    "items": [{
      "item_id": 1,
      "item_description": "Coffee",
      "item_price_net": 30000,
      "item_price_gross": 36000,
      "item_vat_value": 6000,
      "quantity": 1
    }],
    "total_net": 30000,
    "total_vat": 6000,
    "total_gross": 36000,
    "payment_method": "CARD"
  }'
```

### Test KDS Success
```bash
curl -X POST https://your-service.railway.app/mocks/kds \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": 123456,
    "kiosk_id": "kiosk_001",
    "items": [{
      "item_id": 1,
      "description": "Coffee",
      "quantity": 1
    }]
  }'
```

### Set All Services to Failure Mode
```bash
curl -X POST https://your-service.railway.app/mocks/config \
  -H "Content-Type: application/json" \
  -d '{
    "payment": {"mode": "AUTO_FAILURE"},
    "fiscal": {"mode": "AUTO_FAILURE"},
    "kds": {"mode": "AUTO_FAILURE"}
  }'
```

### Set Payment to Manual Mode
```bash
curl -X POST https://your-service.railway.app/mocks/config \
  -H "Content-Type: application/json" \
  -d '{
    "payment": {
      "mode": "MANUAL",
      "timeout_seconds": 60,
      "default_response": "SUCCESS"
    }
  }'
```

### Get Current Configuration
```bash
curl https://your-service.railway.app/mocks/config
```

### Get Recent Logs
```bash
curl https://your-service.railway.app/mocks/logs?limit=20
```

---

## Testing Scenarios for Kiosk

### Scenario 1: Happy Path (All Success)
1. Set all services to AUTO_SUCCESS mode
2. Test full order flow: payment → fiscal → kds
3. Verify all services return success

### Scenario 2: Payment Declined
1. Set payment to AUTO_FAILURE mode
2. Set fiscal and kds to AUTO_SUCCESS
3. Test order flow
4. Verify payment returns DECLINED status

### Scenario 3: Fiscal Error
1. Set payment to AUTO_SUCCESS mode
2. Set fiscal to AUTO_FAILURE mode
3. Set kds to AUTO_SUCCESS
4. Test order flow after successful payment
5. Verify fiscal returns NOT_OK with error code

### Scenario 4: KDS Unavailable
1. Set payment and fiscal to AUTO_SUCCESS
2. Set kds to MANUAL mode
3. Test order flow
4. Admin selects "Service Unavailable" in Telegram
5. Verify kiosk receives 503 error

### Scenario 5: Mixed Sequence
1. Set payment to SEQUENCE (7 success, 3 failure)
2. Set fiscal and kds to AUTO_SUCCESS
3. Run 10 orders sequentially
4. Verify approximately 70% success rate

### Scenario 6: Manual Approval Flow
1. Set all services to MANUAL mode
2. Set timeout to 60 seconds
3. Test order flow
4. Admin approves/declines via Telegram within timeout
5. Verify correct response received

### Scenario 7: Timeout Handling
1. Set payment to MANUAL mode with 10 second timeout
2. Set default_response to "FAILURE"
3. Test order flow
4. Don't respond in Telegram
5. Verify default response returned after timeout

---

## Notes

- Все суммы указываются в копейках (57000 = 570.00 руб)
- Временные метки в формате ISO 8601 с timezone
- Все ID (payment_id, fiscal_document_number, kds_ticket_id) генерируются последовательно
- Логи хранятся в памяти (максимум 1000 записей)
- При перезапуске сервиса все настройки сбрасываются к AUTO_SUCCESS

---

## Base URL

Production: `https://your-service.railway.app`

Swagger UI: `https://your-service.railway.app/docs`

ReDoc: `https://your-service.railway.app/redoc`
