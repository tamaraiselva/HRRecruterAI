import os
import requests
import json
from dotenv import load_dotenv
import numpy as np
import pandas as pd

load_dotenv()

class WhatsAppWrapper:

    API_URL = "https://graph.facebook.com/v19.0/"

    def __init__(self, api_token, cloud_number_id):
        self.WHATSAPP_API_TOKEN = api_token
        self.WHATSAPP_CLOUD_NUMBER_ID = cloud_number_id
        if self.WHATSAPP_CLOUD_NUMBER_ID is None:
            raise ValueError("WhatsApp Cloud Number ID is not set in environment variables.")
        self.headers = {
            "Authorization": f"Bearer {self.WHATSAPP_API_TOKEN}",
            "Content-Type": "application/json",
        }
        self.API_URL = self.API_URL + self.WHATSAPP_CLOUD_NUMBER_ID

    def convert_int64_to_int(self, data):
        if isinstance(data, dict):
            return {key: self.convert_int64_to_int(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self.convert_int64_to_int(element) for element in data]
        elif isinstance(data, (np.int64, pd.Int64Dtype().type)):
            return int(data)
        else:
            return data

    def send_template_message(self, template_name, language_code, phone_number):
        phone_number = f"91{int(phone_number)}"  # Add country code and ensure phone number is a standard Python integer
        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": language_code
                }
            }
        }

        # Convert payload to ensure no int64 types
        payload = self.convert_int64_to_int(payload)
        url = f"{self.API_URL}/messages"
        print(url)
        response = requests.post(url, json=payload, headers=self.headers)
        assert response.status_code == 200, f"Error sending message: {response.text}"
        return response.status_code

if __name__ == "__main__":
    client = WhatsAppWrapper()
    client.send_template_message("hr_recruter_ai", "en_US", "")
