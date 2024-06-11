import json
import google.generativeai as genai
import os
import streamlit as st 
from io import StringIO
from PyPDF2 import PdfReader
import analysis_specs as specs

# Set your API key
os.environ["GOOGLE_API_KEY"] = "AIzaSyATpOvIF9VpbwZrYSaWpiYQmpplqL2w6Wo"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# Initialize session state for contract data and analysis results
if 'cont_data' not in st.session_state:
    st.session_state.cont_data = ""
if 'contract_details' not in st.session_state:
    st.session_state.contract_details = None
if 'contract_alerts' not in st.session_state:
    st.session_state.contract_alerts = None
if 'edit_clause_index' not in st.session_state:
    st.session_state.edit_clause_index = None
if 'edit_alert_index' not in st.session_state:
    st.session_state.edit_alert_index = None

# File uploader
uploaded_file = st.file_uploader("Upload Your Contract Here", accept_multiple_files=False, type=['pdf'])
if uploaded_file is not None and st.session_state.contract_details is None and st.session_state.contract_alerts is None and st.session_state.cont_data == "":
    pdf_reader = PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    st.session_state.cont_data = text
    
    # Define the analysis functions
    d = specs.analyze_contract
    c = specs.analyze_alerts
    
    # Define and configure the generative models
    model = genai.GenerativeModel(model_name='models/gemini-1.5-pro', tools=[d])
    model1 = genai.GenerativeModel(model_name='models/gemini-1.5-pro', tools=[c])
    
    # Generate the content for contract details
    result = model.generate_content(f"""
    You are an agent that analyses contracts for a company,
    Please add the Contract type and its clauses from this contract to the database:

    {st.session_state.cont_data}
    """, tool_config={'function_calling_config': 'ANY'})

    # Generate the content for contract alerts
    result1 = model1.generate_content(f"""
    You are an agent that analyses contracts for a company,
    Please return all detected reminders from this contract:

    {st.session_state.cont_data}
    """, tool_config={'function_calling_config': 'ANY'})

    # Parse the results
    fc = result.candidates[0].content.parts[0].function_call
    res = json.dumps(type(fc).to_dict(fc), indent=4)
    
    fc1 = result1.candidates[0].content.parts[0].function_call
    res1 = json.dumps(type(fc1).to_dict(fc1), indent=4)
    
    st.session_state.contract_details = json.loads(res)['args']['Contract_category']
    st.session_state.contract_alerts = json.loads(res1)['args']['alerts']

