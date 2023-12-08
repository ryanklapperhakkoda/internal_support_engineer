import streamlit as st
import openai
import time
openai.api_key = "YOUR_API_KEY_HERE"
assistant_id = "YOUR_ASSISTANT_ID_HERE"

class OpenAIAssistant:
    def __init__(self, assistant_id, api_key):
        self.assistant_id = assistant_id
        openai.api_key = api_key

    def create_thread(self, prompt):
        try:
            thread = openai.beta.threads.create()
            thread_id = thread.id

            openai.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=prompt
            )

            run = openai.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=self.assistant_id,
            )
            return run.id, thread_id
        except Exception as e:
            st.error(f"Error creating thread: {e}")
            return None, None

    def check_status(self, run_id, thread_id):
        try:
            run = openai.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run_id,
            )
            return run.status
        except Exception as e:
            st.error(f"Error checking status: {e}")
            return None

    def get_response(self, thread_id):
        try:
            response = openai.beta.threads.messages.list(thread_id=thread_id)
            return response.data[0].content[0].text.value if response.data else None
        except Exception as e:
            st.error(f"Error retrieving response: {e}")
            return None

# Streamlit Interface
def main():
    st.title("💬 Hakkoda [YOUR_PROJECT_NAME_HERE]")
    st.caption("🚀 Powered by Hakkoda")

    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

    for msg in st.session_state.messages:
        if msg["role"] == "assistant":
            with st.chat_message("assistant", avatar='https://media.licdn.com/dms/image/C560BAQH3BcJJtAN-Sg/company-logo_200_200/0/1656850510866?e=1709164800&v=beta&t=vyLg79tlK4EajdDrZFSw6o2MZY3CLtAdXqSAAAi3aTY'):
                st.write(msg["content"])
        else:
            st.chat_message("user").write(msg["content"])

    if prompt := st.chat_input():
        if not openai.api_key:
            st.info("Please add your OpenAI API key to continue.")
            st.stop()

        assistant = OpenAIAssistant(assistant_id, openai.api_key)
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        run_id, thread_id = assistant.create_thread(prompt)
        print(run_id, thread_id)
        if run_id and thread_id:
            with st.spinner("Accessing assistant..."):
                while True:
                    status = assistant.check_status(run_id, thread_id)
                    if status == "completed":
                        break
                    time.sleep(2)

            response = assistant.get_response(thread_id)
            if response:
                st.session_state.messages.append({"role": "assistant", "content": response})
                with st.chat_message("assistant", avatar='https://media.licdn.com/dms/image/C560BAQH3BcJJtAN-Sg/company-logo_200_200/0/1656850510866?e=1709164800&v=beta&t=vyLg79tlK4EajdDrZFSw6o2MZY3CLtAdXqSAAAi3aTY'):
                    st.write(response)

if __name__ == "__main__":
    main()
