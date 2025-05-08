import os
import subprocess
import sys
import time
import signal
import platform

# Store all processes to terminate them later
processes = []

def start_service(command, cwd=None):
    """Start a service with the given command and working directory"""
    if platform.system() == 'Windows':
        process = subprocess.Popen(command, cwd=cwd, creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        process = subprocess.Popen(command, cwd=cwd, shell=True)
    processes.append(process)
    return process

def stop_all_services():
    """Stop all running services"""
    for process in processes:
        try:
            if platform.system() == 'Windows':
                process.kill()
            else:
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        except:
            pass
    print("\nAll services stopped.")

def main():
    # Get the base directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    try:
        print("Starting HR Recruiter AI Services...\n")
        
        # Start User Management API
        print("Starting User Management API (Port 8084)...")
        user_mgmt_dir = os.path.join(base_dir, "UserManagement_RestAPI")
        start_service(["uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8084", "--reload"], user_mgmt_dir)
        
        # Start Job Description API
        print("\nStarting Job Description API (Port 8081)...")
        job_desc_dir = os.path.join(base_dir, "JobDescription_RestAPI")
        start_service(["uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8081", "--reload"], job_desc_dir)
        
        # Start Resources API
        print("\nStarting Resources API (Port 8085)...")
        resources_dir = os.path.join(base_dir, "Resources_RestAPI")
        start_service(["uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8085", "--reload"], resources_dir)
        
        # Start WhatsApp Bot
        print("\nStarting WhatsApp Bot (Port 5000)...")
        whatsapp_dir = os.path.join(base_dir, "HR_Recuiter_Whatsapp_Chatbot")
        start_service(["python", "main.py", "5000"], whatsapp_dir)
        
        # Start ngrok tunnel
        print("\nStarting ngrok tunnel for WhatsApp Bot...")
        start_service(["ngrok", "http", "http://localhost:5000"])
        
        # Start Streamlit UI
        print("\nStarting Streamlit UI...")
        streamlit_dir = os.path.join(base_dir, "RecruterAI_Streamlit_UI")
        start_service(["streamlit", "run", "app.py"], streamlit_dir)
        
        print("\nAll services started successfully!")
        print("\nService Information:")
        print("- User Management API: http://127.0.0.1:8084")
        print("- Job Description API: http://127.0.0.1:8081")
        print("- Resources API: http://127.0.0.1:8085")
        print("- WhatsApp Bot: http://127.0.0.1:5000")
        print("- Streamlit UI: Should open automatically in your browser")
        print("- ngrok: Check the ngrok window for the public URL")
        
        print("\nPress Ctrl+C to stop all services...")
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping all services...")
        stop_all_services()
    except Exception as e:
        print(f"\nError: {e}")
        stop_all_services()

if __name__ == "__main__":
    main()