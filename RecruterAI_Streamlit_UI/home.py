import streamlit as st
from modal import Modal
import streamlit_antd_components as sac
import requests
from pymongo import MongoClient
# from streamlit_extras.switch_page_button import switch_page
import pandas as pd
import re
import time
import urllib.parse
from whatsapp_client import WhatsAppWrapper
import ast
import numpy as np 

def main():
    # MongoDB configuration
    if "message" in st.session_state and st.session_state.message:
        st.success(st.session_state.message)
        st.session_state.message = ""

    MONGO_URI = "mongodb://localhost:27017/"
    client = MongoClient(MONGO_URI)
    db = client["recruiter_ai"]
    collection = db["job_descriptions"]
    candidate_collection = db["candidates"]

    st.title("HR Recruiter AI")

    # if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    #     switch_page("login")
    
    # Define modal
    modal = Modal("Job Description", key="Job_Description", max_width=1000, padding=20,top_position="10px")

    # Initialize modal for managing users
    manage_users_modal = Modal("Manage Users", key="Manage_Users", max_width=1000, padding=20,top_position="10px")
    edit_user_modal = Modal("Edit User", key="Edit_User", max_width=1000, padding=20,top_position="10px")
    add_user_modal = Modal("Add User", key="Add_User", max_width=1000, padding=20,top_position="10px")
    settings_model = Modal("Settings", key="Settings", max_width=1000, padding=20,top_position="10px")

    # Initialize session state variables
    if 'current_job_description' not in st.session_state:
        st.session_state['current_job_description'] = ""
    if 'selected_job_id' not in st.session_state:
        st.session_state['selected_job_id'] = None
    if 'modal_open' not in st.session_state:
        st.session_state['modal_open'] = False
    if 'modal_content' not in st.session_state:
        st.session_state['modal_content'] = ""
    if 'job_submitted' not in st.session_state:
        st.session_state['job_submitted'] = False
    if 'job_updated' not in st.session_state:
        st.session_state['job_updated'] = False
    if 'JD_success_flag' not in st.session_state:
        st.session_state['JD_success_flag'] = False
    if 'setting_mobile_number_flag' not in st.session_state:
        st.session_state['setting_mobile_number_flag'] = False
    if 'setting_flag' not in st.session_state:
        st.session_state['setting_flag'] = False
    if 'whatsapp_success_flag' not in st.session_state:
        st.session_state['whatsapp_success_flag'] = False
    if 'JD_retrieve_error_flag' not in st.session_state:
        st.session_state['JD_retrieve_error_flag'] = False
    if 'JD_bad_request_error_flag' not in st.session_state:
        st.session_state['JD_bad_request_error_flag'] = False
    if 'JD_not_found_flag' not in st.session_state:
        st.session_state['JD_not_found_flag'] = False
    if 'JD_warning_flag' not in st.session_state:
        st.session_state['JD_warning_flag'] = False
    if 'update_success_flag' not in st.session_state:
        st.session_state['update_success_flag'] = False
    if 'update_error_flag' not in st.session_state:
        st.session_state['update_error_flag'] = False
    if 'update_fetch_error_flag' not in st.session_state:
        st.session_state['update_fetch_error_flag'] = False
    if 'update_warning_flag' not in st.session_state:
        st.session_state['update_warning_flag'] = False
    if 'view_candidates' not in st.session_state:
        st.session_state['view_candidates'] = False
    if 'selected_candidates' not in st.session_state:
        st.session_state['selected_candidates'] = []
    if 'creating_new_job' not in st.session_state:
        st.session_state['creating_new_job'] = False

    if 'checked_candidates' not in st.session_state:
        st.session_state['checked_candidates'] = set()  # Initialize as a set for fast add/remove operations
    if 'status_update' not in st.session_state:
        st.session_state['status_update'] = {}
    if 'df_candidates' not in st.session_state:
        st.session_state['df_candidates'] = pd.DataFrame()  # Initialize with empty DataFrame
    
    if 'user_id' not in st.session_state:
        st.session_state['user_id'] = None
    if 'user_role' not in st.session_state:
        st.session_state['user_role'] = None
    if 'show_view_candidates' not in st.session_state:
        st.session_state['show_view_candidates'] = False
    if 'save_clicked' not in st.session_state:
        st.session_state['save_clicked'] = False
    if 'first_save_clicked' not in st.session_state:
        st.session_state['first_save_clicked'] = False  # Track if "Save" was clicked for the first time

    if 'edit_mode' not in st.session_state:
        st.session_state['edit_mode'] = False
    if 'update_mode' not in st.session_state:
        st.session_state['update_mode'] = False

    # Alert boxes
    # Display success message at the top if the flag is set
    if st.session_state['setting_flag']:
        st.error("Please go to settings and update the WhatsApp API Token and WhatsApp Cloud Number ID.")
        st.session_state['setting_flag'] = False  # Reset the flag

    # Display success message at the top if the flag is set
    if st.session_state['setting_mobile_number_flag']:
        st.error("Mobile number must be exactly 10 digits.")
        st.session_state['setting_mobile_number_flag'] = False  # Reset the flag
    
    # Display success message at the top if the flag is set
    if st.session_state['whatsapp_success_flag']:
        st.success(f"Message sent successfully for the selected Candidate....")
        st.session_state['whatsapp_success_flag'] = False  # Reset the flag

    # Display success message at the top if the flag is set
    if st.session_state['JD_success_flag']:
        st.success("Job description created successfully!")
        st.session_state['JD_success_flag'] = False  # Reset the flag

    if st.session_state['JD_retrieve_error_flag']:
        st.error("Failed to retrieve job ID or job description from response.")
        st.session_state['JD_retrieve_error_flag'] = False

    if st.session_state['JD_bad_request_error_flag']:
        st.error("Bad Error Key from Hugging Face......")
        st.session_state['JD_bad_request_error_flag'] = False

    if st.session_state['JD_not_found_flag']:
        st.error("Job Description not found.")
        st.session_state['JD_not_found_flag'] = False

    if st.session_state['JD_warning_flag']:
        st.warning("Please enter a job description before submitting.")
        st.session_state['JD_warning_flag'] = False

    # Fetch job descriptions based on user role
    def fetch_job_descriptions():
        if st.session_state.user_role == 'admin':
            return list(collection.find({}, {"_id": 1, "prompt": 1, "job_description": 1}).sort([('_id', -1)]))
        else:
            user_id = st.session_state.get('user_id')
            return list(collection.find({"user_id": user_id}, {"_id": 1, "prompt": 1, "job_description": 1}).sort([('_id', -1)]))

    # Define validation functions
    def validate_email(email):
        return re.match(r"[^@]+@[^@]+\.[^@]+", email)
    
    def validate_password(password):
        return re.match(r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).{8,}$", password)
    
    def validate_mobile_number(mobile_number):
        return re.match(r"^\d{10}$", mobile_number)
    
    # Handle New Job Description
    def new_job_description():
        st.session_state['current_job_description'] = ""
        st.session_state['selected_job_id'] = None
        st.session_state['job_submitted'] = False
        st.session_state['job_updated'] = False
        st.session_state['creating_new_job'] = True
        st.session_state['view_candidates'] = False



    def submit_job_description(job_description):
        if job_description:
            api_url = "http://localhost:8081/api/v1/jd"
            payload = {"prompt": job_description}
            with st.spinner('Generating job description...'):
                try:
                    response = requests.post(api_url, json=payload)
                    if response.status_code == 201:
                        jd_response = response.json()
                        job_id = jd_response.get("id")
                        prompt_saved = job_description
                        job_description_created = jd_response.get("job_description")
                        user_id = st.session_state['user_id']  # Get the user_id from the session state

                        if job_id and job_description_created:
                            collection.insert_one({"_id": job_id, "prompt": prompt_saved, "job_description": job_description_created, "user_id": user_id})
                            st.session_state['selected_job_id'] = job_id
                            st.session_state['current_job_description'] = prompt_saved
                            st.session_state['job_submitted'] = True
                            st.session_state['JD_success_flag'] = True
                            st.session_state['save_clicked'] = False
                            st.session_state['first_save_clicked'] = False
                            st.rerun()
                        else:
                            st.session_state['JD_retrieve_error_flag'] = True
                    else:
                        if response.status_code == 500:
                            st.session_state['JD_bad_request_error_flag'] = True
                        elif response.status_code == 404:
                            st.session_state['JD_not_found_flag'] = True

                except requests.exceptions.RequestException as e:
                    st.error(f"Error: {e}")  # Display a generic error message
                    st.session_state['JD_retrieve_error_flag'] = True
        else:
            # st.warning("Please provide a job description.")
            st.session_state['JD_warning_flag'] = True


    # Update Job Description

    def update_job_description(job_description):
        if st.session_state['update_success_flag']:
            st.success("Job description updated successfully!")
            st.session_state['update_success_flag'] = False

        if st.session_state['update_error_flag']:
            st.error("Failed to update job description. Please try again.")
            st.session_state['update_error_flag'] = False

        if st.session_state['update_fetch_error_flag']:
            st.error("Failed to fetch job description. Please try again.")
            st.session_state['update_fetch_error_flag'] = False

        if st.session_state['update_warning_flag']:
            st.warning("No job description selected.")
            st.session_state['update_warning_flag'] = False
        with st.spinner('Updating job description...'):
            if st.session_state['selected_job_id'] is not None:
                api_url = f"http://localhost:8081/api/v1/jd/{st.session_state['selected_job_id']}"
                payload = {"job_description": job_description}
                update_response = requests.put(api_url, json=payload)

                if update_response.status_code == 200:
                    st.session_state['update_success_flag'] = True
                    st.session_state['job_updated'] = False
                    st.session_state['edit_mode'] = False
                    st.session_state['update_mode'] = False
                    st.session_state['first_save_clicked'] = False  # Reset this to allow re-enabling Save button
                    st.rerun()
                else:
                    st.session_state['update_error_flag'] = True
            else:
                st.session_state['update_warning_flag'] = True


    # # Display Candidates
    def display_candidates():
        with st.spinner('Loading Candidates...'):
            col1, col2, col3, col4, col5, col6 = st.columns([3,2,5,6,6,6])
            with col1:
                st.markdown("**Select**")
            with col2:
                st.markdown("**Id**")
            with col3:
                st.markdown("**Name**")
            with col4:
                st.markdown("**Email**")
            with col5:
                st.markdown("**Mobile**")
            with col6:
                st.markdown("**Status**")

            selected_job_id = st.session_state['selected_job_id']
            job_description = collection.find_one({"_id": selected_job_id})

            if job_description and "resource_id" in job_description:
                resource_id = job_description["resource_id"]
                candidates = list(candidate_collection.find({"resource_id": resource_id, "selected_job_id": selected_job_id}))

                candidate_list = []
                for candidate in candidates:
                    candidate_dict = {
                        "ID": candidate.get("ID"),
                        "Name": candidate.get("Name"),
                        "Email": candidate.get("Email"),
                        "Phone": candidate.get("Phone"),
                        "Status": candidate.get("Status")
                    }
                    candidate_list.append(candidate_dict)

                df_candidates = pd.DataFrame(candidate_list)
                st.session_state['df_candidates'] = df_candidates  # Store in session state

                # Clear previous checkbox selections
                if 'checked_candidates' not in st.session_state:
                    st.session_state['checked_candidates'] = set()
                if 'status_update' not in st.session_state:
                    st.session_state['status_update'] = {}

                for idx, row in df_candidates.iterrows():
                    col1, col2, col3, col4, col5, col6 = st.columns([3,2,5,6,6,6])

                    with col1:
                        selected = st.checkbox("", key=f"candidate_{idx}", value=idx in st.session_state['checked_candidates'])
                        if selected:
                            st.session_state['checked_candidates'].add(idx)
                        else:
                            st.session_state['checked_candidates'].discard(idx)
                    with col2:
                        st.write(row['ID'])
                    with col3:
                        st.write(row['Name'])
                    with col4:
                        st.write(row['Email'])
                    with col5:
                        st.write(row['Phone'])
                    with col6:
                        # Display status based on session state updates or database value
                        if idx in st.session_state['status_update']:
                            st.write("Interview Scheduled" if st.session_state['status_update'][idx] else "Interview Not Scheduled")
                        else:
                            st.write(row['Status'])
                if st.button("Schedule Interview"):
                    if st.session_state['checked_candidates']:
                        selected_job_id = st.session_state['selected_job_id']
                        job_description = collection.find_one({"_id": selected_job_id})
                        if job_description and "resource_id" in job_description:
                            resource_id = job_description["resource_id"]
                            update_status(df_candidates, resource_id, selected_job_id, [])
                            schedule_interviews()
                            # Clear the checkboxes and reset session state variables after scheduling
                            st.session_state['checked_candidates'] = set()
                            st.session_state['status_update'] = {}
                            st.rerun()
                        else:
                            st.error("Failed to fetch job description.")
                    else:
                        st.warning("Please select a candidate for scheduling the interview.")
            else:
                st.error("Failed to fetch candidates.")

    def update_status(df_candidates, resource_id, selected_job_id,successful_updates):
        # Initialize the session state for status updates
        st.session_state['status_update'] = {}
        
        # Loop through the list of successful updates
        for idx in successful_updates:
            candidate_id = df_candidates.iloc[idx]['ID']
            
            # Convert candidate_id to native Python type if it's a numpy type
            if isinstance(candidate_id, (np.integer, np.int64)):
                candidate_id = int(candidate_id)
            
            # Update the status of the candidate in the database
            candidate_collection.update_one(
                {"ID": candidate_id, "resource_id": resource_id, "selected_job_id": selected_job_id},
                {"$set": {"Status": "Interview Scheduled"}}
            )
            
            # Track the status update in session state
            st.session_state['status_update'][idx] = True

    # Schedule Interviews
    def schedule_interviews():
        with st.spinner('Scheduling Interview for the selected Candidate...'):
            df_candidates = st.session_state['df_candidates']  # Retrieve from session state
            successful_updates = []  # List to track successful updates
            for idx in st.session_state['checked_candidates']:
                candidate = df_candidates.iloc[idx]
                phone_number = candidate['Phone']
                user_id = st.session_state.get('user_id')
                user = fetch_user_data_by_id(user_id)
                api_token = user.get('whatsapp_api_token')
                cloud_number_id = user.get('whatsapp_cloud_number_id')
                # Check if API token and WhatsApp Cloud Number ID are provided
                if not api_token or not cloud_number_id:
                    st.session_state['setting_flag'] = True
                elif not validate_mobile_number(phone_number):
                    st.session_state['setting_mobile_number_flag'] = True
                else:
                    try:
                        client = WhatsAppWrapper(api_token, cloud_number_id)
                        client.send_template_message("hr_recruter_ai", "en_US", phone_number)
                        successful_updates.append(idx)
                        st.session_state['whatsapp_success_flag'] = True
                    except Exception as e:
                        st.error(f"Failed to send message to {phone_number}: {e}")
                        print(e)

        # Update status for candidates with successful message sending
        if successful_updates:
            selected_job_id = st.session_state['selected_job_id']
            job_description = collection.find_one({"_id": selected_job_id})
            if job_description and "resource_id" in job_description:
                resource_id = job_description["resource_id"] # Ensure job_description is correctly fetched
            update_status(df_candidates, resource_id, selected_job_id, successful_updates)

        # Clear checked candidates after scheduling
        st.session_state['checked_candidates'] = set()

        # Refresh the candidates' display
        st.rerun()

    

    # Function to fetch user data
    def fetch_user_data():
        url = 'http://localhost:8083/api/v1/user'
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            st.error("Failed to fetch user data.")
            return []
        
    def fetch_user_data_by_id(id):
        url = f'http://localhost:8083/api/v1/user/{id}'
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            st.error("Failed to fetch user data.")
            return []
        
    # Function to update user data
    def update_user_data(user_id, updated_user):
        url = f'http://localhost:8083/api/v1/user/{user_id}'
        response = requests.put(url, json=updated_user)
        if response.status_code == 200:
            #st.success("User updated successfully!")
            return True
        else:
            st.error("Failed to update user.")
            return False

    # Function to delete user
    def delete_user(user_id):
        url = f'http://localhost:8083/api/v1/user/{user_id}'
        response = requests.delete(url)
        if response.status_code == 200:
            #st.success("User deleted successfully!")
            collection.delete_many({"user_id": user_id})
            candidate_collection.delete_many({"user_id": user_id})
            return True
        else:
            st.error("Failed to delete user.")
            return False

    # Add User function
    def add_user(user):
        url = 'http://localhost:8083/api/v1/user'
        response = requests.post(url, json=user)
        if response.status_code == 201:
            #st.success("User added successfully!")
            return True
        else:
            st.error("Failed to add user.")
            return False


    # # Sidebar
    with st.sidebar:
        job_descriptions = fetch_job_descriptions()
        # Button to manage users if user is admin
        if st.session_state['user_role'] == 'admin':
            if st.button("Manage Users"):
                manage_users_modal.open()
        if st.button("Settings"):
            settings_model.open()
        if st.button("Logout", key="logout_button_home"):
            st.session_state.login_state = False
            st.session_state.login_successful = False
            st.session_state.message = ""
            st.session_state.login_inputs = {"email": "", "password": ""}

            st.session_state['current_job_description'] = ""
            st.session_state['selected_job_id'] = None
            st.session_state['modal_open'] = False
            st.session_state['modal_content'] = ""
            st.session_state['job_submitted'] = False
            st.session_state['job_updated'] = False
            st.session_state['view_candidates'] = False
            st.session_state['selected_candidates'] = []
            st.session_state['creating_new_job'] = False

            st.session_state.user_data = {}  # Clear user data
            st.session_state['current_job_description'] = ""
            st.session_state['selected_job_id'] = None
            st.session_state['modal_open'] = False
            st.session_state['modal_content'] = ""
            st.session_state['job_submitted'] = False
            st.session_state['job_updated'] = False
            st.session_state['view_candidates'] = False
            st.session_state['selected_candidates'] = []
            st.session_state['creating_new_job'] = False

            st.session_state.user_data = {}  # Clear user data
            st.rerun()
        # st.sidebar.button("Logout", on_click=logout)
        sac.divider(label='Job Description', align='center', color='gray')
        st.sidebar.button("New Job Description", on_click=new_job_description)
        # Search bar for job IDs
        search_term = st.sidebar.text_input("Search Job ID:", "")
        # Filter job descriptions based on search term
        filtered_jobs = [job for job in job_descriptions if search_term in str(job['_id'])]
        for job in filtered_jobs:
            job_id = job['_id']
            job_label = f"Job ID: {job_id}"
            is_selected = st.session_state['selected_job_id'] == job_id
            button_text = f"{job_label} {'(Selected)' if is_selected else ''}"

            if st.sidebar.button(button_text, key=f"job_{job_id}"):
                st.session_state['selected_job_id'] = job_id
                st.session_state['current_job_description'] = job.get('prompt', '')
                st.session_state['job_submitted'] = True
                st.session_state['job_updated'] = False
                st.session_state['creating_new_job'] = False
                st.session_state['view_candidates'] = False
                st.session_state['checked_candidates'] = set()
                st.session_state['status_update'] = {}
                st.session_state['save_clicked'] = False
                st.rerun()
    

    # Job description input
    text_area_disabled = st.session_state['selected_job_id'] is not None
    job_description = st.text_area("Describe the Job Profile", value=st.session_state['current_job_description'], height=150, disabled=text_area_disabled)

    # Create columns for buttons
    col1, col2 = st.columns(2)

    with col1:
        submit_disabled = st.session_state['selected_job_id'] is not None
        if st.button("Submit", disabled=submit_disabled):
            submit_job_description(job_description)

    with col2:
        if st.session_state['job_submitted']:
            if st.session_state['selected_job_id']:
                col1, col2 = st.columns(2)

                with col1:
                    open_modal = st.button("View Job Description")
                    with st.spinner('fetching job description...'):
                        if open_modal:
                            modal.open()

                with col2:
                    # Show the View Candidates button only after the first save
                    if st.session_state['first_save_clicked']:
                        view_candidates_button = st.button("View Candidates")
                        if view_candidates_button:
                            st.session_state['view_candidates'] = True
                    elif st.session_state['save_clicked']:
                        st.session_state['first_save_clicked'] = True
                        view_candidates_button = st.button("View Candidates")
                        if view_candidates_button:
                            st.session_state['view_candidates'] = True


    if modal.is_open():
        with modal.container():
            if st.session_state['update_success_flag']:
                st.success("Job description updated successfully!")
                st.session_state['update_success_flag'] = False

            if st.session_state['update_error_flag']:
                st.error("Failed to update job description. Please try again.")
                st.session_state['update_error_flag'] = False

            if st.session_state['update_fetch_error_flag']:
                st.error("Failed to fetch job description. Please try again.")
                st.session_state['update_fetch_error_flag'] = False

            if st.session_state['update_warning_flag']:
                st.warning("No job description selected.")
                st.session_state['update_warning_flag'] = False

            if st.session_state['selected_job_id'] is not None:
                api_url = f"http://localhost:8081/api/v1/jd/{st.session_state['selected_job_id']}"
                response = requests.get(api_url)

                if response.status_code == 200:
                    jd_response = response.json()
                    # Determine if text area should be disabled
                    is_disabled = not st.session_state['job_updated'] and st.session_state['job_submitted']
                    job_description = st.text_area("Job Description", value=jd_response.get('job_description', ''), height=250, disabled=is_disabled)
                    col1, col2 = st.columns(2)
                    with col1:
                        # Add Save button
                        save_button = st.button("Save", disabled=st.session_state['edit_mode'] or st.session_state['first_save_clicked'])
                        with st.spinner('Filtering Candidates...'):
                            if save_button:
                                # Save job description logic
                                st.session_state['first_save_clicked'] = True 
                                candidate_url = "http://localhost:8085/api/v1/resource/"
                                payload = {"job_description": job_description}  # JD from Streamlit database
                                
                                try:
                                    candidate_response = requests.post(candidate_url, json=payload)
                                    if candidate_response.status_code == 200:
                                        candidate_data = candidate_response.json()
                                        resource_id = candidate_data.get("id")
                                        selected_job_id = st.session_state['selected_job_id']
                                        user_id = st.session_state.get('user_id')

                                        # Check if the resource_id already exists in the database
                                        existing_record = collection.find_one({"_id": selected_job_id, "resource_id": {"$exists": True}})

                                        if existing_record:
                                            # Update the existing record with the new resource_id
                                            collection.update_one(
                                                {"_id": selected_job_id},
                                                {"$set": {"resource_id": resource_id}}
                                            )
                                        else:
                                            # Insert resource_id into the corresponding JD in the database
                                            collection.update_one(
                                                {"_id": selected_job_id},
                                                {"$set": {"resource_id": resource_id}}
                                            )

                                        candidate_list = []
                                        if "resource" in candidate_data:
                                            resource_data = candidate_data["resource"]
                                            if resource_data != []:
                                                if resource_data:
                                                    for item in resource_data:
                                                        try:
                                                            # Parse the item string to a list of candidate information
                                                            outer_list = ast.literal_eval(item)
                                                            for candidate_info in outer_list:
                                                                candidate_dict = {
                                                                    "ID": candidate_info[0],
                                                                    "Name": candidate_info[1],
                                                                    "Email": candidate_info[2],
                                                                    "Phone": candidate_info[3],
                                                                    "Status": "Interview Not Scheduled",
                                                                    "resource_id": resource_id,
                                                                    "selected_job_id": selected_job_id,
                                                                    "user_id": user_id
                                                                }
                                                                candidate_list.append(candidate_dict)
                                                            st.success("Candidate filtered Successfully...")
                                                        except Exception as e:
                                                            st.error("No candidates matched for the Job Description...")
                                            else:
                                                st.error("No candidates matched for the Job Description...")

                                        # Save or update candidates in MongoDB
                                        for candidate in candidate_list:
                                            # Define the query to find candidates with the same job ID and user ID
                                            query = {"selected_job_id": selected_job_id, "user_id": candidate.get("user_id")}
                                            # Delete existing candidates with the same job ID and user ID
                                            candidate_collection.delete_many(query)
                                            candidate_collection.insert_one(candidate)

                                    else:
                                        st.error(f"Error: {candidate_response.status_code}")
                                        st.write(candidate_response.json())
                                except requests.exceptions.RequestException as e:
                                    st.error(f"Request failed: {e}")                                

                    with col2:
                    # Create columns for Edit and Update buttons
                        edit_col, update_col = st.columns([1, 1])
                        with edit_col:
                            edit_button = st.button("Edit")
                            with st.spinner('Editing job description...'):
                                if edit_button:
                                    st.session_state['edit_mode'] = True
                                    st.session_state['job_updated'] = True
                                    st.rerun()
    
                        with update_col:
                            if st.session_state['edit_mode']:
                                update_button = st.button("Update")
                                if update_button:
                                    update_job_description(job_description)
                                    st.session_state['edit_mode'] = False 
                                    st.session_state['job_updated'] = True  
                                    st.rerun()
                            
                else:
                    st.session_state['update_fetch_error_flag'] = True
            else:
                st.session_state['update_warning_flag'] = True

    if st.session_state['view_candidates']:
        display_candidates()

    # Define the content of the manage users modal
    if manage_users_modal.is_open():
        with manage_users_modal.container():
            # Show success message if the update was successful
            if 'update_success' in st.session_state and st.session_state.update_success:
                st.success("User updated successfully!")
                del st.session_state.update_success
            # Show success message if the update was successful
            if 'added_success' in st.session_state and st.session_state.added_success:
                st.success("User Added successfully!")
                del st.session_state.added_success
            # Show success message if the update was successful
            if 'delete_success' in st.session_state and st.session_state.delete_success:
                st.success("User Deleted successfully!")
                del st.session_state.delete_success
            # Add User Button
            if st.button("Add User"):
                add_user_modal.open()

            # Display progress bar
            progress_bar = st.progress(0)
            progress_bar.progress(10)  # Set initial progress
    
            # Fetch user data with loading indication
            user_data = []
            try:
                user_data = fetch_user_data()
                # Simulate loading time for demonstration purposes
                for i in range(20, 100, 10):
                    progress_bar.progress(i)
                    time.sleep(0.1)  # Simulate loading time
            except Exception as e:
                st.error(f"Error fetching user data: {e}")
    
            progress_bar.progress(100)
            progress_bar.empty()
            # Complete progress bar
            
            if user_data:
                # Filter out the admin details
                filtered_user_data = [user for user in user_data if user['email'] != 'admin@gmail.com']

                col1, col2, col3, col4 = st.columns([3, 2, 2, 2])

                with col1:
                    st.markdown("**id**")
                with col2:
                    st.markdown("**Name**")
                with col3:
                    st.markdown("**Edit**")
                with col4:
                    st.markdown("**Delete**")
    
                for index, user in enumerate(filtered_user_data):
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 2])

                    with col1:
                        st.write(index + 1)
                    with col2:
                        st.write(user['name'])
                    with col3:
                        if st.button("Edit", key=f"edit_{index}"):
                            st.session_state['current_user'] = user
                            edit_user_modal.open()
                    with col4:
                        if st.button("Delete", key=f"delete_{index}"):
                            if delete_user(user['id']):
                                st.session_state.delete_success = True
                                st.rerun()
        
    # Define the content of the edit user modal
    if edit_user_modal.is_open():
        with edit_user_modal.container():
            user = st.session_state.get('current_user', {})

            if user:
                with st.form("edit_form"):
                    name = st.text_input("Name", value=user.get('name', ''))
                    email = st.text_input("Email", value=user.get('email', ''))
                    mobile_number = st.text_input("Mobile Number", value=user.get('mobile_number', ''))
                    location = st.text_input("Location", value=user.get('location', ''))
                    

                    submit_button = st.form_submit_button("Update")
                    if submit_button:
                        # Validate inputs
                        if not name or not email or not mobile_number or not location:
                            st.error("Please fill in all fields.")
                        elif len(name) > 20:
                            st.error("Name should be up to 20 characters.")
                        elif not validate_email(email):
                            st.error("Invalid email format.")
                        elif not validate_mobile_number(mobile_number):
                            st.error("Mobile number must be exactly 10 digits.")
                        else:
                            updated_user = {
                                "name": name,
                                "email": email,
                                "mobile_number": int(mobile_number),
                                "location": location
                            }

                            # Compare the existing and updated user data to check for changes
                            changes_made = False
                            for key in updated_user:
                                if updated_user[key] != user.get(key):
                                    changes_made = True
                                    break

                            if not changes_made:
                                st.info("No changes have been made.")
                            else:
                                if update_user_data(user['id'], updated_user):
                                    st.session_state.update_success = True
                                    edit_user_modal.close()
                                    st.rerun()

    # Define the content of the add user modal
    if add_user_modal.is_open():
        with add_user_modal.container():

            with st.form("add_form"):
                name = st.text_input("Name")
                email = st.text_input("Email")
                mobile_number = st.text_input("Mobile Number")
                location = st.text_input("Location")
                password = st.text_input("Password", type="password")

                if st.form_submit_button("Add User"):
                    # Validate inputs
                    if not name or not email or not mobile_number or not location or not password:
                        st.error("Please fill in all fields.")
                    elif len(name) > 20:
                        st.error("Name should be up to 20 characters.")
                    elif not validate_email(email):
                        st.error("Invalid email format.")
                    elif not validate_password(password):
                        st.error("Password must be at least 8 characters long and include uppercase, lowercase, and a number.")
                    elif not validate_mobile_number(mobile_number):
                        st.error("Mobile number must be exactly 10 digits.")
                    else:
                        new_user = {
                            "name": name,
                            "email": email,
                            "mobile_number": int(mobile_number),
                            "location": location,
                            "password": password
                        }
                    if add_user(new_user):
                        st.session_state.added_success = True
                        add_user_modal.close()
                        st.rerun()
                    else:
                        st.error("Failed to add user. Please try again.")

    # Define the content of the add user modal
    if settings_model.is_open():
        with settings_model.container():
            # Show success message if the update was successful
            if 'update_success' in st.session_state and st.session_state.update_success:
                st.success("User updated successfully!")
                del st.session_state.update_success
            # Fetch user data
            user_id = st.session_state.get('user_id')
            user = fetch_user_data_by_id(user_id)  # Fetch user data by ID
    
            if user:
                with st.form("edit_form"):
                    # Form fields pre-populated with user data
                    name = st.text_input("Name", value=user.get('name', ''))
                    email = st.text_input("Email", value=user.get('email', ''))
                    mobile_number = st.text_input("Mobile Number", value=str(user.get('mobile_number', '')))  # Convert to string for text input
                    location = st.text_input("Location", value=user.get('location', ''))
                    # Password fields for resetting password
                    new_password = st.text_input("New Password", value="", type="password")
                    confirm_password = st.text_input("Confirm New Password", value="", type="password")
                    whatsapp_api_token = st.text_input("WhatsApp API Token", value=user.get('whatsapp_api_token', ''))
                    whatsapp_cloud_number_id = st.text_input("WhatsApp Cloud Number", value=user.get('whatsapp_cloud_number_id', ''))
                    
                    submit_button = st.form_submit_button("Update")
                    if submit_button:
                        try:
                            # Validate inputs
                            if not name or not email or not mobile_number or not location:
                                st.error("Please fill in all fields.")
                            elif len(name) > 20:
                                st.error("Name should be up to 20 characters.")
                            elif not validate_email(email):
                                st.error("Invalid email format.")
                            elif new_password and not validate_password(new_password):
                                st.error("Password must be at least 8 characters long and include uppercase, lowercase, and a number.")
                            elif new_password != confirm_password:
                                st.error("New password and confirmation do not match.")
                            elif not validate_mobile_number(mobile_number):
                                st.error("Mobile number must be exactly 10 digits.")
                            else:
                                # Convert mobile number to int, handle errors if conversion fails
                                updated_user = {
                                    "name": name,
                                    "email": email,
                                    "mobile_number": int(mobile_number),
                                    "location": location,
                                    "whatsapp_api_token": whatsapp_api_token,
                                    "whatsapp_cloud_number_id": whatsapp_cloud_number_id
                                }
                                # Include the new password if provided
                                if new_password:
                                    updated_user["password"] = new_password
                                # Compare the existing and updated user data to check for changes
                                changes_made = False
                                for key in updated_user:
                                    if key == 'password':
                                        if new_password and updated_user[key] != user.get(key):
                                            changes_made = True
                                            break
                                    elif updated_user[key] != user.get(key):
                                        changes_made = True
                                        break
                                    
                                if not changes_made:
                                    st.info("No changes have been made.")
                                else:
                                    if update_user_data(user_id, updated_user):
                                        st.session_state.update_success = True
                                        st.rerun()  # Reload the page to reflect changes
                        except ValueError:
                            st.error("Please enter a valid mobile number.")
                            
if __name__ == "__main__":
    main()