# Display the results if available
if st.session_state.contract_details and st.session_state.contract_alerts:
    st.subheader("Contract Details")
    st.write(f"**Contract Type:** {st.session_state.contract_details['type']}")
    st.write(f"**Start Date:** {st.session_state.contract_details['start_of_contract']}")
    st.write(f"**End Date:** {st.session_state.contract_details['end_of_contract']}")
    st.write(f"**Summary:** {st.session_state.contract_details['summary']}")

    # Display clauses in an expandable format
    st.subheader("Clauses")
    for i, clause in enumerate(st.session_state.contract_details['clauses']):
        with st.expander(f"{clause['type']}"):
            st.write(clause['description'])
            if clause['financial_info'] != "N/A":
                st.write(f"**Financial Info:** {clause['financial_info']}")
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button(f"Edit Clause {i + 1}", key=f"edit_clause_{i}"):
                    st.session_state.edit_clause_index = i
                    st.session_state.edit_clause_data = clause
            with col2:
                if st.button(f"Delete Clause {i + 1}", key=f"delete_clause_{i}"):
                    del st.session_state.contract_details['clauses'][i]
                    st.experimental_rerun()
    
    # Edit Clause Form
    if st.session_state.edit_clause_index is not None:
        st.write("Edit Clause")
        clause_data = st.session_state.contract_details['clauses'][st.session_state.edit_clause_index]
        with st.form("Edit Clause Form"):
            clause_type = st.selectbox("Clause Type", specs.clause_types, index=specs.clause_types.index(clause_data['type']))
            clause_description = st.text_area("Description", value=clause_data['description'])
            clause_financial_info = st.text_input("Financial Info", value=clause_data['financial_info'])
            submit = st.form_submit_button("Submit")
            if submit:
                st.session_state.contract_details['clauses'][st.session_state.edit_clause_index] = {
                    "type": clause_type,
                    "description": clause_description,
                    "financial_info": clause_financial_info
                }
                st.session_state.edit_clause_index = None
                st.experimental_rerun()

    with st.popover("Add Clause"):
        st.write("Add a new clause here.")
        with st.form("Add Clause"):
            clause_type = st.selectbox("Clause Type", specs.clause_types)
            clause_description = st.text_area("Description")
            clause_financial_info = st.text_input("Financial Info")
            submit = st.form_submit_button("Submit")
            if submit:
                new_clause = {
                    "type": clause_type,
                    "description": clause_description,
                    "financial_info": clause_financial_info
                }
                st.session_state.contract_details['clauses'].append(new_clause)
                st.experimental_rerun()

    # Display reminders
    st.subheader("Reminders")
    for i, alert in enumerate(st.session_state.contract_alerts):
        with st.expander(f"{alert['type']}"):
            st.write(alert['details'])
            if alert['due_date'] != "N/A":
                st.write(f"**Due Date:** {alert['due_date']}")
            if alert['amount'] != "N/A":
                st.write(f"**Amount:** {alert['amount']}")
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button(f"Edit Alert {i + 1}", key=f"edit_alert_{i}"):
                    st.session_state.edit_alert_index = i
                    st.session_state.edit_alert_data = alert
            with col2:
                if st.button(f"Delete Alert {i + 1}", key=f"delete_alert_{i}"):
                    del st.session_state.contract_alerts[i]
                    st.experimental_rerun()

    # Edit Alert Form
    if st.session_state.edit_alert_index is not None:
        st.write("Edit Alert")
        alert_data = st.session_state.contract_alerts[st.session_state.edit_alert_index]
        with st.form("Edit Alert Form"):
            alert_name = st.text_input("Alert Name", value=alert_data.get('name', ''))
            alert_type = st.selectbox("Alert Type", specs.alert_types, index=specs.alert_types.index(alert_data['type']))
            alert_due_date = st.date_input("Due Date", value=alert_data['due_date'])
            alert_amount = st.text_input("Amount", value=alert_data['amount'])
            alert_details = st.text_area("Details", value=alert_data['details'])
            submit = st.form_submit_button("Submit")
            if submit:
                st.session_state.contract_alerts[st.session_state.edit_alert_index] = {
                    "name": alert_name,
                    "type": alert_type,
                    "due_date": alert_due_date,
                    "amount": alert_amount,
                    "details": alert_details
                }
                st.session_state.edit_alert_index = None
                st.experimental_rerun()

    with st.popover("Add Alert"):
        st.write("Add a new alert here.")
        with st.form("Add Alert"):
            alert_name = st.text_input("Alert Name")
            alert_type = st.selectbox("Alert Type", specs.alert_types)
            alert_due_date = st.date_input("Due Date")
            alert_amount = st.text_input("Amount")
            alert_details = st.text_area("Details")
            submit = st.form_submit_button("Submit")
            if submit:
                new_alert = {
                    "name": alert_name,
                    "type": alert_type,
                    "due_date": alert_due_date,
                    "amount": alert_amount,
                    "details": alert_details
                }
                st.session_state.contract_alerts.append(new_alert)
                st.experimental_rerun()

    # Add some CSS for styling
    st.markdown("""
        <style>
        .css-18e3th9 {
            padding: 20px;
        }
        .css-1d391kg p {
            margin: 0;
            padding: 0.
        }
        .css-1avcm0n {
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 10px;
            margin-bottom: 10px;
        }
        </style>
        """, unsafe_allow_html=True)
