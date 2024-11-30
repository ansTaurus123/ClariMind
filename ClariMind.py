import streamlit as st
import pandas as pd
from groq import Groq

# Initialize the Groq client with your API key
client = Groq(api_key="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")

# Define the system message for the model
system_message = {
    "role": "system",
    "content": "You are a mental health assistant trained to identify symptoms of ADHD, PTSD, and schizophrenia based on user responses and provide appropriate recommendations or resources. Start conversations with empathy and stay supportive, deals user as a patient being a worthy psychiatrist."
}

# Function to reset the chat
def reset_chat():
    st.session_state.messages = []
    st.session_state.chat_title = "New Chat"

# Initialize session state variables
if 'messages' not in st.session_state:
    st.session_state.messages = []
    st.session_state.chat_title = "Mental Health Assistant"
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

# Button to open the questionnaire
if st.button("Please fill the questionnaire"):
    st.session_state.questionnaire_open = True

# Display the questionnaire if the button was clicked
if st.session_state.questionnaire_open and not st.session_state.questionnaire_submitted:
    st.header("Mental Health Screening Questionnaire")
    st.write("Please answer the following questions to help us understand your condition.")

    # Questionnaire for mental health screening
    attention_span = st.radio("Do you find it difficult to concentrate for extended periods?", ["Yes", "No"])
    restlessness = st.radio("Do you often feel restless or unable to sit still?", ["Yes", "No"])
    intrusive_memories = st.radio("Do you experience intrusive or distressing memories of traumatic events?", ["Yes", "No"])
    flashbacks = st.radio("Do you frequently relive past traumatic events (e.g., through flashbacks)?", ["Yes", "No"])
    paranoia = st.radio("Do you feel like others are watching or trying to harm you?", ["Yes", "No"])
    auditory_hallucinations = st.radio("Do you hear voices that others cannot hear?", ["Yes", "No"])
    difficulty_completing_tasks = st.radio("Do you often start tasks but fail to complete them?", ["Yes", "No"])
    emotional_numbness = st.radio("Do you feel emotionally numb or detached from people?", ["Yes", "No"])
    delusions = st.radio("Do you hold beliefs that others find unusual or illogical?", ["Yes", "No"])
    sleep_disturbances = st.radio("Do you experience difficulty falling or staying asleep?", ["Yes", "No"])
    hypervigilance = st.radio("Are you easily startled or always on guard?", ["Yes", "No"])
    impulsivity = st.radio("Do you act on impulses without considering the consequences?", ["Yes", "No"])

    # Submit button for questionnaire
    if st.button("Submit Questionnaire"):
        # Store questionnaire responses in a DataFrame
        questionnaire_data = {
            "Name": name,
            "Age": age,
            "Location": location,
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

        # Append to CSV file
        df.to_csv("mental_health_responses.csv", mode='a', header=not pd.io.common.file_exists("mental_health_responses.csv"), index=False)
        
        st.session_state.questionnaire_open = False
        st.session_state.questionnaire_submitted = True
        st.success("Thank you for completing the questionnaire!")

# Chat function (this will work regardless of the questionnaire status)
st.title(st.session_state.chat_title)

# Display all previous chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input for the chat
user_input = st.chat_input("Ask about mental health support...")
if user_input:
    # Store user message in the chat history
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Create a user profile string
    user_profile_string = f"User profile: Name: {name}, Age: {age}, Location: {location}, Gender: {gender}"

    # Prepare messages for the API call, including the profile and the conversation history
    messages = [system_message, {"role": "user", "content": user_profile_string}] + st.session_state.messages

    try:
        # Generate a response from the Groq API
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=messages,  # Send the entire conversation with profile info
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
