# HR Recruiter AI - Service Launcher

This document explains how to start all HR Recruiter AI services with a single command.

## Available Launchers

Two launcher scripts have been created to help you start all services at once:

1. **Batch Script** (Windows): `start_all_services.bat`
2. **Python Script** (Cross-platform): `start_all_services.py`

## Services Started

Both scripts will start the following services:

- **User Management API**: Running on port 8083
- **Job Description API**: Running on port 8081
- **Resources API**: Running on port 8085
- **WhatsApp Bot**: Running on port 5000
- **ngrok tunnel**: For WhatsApp webhook (check ngrok window for public URL)
- **Streamlit UI**: Will open automatically in your browser

## How to Use

### Using the Batch Script (Windows)

1. Open Command Prompt or Windows Explorer
2. Navigate to the HR Recruiter AI project folder
3. Double-click on `start_all_services.bat` or run it from Command Prompt
4. Multiple command windows will open, one for each service
5. To stop all services, press any key in the main batch script window

### Using the Python Script (Cross-platform)

1. Open Command Prompt/Terminal
2. Navigate to the HR Recruiter AI project folder
3. Run: `python start_all_services.py`
4. Multiple windows will open (on Windows) or processes will start (on Linux/Mac)
5. To stop all services, press Ctrl+C in the terminal where you started the Python script

## Requirements

- Make sure all required dependencies are installed for each component
- ngrok must be installed and available in your PATH
- Python must be installed and available in your PATH

## Troubleshooting

If any service fails to start:

1. Check the error message in the respective command window
2. Verify that all dependencies are installed
3. Ensure the required ports (8083, 8081, 8085, 5000) are not in use by other applications
4. Check that MongoDB is running (required for WhatsApp bot)

## Manual Startup (Alternative)

If you prefer to start services manually, use these commands in separate terminals:

```
# User Management API
cd UserManagement_RestAPI
uvicorn main:app --host 127.0.0.1 --port 8083 --reload

# Job Description API
cd JobDescription_RestAPI
uvicorn main:app --host 127.0.0.1 --port 8081 --reload

# Resources API
cd Resources_RestAPI
uvicorn main:app --host 127.0.0.1 --port 8085 --reload

# WhatsApp Bot
cd HR_Recuiter_Whatsapp_Chatbot
python main.py 5000

# ngrok tunnel for WhatsApp
ngrok http http://localhost:5000

# Streamlit UI
cd RecruterAI_Streamlit_UI
streamlit run app.py
```