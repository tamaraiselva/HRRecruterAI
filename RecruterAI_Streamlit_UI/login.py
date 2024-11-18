import streamlit as st
import requests
import re
import time

def get_login_fields():
    return [
        {"name": "email", "type": "string"},
        {"name": "password", "type": "string"}
    ]

def get_signup_fields():
    return [
        {"name": "name", "type": "string"},
        {"name": "email", "type": "string"},
        {"name": "mobile_number", "type": "string"},
        {"name": "location", "type": "string"},
        {"name": "password", "type": "string"}
    ]

def validate_name(name):
    # Name should start with a capital letter and be up to 15 characters long
    return re.match(r"^[A-Z][a-zA-Z]{0,14}$", name)

def validate_email(email):
    return re.match(r"^[\w\.\+\-]+@[A-Za-z0-9\-]+\.[A-Za-z]{2,}$", email)

def validate_password(password):
    return (len(password) >= 8 and 
            any(char.isupper() for char in password) and 
            any(char.islower() for char in password) and 
            any(char.isdigit() for char in password))

def validate_mobile_number(mobile_number):
    return re.match(r"^\d{10}$", mobile_number)

def login(payload):
    url = 'http://localhost:8083/api/v1/login'  
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        user_data = response.json()
        user_id = user_data.get('user_id')
        user_role = user_data.get('user_role') 
        if user_id is not None:
            st.session_state['user_id'] = user_id  # Store the user ID in session state
            st.session_state['user_role'] = user_role
            return True, user_data
        else:
            return False, "User ID not found in response"
    elif response.status_code == 404:
        return False, "User not found, please signup before login"
    else:
        return False, "Invalid Username or Password"

def signup(payload):
    url = 'http://localhost:8083/api/v1/user'
    response = requests.post(url, json=payload)
    if response.status_code == 201:  # 201 is used for resource creation
        return True, response.json()
    elif response.status_code == 422:
        return False,"User already exist"
    else:
        return False, response.text

def fetch_user_data(user_id=None):
    url = 'http://localhost:8083/api/v1/users'
    if user_id:
        url += f'/{user_id}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def reset_password(email, new_password):
    url = f'http://localhost:8083/api/v1/password_reset/{email}'
    response = requests.put(url, json={"new_password": new_password})
    if response.status_code == 200:
        return True, "Password Reseted Successfully"
    elif response.status_code == 404:
        return False, "User with the given email not found"
    else:
        return False, "Failed to Reset Password" 

def show_login_page():
    st.subheader("Login Page")

    if st.session_state.success:
        st.success(st.session_state.message)
        st.session_state.message = ""
        st.session_state.success = False

    fields = get_login_fields()
    inputs = st.session_state.login_inputs

    for field in fields:
        if field['type'] == 'string':
            if field['name'] == 'password':
                inputs[field['name']] = st.text_input(
                    field['name'].replace('_', ' ').capitalize(), 
                    type="password", 
                    value=inputs.get(field['name'], ""), 
                    autocomplete="new-password",
                    key="login_password"
                )
            else:
                inputs[field['name']] = st.text_input(
                    field['name'].replace('_', ' ').capitalize(), 
                    value=inputs.get(field['name'], ""), 
                    autocomplete="off",
                    key="login_email"
                )

    if st.button("Login"):
        empty_fields = [field['name'] for field in fields if not inputs.get(field['name'])]
        if empty_fields:
            st.session_state.message = "Please fill in all fields"
            st.rerun()
        else:
            payload = {field['name']: inputs[field['name']] for field in fields}
            success, message = login(payload)

            if success:
                st.session_state.message = "Login successful!"
                st.session_state.login_state = True
                st.session_state.login_inputs = {"email": "", "password": ""}  # Clear login inputs on success
                st.rerun()
            elif not success:
                st.session_state.message = message  # Set the message from the login function
                st.session_state.login_state = False
                st.rerun()
            else:
                st.session_state.message = "Login failed. Please check your username and password"
                st.rerun()

    if st.session_state.message:
        st.error(st.session_state.message)

    if st.button("Sign Up"):
        st.session_state.page = "signup"
        st.session_state.message = ""  # Clear any previous messages
        st.session_state.login_inputs = {"email": "", "password": ""}  # Clear inputs when switching to signup mode
        st.rerun()

    if st.button("Forgot Password?"):
        st.session_state.page = "forgot_password"
        st.session_state.message = ""  # Clear any previous messages
        st.session_state.login_inputs = {"email": "", "password": ""}  # Clear inputs when switching to forgot password mode
        st.rerun()

