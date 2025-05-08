#!/bin/bash

# HR Recruiter AI Service Launcher (Linux/Mac version)
echo "Starting HR Recruiter AI Services..."
echo ""

# Function to clean up processes when script is terminated
cleanup() {
    echo "\nStopping all services..."
    pkill -f "uvicorn main:app --host 127.0.0.1 --port 8083"
    pkill -f "uvicorn main:app --host 127.0.0.1 --port 8081"
    pkill -f "uvicorn main:app --host 127.0.0.1 --port 8085"
    pkill -f "python main.py 5000"
    pkill -f "ngrok http http://localhost:5000"
    pkill -f "streamlit run app.py"
    echo "All services stopped."
    exit 0
}

# Set up trap to catch SIGINT (Ctrl+C) and SIGTERM
trap cleanup SIGINT SIGTERM

# Start User Management API
echo "Starting User Management API (Port 8083)..."
cd "$(dirname "$0")/UserManagement_RestAPI" && \
uvicorn main:app --host 127.0.0.1 --port 8083 --reload > /dev/null 2>&1 &

# Start Job Description API
echo "\nStarting Job Description API (Port 8081)..."
cd "$(dirname "$0")/JobDescription_RestAPI" && \
uvicorn main:app --host 127.0.0.1 --port 8081 --reload > /dev/null 2>&1 &

# Start Resources API
echo "\nStarting Resources API (Port 8085)..."
cd "$(dirname "$0")/Resources_RestAPI" && \
uvicorn main:app --host 127.0.0.1 --port 8085 --reload > /dev/null 2>&1 &

# Start WhatsApp Bot
echo "\nStarting WhatsApp Bot (Port 5000)..."
cd "$(dirname "$0")/HR_Recuiter_Whatsapp_Chatbot" && \
python main.py 5000 > /dev/null 2>&1 &

# Start ngrok tunnel
echo "\nStarting ngrok tunnel for WhatsApp Bot..."
ngrok http http://localhost:5000 > /dev/null 2>&1 &

# Start Streamlit UI
echo "\nStarting Streamlit UI..."
cd "$(dirname "$0")/RecruterAI_Streamlit_UI" && \
streamlit run app.py > /dev/null 2>&1 &

echo "\nAll services started successfully!"
echo "\nService Information:"
echo "- User Management API: http://127.0.0.1:8083"
echo "- Job Description API: http://127.0.0.1:8081"
echo "- Resources API: http://127.0.0.1:8085"
echo "- WhatsApp Bot: http://127.0.0.1:5000"
echo "- Streamlit UI: Should open automatically in your browser"
echo "- ngrok: Run 'ps aux | grep ngrok' to find the ngrok process and check its logs"

echo "\nPress Ctrl+C to stop all services..."

# Keep script running until user presses Ctrl+C
while true; do
    sleep 1
done