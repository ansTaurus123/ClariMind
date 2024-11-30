import streamlit as st
import pandas as pd
from groq import Groq

# Initialize the Groq client with your API key
client = Groq(api_key="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")

# Custom CSS for background image
def add_background_image():
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("https://raw.githubusercontent.com/ansabb420/ClariMind/main/360_F_562116144_lxZOlafYtRtv8BzmKTKGcNby0D37ZVTZ.jpg");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Add background image
add_background_image()

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
    st.session_state.questionnaire_open = True
    st.session_state.questionnaire_submitted = False
    st.session_state.chat_title = "ClariMind"

# Initialize session state variables
if 'messages' not in st.session_state:
    st.session_state.messages = []
    st.session_state.questionnaire_open = True
    st.session_state.questionnaire_submitted = False
    st.session_state.chat_title = "ClariMind"

# Function to save patient persona
def save_patient_persona(name, age, location, gender, responses):
    persona = f"""
    Patient Profile:
    - Name: {name}
    - Age: {age}
    - Gender: {gender}
    - Location: {location}
    - Symptoms:
      * Attention span issues: {responses['attention_span']}
      * Restlessness: {responses['restlessness']}
      * Anxiety: {responses['anxiety']}
      * Low energy: {responses['low_energy']}
      * Intrusive memories: {responses['intrusive_memories']}
      * Hallucinations: {responses['hallucinations']}
      * Impulsivity: {responses['impulsivity']}
      * Mood swings: {responses['mood_swings']}
      * Sleep disturbances: {responses['sleep_disturbances']}
      * Paranoia: {responses['paranoia']}
      * Emotional detachment: {responses['emotional_detachment']}
    """
    st.session_state.patient_persona = persona

# Questionnaire logic
if st.session_state.questionnaire_open and not st.session_state.questionnaire_submitted:
    st.title("Mental Health Screening")
    st.write("Please fill out the questionnaire to help us understand your condition.")

    # Basic user details
    name = st.text_input("Name", value="Patient")
    age = st.number_input("Age", min_value=1, max_value=100, value=25)
    location = st.text_input("Location")
    gender = st.selectbox("Gender", options=["Male", "Female", "Other"])

    # Diverse mental health questions
    st.header("Your Mental Health Symptoms")
    responses = {
        "attention_span": st.radio("Do you struggle with maintaining attention?", ["Yes", "No"]),
        "restlessness": st.radio("Do you feel restless or unable to relax?", ["Yes", "No"]),
        "anxiety": st.radio("Do you often feel anxious or worried?", ["Yes", "No"]),
        "low_energy": st.radio("Do you experience low energy or fatigue?", ["Yes", "No"]),
        "intrusive_memories": st.radio("Do you have distressing memories or flashbacks?", ["Yes", "No"]),
        "hallucinations": st.radio("Do you hear or see things that others cannot?", ["Yes", "No"]),
        "impulsivity": st.radio("Do you act on impulses without considering consequences?", ["Yes", "No"]),
        "mood_swings": st.radio("Do you experience frequent mood swings?", ["Yes", "No"]),
        "sleep_disturbances": st.radio("Do you have trouble sleeping?", ["Yes", "No"]),
        "paranoia": st.radio("Do you feel suspicious or paranoid?", ["Yes", "No"]),
        "emotional_detachment": st.radio("Do you feel emotionally detached or numb?", ["Yes", "No"])
    }

    # Submit button
    if st.button("Submit Questionnaire"):
        save_patient_persona(name, age, location, gender, responses)

        # Save data to a CSV file for records
        df = pd.DataFrame([{**responses, "Name": name, "Age": age, "Location": location, "Gender": gender}])
        df.to_csv("mental_health_responses.csv", mode='a', header=not pd.io.common.file_exists("mental_health_responses.csv"), index=False)

        st.session_state.questionnaire_open = False
        st.session_state.questionnaire_submitted = True
        st.success("Questionnaire submitted! Redirecting to the chat interface.")

# Chat interface logic
if not st.session_state.questionnaire_open and st.session_state.questionnaire_submitted:
    st.title(st.session_state.chat_title)

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User chat input
    user_input = st.chat_input("How can I assist you today?")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Use patient persona if available
        persona = st.session_state.get("patient_persona", "Patient profile not available.")
        messages = [system_message, {"role": "user", "content": persona}] + st.session_state.messages

        try:
            # Generate assistant response
            response = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=messages,
                temperature=0.8,
                max_tokens=500,
            )
            assistant_reply = response.choices[0].message.content
        except Exception as e:
            assistant_reply = f"Error generating response: {str(e)}"

        # Save and display assistant reply
        st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
        with st.chat_message("assistant"):
            st.markdown(assistant_reply)

# Reset option
with st.sidebar:
    if st.button("Reset App"):
        reset_chat()
