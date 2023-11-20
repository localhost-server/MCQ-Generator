import streamlit as st
from streamlit import session_state as ss

def file_upload_check(file):
    if not hasattr(ss, 'uploaded_file') or ss.uploaded_file is None:
        # If there is no previously uploaded file, set the current file as the uploaded file
        ss.uploaded_file = file
        return True
    elif ss.uploaded_file.name == file.name:
        # If the current file has the same name as the previously uploaded file, return True
        return True
    else:
        # If the current file is different from the previously uploaded file, update the uploaded file and return False
        ss.uploaded_file = file
        return False

uploaded_file = st.file_uploader("Choose a file")

if uploaded_file:
    if file_upload_check(uploaded_file):
        st.write("File has not changed.")
    else:
        st.write("File has changed.")
