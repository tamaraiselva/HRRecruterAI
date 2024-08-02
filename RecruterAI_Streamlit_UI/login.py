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
            # st.session_state['logged_in'] = True
            st.session_state['user_id'] = user_id  # Store the user ID in session state
            st.session_state['user_role'] = user_role
            return True, user_data
        else:
            return False, "User ID not found in response"
    else:
        return False, response.text

def signup(payload):
    url = 'http://localhost:8083/api/v1/user'
    response = requests.post(url, json=payload)
    if response.status_code == 201:  # 201 is used for resource creation
        return True, response.json()
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

def main():

    if "login_state" not in st.session_state:
        st.session_state.login_state = False

    if "signup_mode" not in st.session_state:
        st.session_state.signup_mode = False

    if "message" not in st.session_state:
        st.session_state.message = ""

    if "success" not in st.session_state:
        st.session_state.success = False

    if "signup_inputs" not in st.session_state:
        st.session_state.signup_inputs = {}

    if "login_inputs" not in st.session_state:
        st.session_state.login_inputs = {"email": "", "password": ""}
 
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    if 'user_id' not in st.session_state:
        st.session_state['user_id'] = None
  
    if 'user_role' not in st.session_state:
        st.session_state['user_role'] = None

    if st.session_state.signup_mode:
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
                st.session_state.message = f"Please enter {' and '.join(empty_fields)}"
            elif len(inputs['name']) > 20:
                st.session_state.message = "Name should be up to 20 characters."
            elif not validate_email(inputs['email']):
                st.session_state.message = "Invalid email format."
            elif not validate_password(inputs['password']):
                st.session_state.message = "Password must be at least 8 characters long and include first character as uppercase, lowercase, and a number."
            elif not validate_mobile_number(inputs['mobile_number']):
                st.session_state.message = "Mobile number must be exactly 10 digits."
            else:
                payload = {field['name']: inputs[field['name']] for field in fields}
                success, message = signup(payload)

                if success:
                    st.session_state.message = "Signup successful! You can now log in."
                    st.session_state.signup_mode = False
                    st.session_state.success = True
                    st.session_state.signup_inputs = {}  # Clear inputs after successful signup
                    st.rerun()
                else:
                    st.session_state.message = f"Signup failed. Please try again. {message}"
            
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
            st.session_state.signup_mode = False
            st.session_state.message = ""  # Clear any previous messages
            st.session_state.signup_inputs = {}  # Clear inputs when switching to login mode
            st.rerun()
    
    else:
        st.subheader("Login Page")

        if st.session_state.success:
            st.success(st.session_state.message)
            st.session_state.message = ""
            st.session_state.success = False

        if st.session_state.login_state:
            st.write("Welcome to the home page!")
            if st.session_state.user_role == 'admin':
                user_data = fetch_user_data()
                if user_data:
                    st.write("All User Data:")
                    st.json(user_data)
                else:
                    st.error("Failed to fetch user data.")
            else:
                user_data = fetch_user_data(st.session_state.user_id)
                if user_data:
                    st.write("Your User Data:")
                    st.json(user_data)
                else:
                    st.error("Failed to fetch your user data.")
            
            return
           
             

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
                st.session_state.message = f"Please enter {' and '.join(empty_fields)}"
                st.rerun()
            else:
                payload = {field['name']: inputs[field['name']] for field in fields}
                success, message = login(payload)

                if success:
                    st.session_state.message = "Login successful!"
                    st.session_state.login_state = True
                    st.session_state.login_inputs = {"email": "", "password": ""}  # Clear login inputs on success
                    st.rerun()
                else:
                    st.session_state.message = f"Login failed. Please try again. {message}"
                    st.rerun()

        if st.session_state.message:
            st.error(st.session_state.message)

        if st.button("Sign Up"):
            st.session_state.signup_mode = True
            st.session_state.message = ""  # Clear any previous messages
            st.rerun()

if __name__ == "__main__":
    main()
