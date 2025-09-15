# Webhook Email API Documentation

## Overview

The backend now includes a new email API endpoint that forwards email requests to your external webhook service. This provides a seamless integration between your backend and the webhook email service.

## API Endpoint

### Send Email via Webhook

**Endpoint:** `POST /api/email/send-webhook-email`

**Description:** Sends an email by forwarding the request to the external webhook service and returns the webhook's response.

**Request Body:**
```json
{
    "to_email": "pittisunilkumar3@gmail.com",
    "subject": "Test Email from Backend API",
    "message": "This is a test email sent via the backend API",
    "html_message": "<p>This is a <strong>test email</strong> sent via the backend API</p>"
}
```

**Response (Success - 200 OK):**
```json
[
    {
        "accepted": [
            "pittisunilkumar3@gmail.com"
        ],
        "rejected": [],
        "ehlo": [
            "SIZE 202428800",
            "LIMITS MAILMAX=1000 RCPTMAX=10",
            "8BITMIME",
            "PIPELINING",
            "PIPECONNECT",
            "AUTH PLAIN LOGIN",
            "HELP"
        ],
        "envelopeTime": 648,
        "messageTime": 420,
        "messageSize": 733,
        "response": "250 OK id=1ux2q3-0000000Et3v-02st",
        "envelope": {
            "from": "info@sveats.cyberdetox.in",
            "to": [
                "pittisunilkumar3@gmail.com"
            ]
        },
        "messageId": "<6e1248fb-80b6-b9df-0ac2-e186f3a17834@sveats.cyberdetox.in>"
    }
]
```

## Request Schema

### WebhookEmailRequest

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `to_email` | EmailStr | Yes | Recipient's email address |
| `subject` | string | Yes | Email subject (min: 1 char) |
| `message` | string | Yes | Plain text email content (min: 1 char) |
| `html_message` | string | Yes | HTML formatted email content (min: 1 char) |

## Response Schema

### WebhookEmailResponse

| Field | Type | Description |
|-------|------|-------------|
| `accepted` | List[string] | List of accepted email addresses |
| `rejected` | List[string] | List of rejected email addresses |
| `ehlo` | List[string] | EHLO response from SMTP server |
| `envelopeTime` | integer | Time taken for envelope processing (ms) |
| `messageTime` | integer | Time taken for message processing (ms) |
| `messageSize` | integer | Message size in bytes |
| `response` | string | SMTP server response |
| `envelope` | EmailEnvelope | Email envelope information |
| `messageId` | string | Unique message identifier |

### EmailEnvelope

| Field | Type | Description |
|-------|------|-------------|
| `from` | string | Sender email address |
| `to` | List[string] | Recipient email addresses |

## Error Responses

### 400 Bad Request
```json
{
    "detail": "Validation error message"
}
```

### 502 Bad Gateway
```json
{
    "detail": "Webhook service failed: 500 - Internal Server Error"
}
```

### 504 Gateway Timeout
```json
{
    "detail": "Webhook service timed out"
}
```

### 500 Internal Server Error
```json
{
    "detail": "Failed to send email via webhook: error details"
}
```

## Usage Examples

### cURL Example
```bash
curl -X POST "http://82.29.165.77:8003/api/email/send-webhook-email" \
     -H "Content-Type: application/json" \
     -d '{
       "to_email": "pittisunilkumar3@gmail.com",
       "subject": "Test Email",
       "message": "This is a test email",
       "html_message": "<p>This is a <strong>test email</strong></p>"
     }'
```

### Python Example
```python
import requests

url = "http://82.29.165.77:8003/api/email/send-webhook-email"
payload = {
    "to_email": "pittisunilkumar3@gmail.com",
    "subject": "Test Email",
    "message": "This is a test email",
    "html_message": "<p>This is a <strong>test email</strong></p>"
}

response = requests.post(url, json=payload)
if response.status_code == 200:
    result = response.json()
    print(f"Email sent! Message ID: {result[0]['messageId']}")
else:
    print(f"Failed: {response.status_code} - {response.text}")
```

### JavaScript/Frontend Example
```javascript
const response = await fetch('http://82.29.165.77:8003/api/email/send-webhook-email', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    to_email: 'pittisunilkumar3@gmail.com',
    subject: 'Test Email',
    message: 'This is a test email',
    html_message: '<p>This is a <strong>test email</strong></p>'
  })
});

if (response.ok) {
  const result = await response.json();
  console.log('Email sent!', result[0].messageId);
} else {
  console.error('Failed to send email:', response.status);
}
```

## Implementation Details

- **Webhook URL:** `https://ai.alviongs.com/webhook/de77d8d6-ae98-471d-ba19-8d7f58ec8449`
- **Timeout:** 30 seconds
- **HTTP Client:** httpx (async)
- **Logging:** Comprehensive logging for debugging
- **Error Handling:** Proper HTTP status codes and error messages

## Features

✅ **Exact Response Format:** Returns the same response format as the direct webhook  
✅ **Error Handling:** Comprehensive error handling with proper HTTP status codes  
✅ **Logging:** Detailed logging for monitoring and debugging  
✅ **Timeout Protection:** 30-second timeout to prevent hanging requests  
✅ **Validation:** Input validation using Pydantic models  
✅ **Documentation:** Auto-generated OpenAPI/Swagger documentation  

## Testing

Use the provided test script to verify the endpoint:

```bash
python test-backend-webhook-email.py
```

## Next Steps

1. **Restart Backend Server:** The server needs to be restarted to pick up the new route
2. **Test the Endpoint:** Use the test script to verify functionality
3. **Update Frontend:** Update frontend code to use the backend API instead of direct webhook calls
4. **Monitor Logs:** Check backend logs for any issues

## Security Considerations

- The webhook URL is hardcoded in the backend for security
- Input validation prevents malicious payloads
- Proper error handling prevents information leakage
- Timeout protection prevents resource exhaustion
