import streamlit as st
from langchain_ollama import ChatOllama
from ollama import chat, ChatResponse
import ollama

# Create the model
#with open('pysch300-modelfile', 'r') as model_file:
 #   modelfile = model_file.read()

#ollama.create(model='v1menti_psych8k', Modelfile=modelfile)
#ollama.pull(model='v1menti_psych8k')

# Function to generate a response from the model
def generate_response(): 
    response = ollama.chat(model='v6.2menti', stream=True, messages=st.session_state.messages) 
    for partial_resp in response:
        token = partial_resp["message"]["content"]
        st.session_state["full_message"] += token
        yield token

def label_input(messages):
    sysmessage = {
    "role": "system",
    "content": "You must label the user inputs risk level as a single word only: normal or crisis. "
                "Do not give a response longer than a single word. Label as crisis only if the user "
                "is in danger, talking about suicide or self harm."
    }
    full_messages = [sysmessage] + messages  # Combine system message with user input
    response = ollama.chat(model='pysch1klabel', stream=True, messages=full_messages)
    label_message = ""
    for partial_resp in response:
        token = partial_resp["message"]["content"]
        label_message += token
    return label_message.strip().lower()

# Streamlit app
st.set_page_config(page_title="🧠 Menti")   #layout="wide"
st.title("🧠💬 Menti - Mental Health Support Chatbot")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Hi, I'm Menti your Mental Health Companion. How can I help you?"}]

# Message history
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message(msg["role"], avatar="🧑‍💻").write(msg["content"]) # user icon and message written
    else:
        st.chat_message(msg["role"], avatar="🤖").write(msg["content"]) # robot icon and message written

# Get input from user and generate response
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user", avatar="🧑‍💻").write(prompt)
    st.session_state["full_message"] = ""
    #get label of input and print
    st.session_state["label_message"] = ""
    user_input = [{"role": "user", "content": prompt}]
    label = label_input(user_input)
    #st.chat_message("assistant", avatar="🤖").write(label)
    if ("crisis" in label):
        st.chat_message("assistant", avatar="🤖").write("I'm really sorry you're feeling this way. Based on what you have shared, it sounds like you might be in a crisis, and I want you to know that you're not alone. There are people who care about you and want to help. I strongly encourage you to reach out to one of these free, confidential support services in the UK. Call Samaritans at 166123 to talk to someone who can listen and support you. or you can text SHOUT to 85258 to speak to a trained volunteer via text. If you are in immediate danger or need urgent care please call 999 to get the support you deserve. Help is always available.")
        st.session_state.messages.append({"role": "assistant", "content": st.session_state["full_message"]})
    else:
        st.chat_message("assistant", avatar="🤖").write_stream(generate_response)
        st.session_state.messages.append({"role": "assistant", "content": st.session_state["full_message"]})