def show_signup_page():
    st.subheader("Signup Page")

    fields = get_signup_fields()
    inputs = st.session_state.signup_inputs

    for field in fields:
        if field['type'] == 'string':
            if field['name'] == 'password':
                inputs[field['name']] = st.text_input(
                    field['name'].replace('_', ' ').capitalize(), 
                    type="password", 
                    value=inputs.get(field['name'], ""), 
                    autocomplete="new-password",
                    key="signup_password"
                )
            else:
                inputs[field['name']] = st.text_input(
                    field['name'].replace('_', ' ').capitalize(), 
                    value=inputs.get(field['name'], ""), 
                    autocomplete="off",
                    key=field['name']
                )

    if st.button("Signup"):
        empty_fields = [field['name'] for field in fields if not inputs.get(field['name'])]
        if empty_fields:
            st.session_state.message = "Please fill in all fields."
        elif len(inputs['name']) > 15:
            st.session_state.message = "Name should be up to 15 characters."
        elif not validate_name(inputs['name']):
            st.session_state.message = "Name must start with a capital letter."
        elif not validate_email(inputs['email']):
            st.session_state.message = "Invalid email format."
        elif not validate_password(inputs['password']):
            st.session_state.message = "Password must be at least 8 characters long and include  uppercase, lowercase,special character and a number."
        elif not validate_mobile_number(inputs['mobile_number']):
            st.session_state.message = "Mobile number must be exactly 10 digits."
        else:
            payload = {field['name']: inputs[field['name']] for field in fields}
            success, message = signup(payload)

            if success:
                st.session_state.message = "Signup successful! You can now log in."
                st.session_state.page = "login"
                st.session_state.success = True
                st.session_state.signup_inputs = {}  # Clear inputs after successful signup
                st.rerun()
            elif not success:
                st.session_state.message = message 
                st.rerun()
            else:
                st.session_state.message = "Signup failed. Please try again."
        
        st.rerun()

    if st.session_state.message:
        if st.session_state.success:
            st.success(st.session_state.message)
            time.sleep(3)  
            st.session_state.message = ""  # Clear the message after a delay
            st.session_state.success = False
            st.rerun()
        else:
            st.error(st.session_state.message)

    if st.button("Back to Login"):
        st.session_state.page = "login"
        st.session_state.message = ""  # Clear any previous messages
        st.session_state.signup_inputs = {}  # Clear inputs when switching to login mode
        st.rerun()

def show_forgot_password_page():
    st.subheader("Forgot Password")

    st.session_state.forgot_password_email = st.text_input(
        "Email", value=st.session_state.forgot_password_email, autocomplete="off"
    )
    st.session_state.forgot_password_new = st.text_input(
        "New Password", type="password", value=st.session_state.forgot_password_new, autocomplete="new-password"
    )
    st.session_state.forgot_password_confirm = st.text_input(
        "Confirm Password", type="password", value=st.session_state.forgot_password_confirm, autocomplete="new-password"
    )

    if st.button("Reset Password"):
        email = st.session_state.forgot_password_email
        new_password = st.session_state.forgot_password_new
        confirm_password = st.session_state.forgot_password_confirm

        if not email or not new_password or not confirm_password:
            st.session_state.message = "Please fill in all fields."
        elif not validate_email(email):
            st.session_state.message = "Invalid email format."
        elif new_password != confirm_password:
            st.session_state.message = "Passwords do not match."
        elif not validate_password(new_password):
            st.session_state.message = "Password must be at least 8 characters long and include uppercase, lowercase,special character and a number."
        else:
            success, message = reset_password(email, new_password)
            if success:
                st.session_state.message = "Password reset successful! You can now log in with your new password."
                st.session_state.page = "login"
                st.session_state.success = True
                st.session_state.forgot_password_email = ""
                st.session_state.forgot_password_new = ""
                st.session_state.forgot_password_confirm = ""
                st.rerun()
            elif not success:
                st.session_state.message = message  # Set the message from the login function
                st.session_state.login_state = False
                st.rerun()
            else:
                st.session_state.message = "Password reset failed"
        
        st.rerun()

    if st.session_state.message:
        if st.session_state.success:
            st.success(st.session_state.message)
            st.session_state.message = ""  # Clear the message after displaying it
            st.session_state.success = False
        else:
            st.error(st.session_state.message)

    if st.button("Back to Login"):
        st.session_state.page = "login"
        st.session_state.message = ""  # Clear any previous messages
        st.session_state.forgot_password_email = ""
        st.session_state.forgot_password_new = ""
        st.session_state.forgot_password_confirm = ""
        st.rerun()

def main():
    st.title("HR Recruiter AI")

    if "page" not in st.session_state:
        st.session_state.page = "login"
    if "message" not in st.session_state:
        st.session_state.message = ""
    if "login_inputs" not in st.session_state:
        st.session_state.login_inputs = {"email": "", "password": ""}
    if "signup_inputs" not in st.session_state:
        st.session_state.signup_inputs = {}
    if "forgot_password_email" not in st.session_state:
        st.session_state.forgot_password_email = ""
    if "forgot_password_new" not in st.session_state:
        st.session_state.forgot_password_new = ""
    if "forgot_password_confirm" not in st.session_state:
        st.session_state.forgot_password_confirm = ""
    if "success" not in st.session_state:
        st.session_state.success = False

    if st.session_state.page == "login":
        show_login_page()
    elif st.session_state.page == "signup":
        show_signup_page()
    elif st.session_state.page == "forgot_password":
        show_forgot_password_page()

if __name__ == "__main__":
    main()
