import ollama
import streamlit as st
import time
import os
from datetime import datetime

#####################################
#                                   #
# Streamlit App for Ollama Library  #
#                                   #
#####################################


def response_generator(msg_content):
    """
    Generates a response word by word with a delay for a typewriter effect.
    """
    lines = msg_content.split('\n')  # Split the content into lines to preserve paragraph breaks.
    for line in lines:
        words = line.split()  # Split the line into words to introduce a delay for each word.
        for word in words:
            yield word + " "
            time.sleep(0.1)
        yield "\n"  # After finishing a line, yield a newline character to preserve paragraph breaks.


def show_msgs():
    """
    Displays chat messages from the session state.
    """
    for msg in st.session_state.messages:
        if msg["role"] == "assistant":
            with st.chat_message("assistant"):
                st.write(msg["content"])
        else:
            with st.chat_message("user"):
                st.write(msg["content"])


def chat(message, model="llama3.2"):
    """
    Sends the user message to the specified model and returns the assistant's response.
    """
    try:
        response = ollama.chat(model=model, messages=[{"role": "user", "content": message}])
        return response["message"]["content"]
    except Exception as e:
        error_message = str(e).lower()
        if "not found" in error_message:
            return f"Model '{model}' not found. Please ensure it is available locally."
        else:
            return f"An unexpected error occurred: {str(e)}"


def format_chatlog(chatlog):
    """
    Formats the chat log for downloading.
    """
    return "\n".join(f"{msg['role']}: {msg['content']}" for msg in chatlog)


def save_chat():
    """
    Saves the current chat to a text file with a timestamp.
    """
    if not os.path.exists("./Chats"):
        os.makedirs("./Chats")

    if st.session_state["messages"]:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"./Chats/chat_{timestamp}.txt"
        with open(filename, "w") as f:
            for message in st.session_state["messages"]:
                f.write(f"{message['role']}: {message['content']}\n")
        st.success(f"Chat saved to {filename}")
    else:
        st.warning("No chat messages to save.")


def main():
    """
    Main function to run the Streamlit app.
    """
    st.title("Ollama Chat Interface")
    st.sidebar.title("Chat Settings")

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    # Display chat messages
    show_msgs()

    # User input
    user_input = st.chat_input("Enter your message:")
    if user_input:
        with st.chat_message("user"):
            st.write(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Get assistant response
        response = chat(user_input)
        st.session_state.messages.append({"role": "assistant", "content": response})

        # Display assistant response
        with st.chat_message("assistant"):
            st.write_stream(response_generator(response))

    # Sidebar actions
    st.sidebar.download_button(
        label="Download Chat Log",
        data=format_chatlog(st.session_state["messages"]),
        file_name="chat_log.txt",
        mime="text/plain",
    )

    if st.sidebar.button("Save Chat"):
        save_chat()

    st.sidebar.info("This application uses the Ollama 3.2 model for conversation.")


if __name__ == "__main__":
    main()
