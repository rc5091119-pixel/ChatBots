import streamlit as st
from Backend import chatbot
from langchain_core.messages import HumanMessage
import uuid


def generate_thread_id():
    return str(uuid.uuid4())


def add_thread(thread_id, thread_title="New Chat"):
    for thread in st.session_state["chat_threads"]:
        if thread["thread_id"] == thread_id:
            return

    st.session_state["chat_threads"].append({
        "thread_id": thread_id,
        "thread_title": thread_title
    })


def reset_chat():
    new_thread_id = generate_thread_id()

    st.session_state["thread_id"] = new_thread_id
    st.session_state["message_history"] = []

    add_thread(new_thread_id, "New Chat")


def load_conversation(thread_id):
    state = chatbot.get_state(
        config={"configurable": {"thread_id": thread_id}}
    )
    return state.values.get("messages", [])


def update_thread_title(thread_id, title):
    for thread in st.session_state["chat_threads"]:
        if thread["thread_id"] == thread_id:
            if thread["thread_title"] == "New Chat":
                thread["thread_title"] = title[:40]
            return


# ---------------- Session State ----------------

if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()

if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = []

add_thread(st.session_state["thread_id"], "New Chat")

CONFIG = {
    "configurable": {
        "thread_id": st.session_state["thread_id"]
    }
}

# ---------------- Sidebar ----------------

st.sidebar.title("LangGraph Chatbot")

if st.sidebar.button("➕ New Chat"):
    reset_chat()
    st.rerun()

st.sidebar.header("My Conversations")

for thread in st.session_state["chat_threads"][::-1]:

    if st.sidebar.button(
        thread["thread_title"],
        key=thread["thread_id"]
    ):

        st.session_state["thread_id"] = thread["thread_id"]

        messages = load_conversation(thread["thread_id"])

        temp_messages = []

        for msg in messages:

            if isinstance(msg, HumanMessage):
                temp_messages.append({
                    "role": "user",
                    "content": msg.content
                })
            else:
                temp_messages.append({
                    "role": "assistant",
                    "content": msg.content
                })

        st.session_state["message_history"] = temp_messages
        st.rerun()


for msg in st.session_state["message_history"]:
    with st.chat_message(msg["role"]):
        st.text(msg["content"])



#{"role": "user", "content": "Hello!"}
#{"role": "assistant", "content": "Hello!"}

user_input = st.chat_input("Enter your text here")

if user_input:

    update_thread_title(st.session_state["thread_id"], user_input)

    st.session_state["message_history"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.text(user_input)

    #st.session_state["message_history"].append({"role": "assistant", "content": ai_message})
    with st.chat_message("assistant"):
        ai_message = st.write_stream(
            message_chunk.content for message_chunk,metadata in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="messages"
            )
        )

    st.session_state["message_history"].append({"role": "assistant", "content": ai_message})
        

    

    