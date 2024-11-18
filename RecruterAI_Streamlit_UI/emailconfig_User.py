import smtplib
from urllib.parse import quote
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailConfig_User:
    # Email account credentials
    EMAIL_ADDRESS = 'padmanabhanhydra@gmail.com'
    EMAIL_PASSWORD = 'qkdb gyjg waha xscw'
    
    @classmethod
    def send_email(cls, to_email, user_password):
        msg = MIMEMultipart()
        msg['From'] = cls.EMAIL_ADDRESS
        msg['To'] = to_email
        msg['Subject'] = 'Your HRrecruiterAI Login Credentials and Welcome Information'
    
        body = f"""
        Dear User,
    
        Welcome to the HRrecruiterAI app!

        We are excited to have you on board. Below are your login details
        
        ---------------------------------------------------
        Login Email: {to_email}
        ---------------------------------------------------
        You can access the HRrecruiterAI app by clicking on the following link: 

        We recommend that you log in and update your password immediately to ensure the security of your account. Should you encounter any issues or have any questions, please do not hesitate to contact our support team at support@hrrecruiterai.com.

        Best regards,
        The HRrecruiterAI Team

        ---
        Note: This is an automated email, please do not reply to this message.
        """
        msg.attach(MIMEText(body, 'plain'))
    
        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(cls.EMAIL_ADDRESS, cls.EMAIL_PASSWORD)
                server.sendmail(cls.EMAIL_ADDRESS, to_email, msg.as_string())
            print(f'Credentials sent successfully to {to_email}')
        except Exception as e:
            print(f'Failed to send email. Error: {e}')




    @classmethod
    def send_email_candidate(cls, candidate_email, candidate_name, job_id):
        msg = MIMEMultipart()
        msg['From'] = cls.EMAIL_ADDRESS
        msg['To'] = candidate_email
        msg['Subject'] = 'Interview Schedule for HRrecruiterAI Position'
        
        yes_url = f"http://localhost:8083/api/v1/response/{job_id}/{candidate_email}?response=yes"
        no_url = f"http://localhost:8083/api/v1/response/{job_id}/{candidate_email}?response=no"

        body = f"""
        <html>
        <body>
        <p>Dear {candidate_name},</p>
        <p>Congratulations! You have been shortlisted for the interview process at [Company Name].</p>
        <p>We are excited about your qualifications for the [Job Title] position. Please review the details of the interview process below:</p>

        <p><b>Interview Details:</b></p>
        <ul>
            <li>Location: [Physical Address or Virtual Meeting Link]</li>
            <li>Duration: [Interview Duration, e.g., 1 hour]</li>
        </ul>

        <p><b>Interview Agenda:</b></p>
        <ul>
            <li>Introduction</li>
            <li>Skills and Technical Assessment</li>
            <li>Behavioral Questions</li>
            <li>Q&A Session</li>
            <li>Conclusion</li>
        </ul>
        
        <p>We would like to know if you are interested in attending the interview.</p>
        
        <p>Are you available for the interview?</p>
        <p>
            <a href="{yes_url}" style="padding:10px 20px; background-color:green; color:white; text-decoration:none;">Yes, I'm interested</a>
            <a href="{no_url}" style="padding:10px 20px; background-color:red; color:white; text-decoration:none;">No, I'm not interested</a>
        </p>
        
        <p>If you have any questions or need further clarification, feel free to reach out to our HR team.</p>

        <p>Thank you for considering this opportunity.</p>
        
        <p>Best Regards,<br>HRrecruiterAI System<br>[Company Name]</p>
        </body>
        </html>
        """

        msg.attach(MIMEText(body, 'html'))

        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(cls.EMAIL_ADDRESS, cls.EMAIL_PASSWORD)
                server.sendmail(cls.EMAIL_ADDRESS, candidate_email, msg.as_string())
            print(f'Interview schedule email sent successfully to {candidate_email}')
        except Exception as e:
            print(f'Failed to send email. Error: {e}')




    @classmethod
    def send_email_Member(cls, to_email):
        msg = MIMEMultipart()
        msg['From'] = cls.EMAIL_ADDRESS
        msg['To'] = to_email
        msg['Subject'] = 'Your HRrecruiterAI Login Credentials and Welcome Information'
    
        body = f"""
        Dear Member,
    
        Welcome to the HRrecruiterAI app!

        We are excited to have you on board. Below are your login details
        
        ---------------------------------------------------
        Login Email: {to_email}
        ---------------------------------------------------
        You can access the HRrecruiterAI app by clicking on the following link: 

        We recommend that you log in and update your password immediately to ensure the security of your account. Should you encounter any issues or have any questions, please do not hesitate to contact our support team at support@hrrecruiterai.com.

        Best regards,
        The HRrecruiterAI Team

        ---
        Note: This is an automated email, please do not reply to this message.
        """
        msg.attach(MIMEText(body, 'plain'))
    
        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(cls.EMAIL_ADDRESS, cls.EMAIL_PASSWORD)
                server.sendmail(cls.EMAIL_ADDRESS, to_email, msg.as_string())
            print(f'Credentials sent successfully to {to_email}')
        except Exception as e:
            print(f'Failed to send email. Error: {e}')

    @classmethod
    def send_email_SchdeulePanel(cls, to_email, job_id, interview_date, interview_time, panel_members_data):
        msg = MIMEMultipart()
        msg['From'] = cls.EMAIL_ADDRESS
        msg['To'] = to_email
        msg['Subject'] = 'Interview Scheduled for [Job Title] Position'

        yes_url = f"http://localhost:8083/api/v1/response/{job_id}/{to_email}?response=yes"
        no_url = f"http://localhost:8083/api/v1/response/{job_id}/{to_email}?response=no"
        
        body = f"""
        <html>
        <body>
        <p>Dear {panel_members_data},</p>
        <p>This is an automated notification from the HRrecruiterAI system.</p>
        <p>You have been selected as a panel member for the interview process for the [Job Title] position. Below are the interview details:</p>

        <p><b>Interview Details:</b></p>
        <ul>
            <li>Date: {interview_date}</li>
            <li>Time: {interview_time}</li>
            <li>Location: [Physical Address or Virtual Meeting Link]</li>
            <li>Duration: [Interview Duration, e.g., 1 hour]</li>
        </ul>

        <p><b>Panel Members:</b></p>
        
        <p><b>Interview Agenda:</b></p>
        <ul>
            <li>Introduction</li>
            <li>Skills and Technical Assessment</li>
            <li>Behavioral Questions</li>
            <li>Q&A Session</li>
            <li>Conclusion</li>
        </ul>

        <p>Please ensure your availability for the interview. If you have any questions or need to make adjustments to the schedule, kindly reach out to the HR team.</p>
        
        <p>We appreciate your participation in this interview process.</p>
        
        <p>Best Regards,<br>HRrecruiterAI System<br>[Company Name]</p>
        </body>
        </html>
        """

        msg.attach(MIMEText(body, 'html'))
        
    
        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(cls.EMAIL_ADDRESS, cls.EMAIL_PASSWORD)
                server.sendmail(cls.EMAIL_ADDRESS, to_email, msg.as_string())
            print(f'Interview schedule sent successfully {to_email}')
        except Exception as e:
            print(f'Failed to send email. Error: {e}')
 

if __name__ == '__main__':
    client = EmailConfig_User()
    client.send_email('', '')
    client.send_email_candidate('')
    client.send_email_Member('')
    client.send_email_SchdeulePanel('')