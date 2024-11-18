import os
from flask import Flask, request, jsonify
from whatsapp_client import WhatsAppWrapper
from whatsapp_bot import ChatBot
import requests
import re
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

mongo_client = MongoClient('mongodb://localhost:27017/')  # Replace with your MongoDB connection string
db = mongo_client['chat_database']
chats_collection = db['chats']

# Define your verify token here
VERIFY_TOKEN = "hrrecruiter"  # Replace with your own verify token

# Extract answer function
def extract_answer(text):
    pattern = re.compile(r"Answer:\s*(.*)", re.DOTALL)
    match = pattern.search(text)
    if match:
        answer = match.group(1).strip()
        # Remove any additional context or instructions from the answer
        end_pattern = r"(Question:|Context:|Answer:)"
        clean_answer = re.split(end_pattern, answer)[0].strip()
        return clean_answer
    return "Answer not found."

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    # Verification logic
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge"), 200
    return "Verification token mismatch", 403

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    # Process the incoming message here
    process_incoming_message(data)
    return jsonify({"status": "success"}), 200

@app.route('/', methods=['GET'])
def listening():
    return jsonify({"status": "listening"}), 200

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    template_name = data.get('template_name')
    language_code = data.get('language_code')
    phone_number = data.get('phone_number')
    api_token = data.get('api_token')
    cloud_number_id = data.get('cloud_number_id')
    selected_job_id = data.get('selected_job_id')

    print(selected_job_id)

    # Ensure the environment variables are set as strings
    os.environ["SELECTED_JOB_ID"] = str(selected_job_id)
    os.environ["WHATSAPP_API_TOKEN"] = str(api_token)
    os.environ["WHATSAPP_CLOUD_NUMBER_ID"] = str(cloud_number_id)
    
    if not template_name or not language_code or not phone_number:
        return jsonify({"error": "Missing required fields"}), 400

    try:
        whatsapp_client = WhatsAppWrapper(api_token,cloud_number_id)
        status_code = whatsapp_client.send_template_message(template_name, language_code, phone_number)
        return jsonify({"status": "success", "code": status_code}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

processed_message_ids = set()

def process_incoming_message(data):
    entry = data.get("entry", [])
    
    for entry_item in entry:
        changes = entry_item.get("changes", [])
        for change in changes:
            value = change.get("value", {})
            messages = value.get("messages", [])
            
            if messages:
                for message in messages:
                    message_id = message.get("id")
                    if message_id in processed_message_ids:
                        continue  # Skip already processed messages
                    
                    processed_message_ids.add(message_id)
                    chatbot = ChatBot()
                    if message.get("type") == "text":
                        text = message.get("text", {}).get("body")
                        if text:
                            response = chatbot.rag_chain.invoke(text)
                            answer = extract_answer(response)
                            save_chat_history(value.get("contacts", [{}])[0].get("wa_id"), text, answer)
                            send_whatsapp_message(value, answer)
                    elif message.get("type") == "button":
                        button_text = message.get("button", {}).get("text")
                        if button_text:
                            response = chatbot.rag_chain.invoke(button_text)
                            answer = extract_answer(response)
                            save_chat_history(value.get("contacts", [{}])[0].get("wa_id"), button_text, answer)
                            send_whatsapp_message(value, answer)

def send_whatsapp_message(value, answer):
    phone_number = value.get("contacts", [{}])[0].get("wa_id")  # Adjust if necessary based on your webhook structure
    api_token = os.getenv("WHATSAPP_API_TOKEN")
    cloud_number_id = os.getenv("WHATSAPP_CLOUD_NUMBER_ID")
    
    if not phone_number or not api_token or not cloud_number_id:
        print("Missing required fields to send message.")
        return
    
    try:
        whatsapp_client = WhatsAppWrapper(api_token, cloud_number_id)
        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "text": {
                "body": answer
            }
        }
        response = requests.post(f"{whatsapp_client.API_URL}/messages", json=payload, headers=whatsapp_client.headers)
        print(f"Response Body: {response.text}")
    except Exception as e:
        print(f"Error sending message: {str(e)}")

def save_chat_history(phone_number, user_message, bot_response):
    current_date = datetime.now().strftime('%Y-%m-%d')
    chat_id = f"chat_{phone_number}"

    chat = chats_collection.find_one({"chat_id": chat_id})
    
    if chat:
        # Chat history exists, update the history for the current date
        if current_date in chat['history']:
            chat['history'][current_date].append({"user": user_message, "bot": bot_response})
        else:
            chat['history'][current_date] = [{"user": user_message, "bot": bot_response}]
        chats_collection.update_one({"chat_id": chat_id}, {"$set": {"history": chat['history']}})
    else:
        # Chat history doesn't exist, create a new record
        new_chat = {
            "chat_id": chat_id,
            "phone_number": phone_number,
            "history": {
                current_date: [{"user": user_message, "bot": bot_response}]
            }
        }
        chats_collection.insert_one(new_chat)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
