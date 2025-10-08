import streamlit as st
import requests
import os
import tempfile

st.set_page_config(page_title="Medicine Error Detection Companion", page_icon="🏥", layout="wide")

st.title("Medicine Error Detection Companion")
st.markdown("Enter your information and upload relevant medical documents to get personalized health insights.")

# Create a form for patient data
with st.form("patient_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        age = st.number_input("Age", min_value=0, max_value=120, value=45)
        sex = st.selectbox("Sex", options=["Male", "Female", "Other"])
        height = st.number_input("Height (cm)", min_value=0.0, value=175.0)
        weight = st.number_input("Weight (kg)", min_value=0.0, value=85.0)
        
    with col2:
        allergies = st.text_area("Allergies (if any)", value="Shellfish, Dust")
        preexisting_conditions = st.text_area("Pre-existing Conditions", value="Diabetes, Hypertension")
        medications = st.text_area("Current Medications", value="Aspirin, Atorvastatin")
        family_history = st.text_area("Family Medical History", value="Heart Disease")
    
    question = st.text_area("What health concern would you like help with?", 
                           value="I took my prescribed medication for Stable Angina Pectoris and now I feel dizzy. What could be wrong?",
                           height=100)
    
    uploaded_files = st.file_uploader("Upload medical documents (PDF/DOCX)", 
                                     type=["pdf", "docx"], 
                                     accept_multiple_files=True)
    
    submit_button = st.form_submit_button("Get Health Insights")

# Process the form submission
if submit_button:
    # Show a spinner while processing
    with st.spinner("Processing your information..."):
        # Prepare the payload
        payload = {
            "age": age,
            "sex": sex,
            "height": height,
            "weight": weight,
            "allergies": allergies,
            "preexisting_conditions": preexisting_conditions,
            "medications": medications,
            "family_history": family_history,
            "question": question
        }
        
        # Prepare files for upload
        files_to_upload = []
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Process each uploaded file
            for uploaded_file in uploaded_files:
                # Create a temporary file path
                temp_file_path = os.path.join(temp_dir, uploaded_file.name)
                
                # Save the uploaded file to the temporary path
                with open(temp_file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Add to files list for API request - use tuple with correct structure
                with open(temp_file_path, "rb") as f:
                    file_content = f.read()
                    files_to_upload.append(("files", (uploaded_file.name, file_content)))
            
            # Send request to API
            url = "http://127.0.0.1:8000/process-patient-data/"
            response = requests.post(url, data=payload, files=files_to_upload)
            
            # Display the response
            if response.status_code == 200:
                st.success("Analysis completed successfully!")
                
                # Display the response in a nicely formatted way
                st.markdown("## Health Insights")
                markdown_text = st.markdown(response.text, unsafe_allow_html=True)
                
    # Ensure proper line breaks for Markdown
                st.markdown(markdown_text) 
            else:
                st.error(f"Error: {response.status_code}")
                st.text(response.text, height=300)
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            
        finally:
            # Clean up temporary files
            import shutil
            try:
                shutil.rmtree(temp_dir)
            except:
                pass

# Add some helpful information at the bottom
st.markdown("---")
st.markdown("### About This Tool")
st.markdown("""
This tool analyzes your health information and medical documents to provide insights about potential issues.
It can help identify possible drug interactions and suggest questions to ask your doctor.
""")

# Add a disclaimer
st.warning("""
**Disclaimer**: This tool is for informational purposes only and does not replace professional medical advice.
Always consult with a healthcare provider for medical concerns.
""")

