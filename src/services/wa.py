import httpx

from src.config import settings

async def send_whatsapp_template(phone_number, otp_code, phone_number_id, whatsapp_api_token, language="en_US"):
    async with httpx.AsyncClient() as client:
        response = await client.post(
        f"{settings.whatsapp_api_url}/{settings.whatsapp_api_version}/{phone_number_id}/messages",
            json={
                { 
                    "messaging_product": "whatsapp", 
                    "to": phone_number, 
                    "type": "template", 
                    "template": { 
                        "name": "verify_template", 
                        "language": { "code": language },
                        "components": [
                            {
                                "type": "body", 
                                "parameters": [
                                    {
                                        "type": "text",
                                        "text": otp_code
                                    }
                                ]
                            },
                            {
                                "type": "button",
                                "sub_type": "url",
                                "index": 0,
                                "parameters": [
                                    {
                                        "type": "text",
                                        "text": otp_code
                                    }
                                ]
                            }
                            
                        ]
                    }
                }

            },
            headers={
                "Content-Type: application/json"
                f"Authorization: Bearer {whatsapp_api_token}",
            }
        )
        return response.json()