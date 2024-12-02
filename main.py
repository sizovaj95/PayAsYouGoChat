import os
import random
import time

from dotenv import load_dotenv
from openai import OpenAI
import gradio as gr


load_dotenv()
MODEL = 'gpt-4o-mini'
client = OpenAI()
system_message = "You are a helpful, friendly assistant."

OPEN_AI_MODELS = ['gpt-4o-mini', 'gpt-4o', 'gpt-3.5-turbo-0125']


def insert_system_role(history: list[dict]) -> list[dict]:
    if len(history) == 1:
        history = [
            {"role": "system", "content": system_message},
            history[0]
        ]
    return history


with gr.Blocks() as ui:
    with gr.Row():
        with gr.Column(scale=1):
            models = gr.Dropdown(OPEN_AI_MODELS, value='gpt-4o-mini', label="Choose model: ", interactive=True)
        with gr.Column(scale=2):
            chatbot = gr.Chatbot(height=800, type="messages")
            msg = gr.Textbox()
            with gr.Row():
                with gr.Column():
                    clear = gr.ClearButton([msg, chatbot])
                with gr.Column():
                    submit = gr.Button("Send")

    def user(message, history):
        return "", history + [{"role": "user", "content": message}]

    def chat(history: list[dict], model_name: str):
        print(model_name)
        history = insert_system_role(history)

        stream = client.chat.completions.create(
            model=model_name,
            messages=history,
            stream=True
        )
        history.append({"role": "assistant", "content": ""})
        for chunk in stream:
            history[-1]['content'] += chunk.choices[0].delta.content or ''
            yield history

    def handle_retry(history, retry_data: gr.RetryData, model_name: str):
        new_history = history[:retry_data.index]
        previous_prompt = history[retry_data.index]
        new_history.append(previous_prompt)
        yield from chat(new_history, model_name)

    msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(chat, [chatbot, models], chatbot)
    chatbot.retry(handle_retry, [chatbot, models], [chatbot])


ui.launch()

