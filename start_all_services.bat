@echo off
echo Starting HR Recruiter AI Services...

echo.
echo Starting User Management API (Port 8083)...
start cmd /k "cd %~dp0UserManagement_RestAPI && uvicorn main:app --host 127.0.0.1 --port 8083 --reload"

echo.
echo Starting Job Description API (Port 8081)...
start cmd /k "cd %~dp0JobDescription_RestAPI && uvicorn main:app --host 127.0.0.1 --port 8081 --reload"

echo.
echo Starting Resources API (Port 8085)...
start cmd /k "cd %~dp0Resources_RestAPI && uvicorn main:app --host 127.0.0.1 --port 8085 --reload"

echo.
echo Starting WhatsApp Bot (Port 5000)...
start cmd /k "cd %~dp0HR_Recuiter_Whatsapp_Chatbot && python main.py 5000"

echo.
echo Starting ngrok tunnel for WhatsApp Bot...
start cmd /k "ngrok http http://localhost:5000"

echo.
echo Starting Streamlit UI...
start cmd /k "cd %~dp0RecruterAI_Streamlit_UI && streamlit run app.py"

echo.
echo All services started successfully!
echo.
echo Service Information:
echo - User Management API: http://127.0.0.1:8083
echo - Job Description API: http://127.0.0.1:8081
echo - Resources API: http://127.0.0.1:8085
echo - WhatsApp Bot: http://127.0.0.1:5000
echo - Streamlit UI: Should open automatically in your browser
echo - ngrok: Check the ngrok window for the public URL

echo.
echo Press any key to stop all services...
pause > nul

taskkill /F /FI "WINDOWTITLE eq *uvicorn*" /T
taskkill /F /FI "WINDOWTITLE eq *python*" /T
taskkill /F /FI "WINDOWTITLE eq *ngrok*" /T
taskkill /F /FI "WINDOWTITLE eq *streamlit*" /T

echo All services stopped.
pause