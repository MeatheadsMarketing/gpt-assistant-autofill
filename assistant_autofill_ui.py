import streamlit as st
import openai
from typing import Dict

# --- Config ---
openai.api_key = st.secrets["OPENAI_API_KEY"]  # Add this in your Streamlit Cloud Secrets

# --- Helper Functions ---
def gpt_prefill_assistant_metadata(name: str) -> Dict:
    prompt = f"""
You are a senior AI developer assistant. Given an assistant function name like '{name}', generate suggestions for 20 assistant design fields.
Return the result in this exact JSON format:
{{
  "function_description": ["text", confidence],
  "primary_input_type": ["text", confidence],
  "expected_output": ["text", confidence],
  ...
  "example_input_output_preview": ["text", confidence]
}}
Only output JSON.
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    import json
    try:
        return json.loads(response.choices[0].message['content'])
    except:
        st.error("Failed to parse GPT output. Check prompt or model response.")
        return {}

# --- UI ---
st.title("🧠 Auto-Fill Assistant Builder")

func_name = st.text_input("Enter Assistant Name", placeholder="e.g., header fixer")

if func_name:
    if st.button("⚡ Auto-Fill Metadata from GPT"):
        st.session_state.metadata = gpt_prefill_assistant_metadata(func_name)

if "metadata" in st.session_state:
    st.subheader("📋 Assistant Field Suggestions")
    for field, (suggestion, confidence) in st.session_state.metadata.items():
        col1, col2, col3 = st.columns([6, 1, 1])
        with col1:
            locked = st.checkbox(f"Lock {field}", key=f"lock_{field}")
            if not locked:
                st.text_area(f"{field.replace('_', ' ').title()}", value=suggestion, key=field)
            else:
                st.code(suggestion, language="markdown")
        with col2:
            st.metric("Conf.", f"{confidence*100:.1f}%")
        with col3:
            if st.button("🔄", key=f"regen_{field}"):
                # Regenerate specific field
                prompt = (
                    f"Based on the assistant '{func_name}', regenerate the field '{field}' and return it as a JSON pair: "
                    f"{{\"{field}\": [\"text\", confidence]}}"
                )
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7
                )
                import json
                try:
                    field_update = json.loads(response.choices[0].message['content'])
                    st.session_state.metadata[field] = field_update[field]
                    st.experimental_rerun()
                except:
                    st.error(f"Failed to regenerate field: {field}")

    st.success("✅ All fields editable and ready for assistant code generation!")

