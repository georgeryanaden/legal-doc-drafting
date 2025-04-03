import streamlit as st
import datetime
import os
from google import genai
from docx import Document, shared
from io import BytesIO

# --- Configure your API key securely ---
API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyBHuqIqb_udt5qKlP0fPCwqMu2JZ4vQVV4")
client = genai.Client(api_key=API_KEY)

# --- Set page config and logo ---
st.set_page_config(page_title="Legal Document Drafter", page_icon="📜")
st.image("assets/logo_inspira.jpeg", width=200)
st.title("📜 AI Legal Document Drafter")
st.markdown("Generate formal legal drafts based on your input")

# --- Define templates ---
DOC_TEMPLATES = {
    "NDA": ["Disclosing Party", "Receiving Party", "Jurisdiction", "Start Date", "End Date"],
    "Power of Attorney": ["Grantor", "Agent", "Scope of Authority", "Start Date", "End Date"],
    "Legal Dispute Complaint": [
        "Plaintiff", "Defendant", "Jurisdiction", "Incident Date", "Description", "Damages", "Monetary Relief"
    ]
}

# --- Select document type ---
doc_type = st.selectbox("Choose a Legal Document Type:", list(DOC_TEMPLATES.keys()))

# --- Input form ---
with st.form("doc_form"):
    st.subheader(f"Enter details for {doc_type}")
    user_inputs = {}
    for field in DOC_TEMPLATES[doc_type]:
        if "Date" in field:
            user_inputs[field] = st.date_input(field, value=datetime.date.today())
        elif "Description" in field or "Scope" in field or "Damages" in field:
            user_inputs[field] = st.text_area(field)
        else:
            user_inputs[field] = st.text_input(field)
    submitted = st.form_submit_button("Generate Document")

# --- Generate document ---
if submitted:
    prompt = f"Draft a formal {doc_type} with the following details:\n"
    for key, val in user_inputs.items():
        prompt += f"{key}: {val}\n"

    with st.spinner("Generating legal document..."):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            draft = response.text
            st.success("✅ Document Generated!")
            st.text_area("Generated Document", draft, height=400)

            # Create Word Document
            doc = Document()

            # Add logo to header
            section = doc.sections[0]
            header = section.header
            header_paragraph = header.paragraphs[0]
            run = header_paragraph.add_run()
            run.add_picture("assets/logo_inspira.jpeg", width=shared.Inches(1.5))

            # Add title and body
            doc.add_heading(f"{doc_type} Draft", level=1)
            for line in draft.split("\n"):
                doc.add_paragraph(line)

            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)

            # Download button for Word doc
            filename = f"{doc_type.replace(' ', '_').lower()}_draft.docx"
            st.download_button(
                label="📥 Download as Word Document",
                data=buffer,
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

        except Exception as e:
            st.error(f"❌ Error: {e}")