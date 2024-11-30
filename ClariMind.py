import streamlit as st
import pandas as pd
from groq import Groq

# Initialize the Groq client with your API key
client = Groq(api_key="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")

# System message for the assistant
system_message = {
    "role": "system",
    "content": (
        "You are a mental health assistant trained to identify symptoms of ADHD, PTSD, and schizophrenia "
        "based on user responses and provide empathetic support, recommendations, and mindfulness activities. "
        "Your responses should prioritize practical solutions tailored to the user's symptoms."
    )
}

# Reset chat functionality
def reset_chat():
    st.session_state.messages = []
    st.session_state.chat_title = "ClariMind"
    st.session_state.questionnaire_open = False
    st.session_state.questionnaire_submitted = False

# Initialize session state variables
if 'messages' not in st.session_state:
    st.session_state.messages = []
    st.session_state.chat_title = "ClariMind"
if 'questionnaire_open' not in st.session_state:
    st.session_state.questionnaire_open = False
if 'questionnaire_submitted' not in st.session_state:
    st.session_state.questionnaire_submitted = False

# Sidebar for user inputs
with st.sidebar:
    st.header("User Inputs")
    name = st.text_input("Name", value="Patient")
    age = st.number_input("Age", min_value=1, max_value=100, value=25)
    location = st.text_input("Location")
    gender = st.selectbox("Gender", options=["Male", "Female", "Other"])

    if st.button("Reset Chat"):
        reset_chat()

# Button to initiate questionnaire
if st.button("Fill the Questionnaire"):
    st.session_state.questionnaire_open = True

# Display questionnaire
if st.session_state.questionnaire_open and not st.session_state.questionnaire_submitted:
    st.header("Mental Health Screening Questionnaire")
    st.write("Please answer the questions to help us understand your condition.")

    # Questionnaire
    attention_span = st.radio("Do you have difficulty concentrating?", ["Yes", "No"])
    restlessness = st.radio("Do you often feel restless?", ["Yes", "No"])
    intrusive_memories = st.radio("Do you have intrusive thoughts or flashbacks?", ["Yes", "No"])
    hallucinations = st.radio("Do you hear voices others cannot?", ["Yes", "No"])
    impulsivity = st.radio("Do you act impulsively?", ["Yes", "No"])
    sleep_issues = st.radio("Do you have trouble sleeping?", ["Yes", "No"])

    if st.button("Submit Questionnaire"):
        # Generate patient persona
        patient_persona = f"""
        Patient Profile:
        - Name: {name}
        - Age: {age}
        - Gender: {gender}
        - Location: {location}
        - Symptoms:
          * Difficulty concentrating: {attention_span}
          * Restlessness: {restlessness}
          * Intrusive thoughts/flashbacks: {intrusive_memories}
          * Hallucinations: {hallucinations}
          * Impulsivity: {impulsivity}
          * Sleep issues: {sleep_issues}
        """
        st.session_state.patient_persona = patient_persona
        st.session_state.questionnaire_submitted = True
        st.success("Questionnaire submitted! Proceed to the chat interface.")

# Chat interface
if st.session_state.questionnaire_submitted:
    st.title(st.session_state.chat_title)

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_input = st.chat_input("How can I assist you?")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Build the assistant response context
        persona = st.session_state.get("patient_persona", "Patient profile not available.")
        messages = [system_message, {"role": "user", "content": persona}] + st.session_state.messages

        try:
            response = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=messages,
                temperature=0.8,
                max_tokens=500,
            )
            assistant_reply = response.choices[0].message.content
        except Exception as e:
            assistant_reply = f"Error generating response: {str(e)}"

        st.session_state.messages.append({"role": "assistant", "content": assistant_reply})

        with st.chat_message("assistant"):
            st.markdown(assistant_reply)
