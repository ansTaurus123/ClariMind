import streamlit as st
import pandas as pd
from groq import Groq

# Initialize the Groq client with your API key
client = Groq(api_key="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")

# Custom CSS for full-page background image
def add_fullpage_background_image():
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("https://raw.githubusercontent.com/ansabb420/ClariMind/main/360_F_562116144_lxZOlafYtRtv8BzmKTKGcNby0D37ZVTZ.jpg");
            background-size: cover;  /* Ensures the image covers the full screen */
            background-repeat: no-repeat;  /* Prevents tiling */
            background-position: center;  /* Centers the image */
            background-attachment: fixed;  /* Keeps the image fixed while scrolling */
            height: 100vh;  /* Sets the height to full viewport height */
            overflow: hidden;  /* Prevents scrollbars from showing */
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Add background image
add_fullpage_background_image()

# Define the system message for the model
system_message = {
    "role": "system",
    "content": "You are a mental health assistant trained to identify symptoms of ADHD, PTSD, and schizophrenia based on user responses and provide appropriate recommendations, resources and perscriptions as per patients condition by thoroughly exploring his state of mind. Start conversations with empathy and stay supportive, like an expert psycho therapist"
}

# Function to reset the chat
def reset_chat():
    st.session_state.messages = []
    st.session_state.chat_title = "New Chat"

# Initialize session state variables
if 'messages' not in st.session_state:
    st.session_state.messages = []
    st.session_state.chat_title = "CLARIMIND"
if 'questionnaire_open' not in st.session_state:
    st.session_state.questionnaire_open = False
if 'questionnaire_submitted' not in st.session_state:
    st.session_state.questionnaire_submitted = False

# Sidebar for user inputs
with st.sidebar:
    st.header("User Inputs")
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=1, max_value=100, value=25)
    location = st.text_input("Location")
    gender = st.selectbox("Gender", options=["Male", "Female", "Other"])

    if st.button("Reset Chat"):
        reset_chat()

# After submitting the questionnaire
if st.button("Submit Questionnaire"):
    # Generate the patient persona based on questionnaire responses
    patient_persona = (
        f"Patient Profile:\n"
        f"- Name: {name}\n"
        f"- Age: {age}\n"
        f"- Location: {location}\n"
        f"- Gender: {gender}\n"
        f"- Symptoms:\n"
        f"  * Attention Span Issues: {'Yes' if attention_span == 'Yes' else 'No'}\n"
        f"  * Restlessness: {'Yes' if restlessness == 'Yes' else 'No'}\n"
        f"  * Intrusive Memories: {'Yes' if intrusive_memories == 'Yes' else 'No'}\n"
        f"  * Flashbacks: {'Yes' if flashbacks == 'Yes' else 'No'}\n"
        f"  * Paranoia: {'Yes' if paranoia == 'Yes' else 'No'}\n"
        f"  * Auditory Hallucinations: {'Yes' if auditory_hallucinations == 'Yes' else 'No'}\n"
        f"  * Difficulty Completing Tasks: {'Yes' if difficulty_completing_tasks == 'Yes' else 'No'}\n"
        f"  * Emotional Numbness: {'Yes' if emotional_numbness == 'Yes' else 'No'}\n"
        f"  * Delusions: {'Yes' if delusions == 'Yes' else 'No'}\n"
        f"  * Sleep Disturbances: {'Yes' if sleep_disturbances == 'Yes' else 'No'}\n"
        f"  * Hypervigilance: {'Yes' if hypervigilance == 'Yes' else 'No'}\n"
        f"  * Impulsivity: {'Yes' if impulsivity == 'Yes' else 'No'}\n"
    )

    # Save the persona in session state for persistent use
    st.session_state.patient_persona = patient_persona

    # Store questionnaire responses in a DataFrame for record-keeping
    questionnaire_data = {
        "Name": name,
        "Age": age,
        "Location": location,
        "Gender": gender,
        "Attention Span": attention_span,
        "Restlessness": restlessness,
        "Intrusive Memories": intrusive_memories,
        "Flashbacks": flashbacks,
        "Paranoia": paranoia,
        "Auditory Hallucinations": auditory_hallucinations,
        "Difficulty Completing Tasks": difficulty_completing_tasks,
        "Emotional Numbness": emotional_numbness,
        "Delusions": delusions,
        "Sleep Disturbances": sleep_disturbances,
        "Hypervigilance": hypervigilance,
        "Impulsivity": impulsivity
    }

    df = pd.DataFrame([questionnaire_data])  # Create DataFrame from dictionary
    df.to_csv("mental_health_responses.csv", mode='a', header=not pd.io.common.file_exists("mental_health_responses.csv"), index=False)

    st.session_state.questionnaire_open = False
    st.session_state.questionnaire_submitted = True
    st.success("Thank you for completing the questionnaire! Your patient profile has been created.")

# Chat function with persona integration
st.title(st.session_state.chat_title)

# Display all previous chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input for the chat
user_input = st.chat_input("How can I assist you today?")
if user_input:
    # Store user message in the chat history
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Prepare the patient persona if available
    if 'patient_persona' in st.session_state:
        persona = st.session_state.patient_persona
    else:
        persona = "Patient has not filled the questionnaire."

    # Create a full message string
    messages = [system_message, {"role": "user", "content": persona}] + st.session_state.messages

    try:
        # Generate a response from the Groq API
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=messages,  # Send persona and chat history
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=False,
        )

        # Ensure response is valid
        if completion.choices and len(completion.choices) > 0:
            response_content = completion.choices[0].message.content
        else:
            response_content = "Sorry, I couldn't generate a response."

    except Exception as e:
        response_content = f"Error: {str(e)}"

    # Store assistant response in the chat history
    st.session_state.messages.append({"role": "assistant", "content": response_content})

    # Display assistant response
    with st.chat_message("assistant"):
        st.markdown(response_content)
