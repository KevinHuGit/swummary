import streamlit as st
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder

# Initialize Ollama
model = ChatOllama(model="phi3:mini")

# Create ChatPromptTemplate and include message history
prompt = ChatPromptTemplate.from_messages(
    [
        MessagesPlaceholder(variable_name="message_history", n_messages=5, optional=True)
    ]
)

chain = prompt | model

# Call LLM
def generate_response(messages):
    langchain_messages = [HumanMessage(content=msg["content"]) if msg["role"] == "user" else AIMessage(content=msg["content"]) for msg in messages]
    response_generator = chain.stream(
            {
                "message_history": langchain_messages
            },
        )
    return response_generator

st.title("Ollama Chat")


#Create store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

#Display chat messages
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.write(message["content"])

#User-provided prompt
if prompt := st.chat_input():
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Generate a new response with streaming
    assistant_message = {"role": "assistant", "content": ""}
    st.session_state["messages"].append(assistant_message)
    
    with st.chat_message("assistant"):
        response_container = st.empty()
        response_generator = generate_response(st.session_state["messages"])
        
        full_response = ""
        for chunk in response_generator:
            full_response += chunk.content
            response_container.markdown(full_response + "▌")
        
        response_container.markdown(full_response)
        st.session_state["messages"][-1]["content"] = full_response