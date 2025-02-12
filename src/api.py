import httpx

from config import settings

async def send_verify_code(phone_number, code, whatsapp_business_phone_number_id, whatsapp_api_token, language="en_US"):
    async with httpx.AsyncClient() as client:
        response = await client.post(
        f"{settings.whatsapp_api_url}/{settings.whatsapp_api_version}/{whatsapp_business_phone_number_id}/messages",
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
                                        "text": code
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
                                        "text": code
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