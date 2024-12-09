from dotenv import load_dotenv
import gradio as gr

import utils.openai_util as outils


load_dotenv()

SYSTEM_MESSAGE = "You are a helpful, friendly assistant."

OPENAI = "OpenAI"

LIST_OF_PROVIDERS = [OPENAI]
DEFAULT_PROVIDER = OPENAI


def user(message, history):
    return "", history + [{"role": "user", "content": message}]

def get_list_of_model_names(provider):
    if provider == OPENAI:
        return gr.Dropdown(outils.MODELS, value=outils.DEFAULT_MODEL, label="Choose model: ", interactive=True)


with gr.Blocks() as ui:
    with gr.Tab("Text"):
        with gr.Row():
            with gr.Column(scale=1):
                providers = gr.Dropdown(LIST_OF_PROVIDERS, value=OPENAI, label="Choose provider: ",
                                        interactive=True)
                models = gr.Dropdown([outils.DEFAULT_MODEL], label="Choose model: ",
                                     value=outils.DEFAULT_MODEL, interactive=True)
                with gr.Accordion("More settings", open=False):
                    temp_slider = gr.Slider(0, 1.5, value=0, step=0.1, interactive=True,
                                            info="Higher values will increase diversity of model's output")
                    system_message_box = gr.Textbox(label="System message", value=SYSTEM_MESSAGE)
                    sys_msg_box_btn = gr.Button("Submit")
            with gr.Column(scale=3):
                chatbot = gr.Chatbot(height=800, type="messages")
                msg = gr.Textbox(placeholder="Your message", label="")
                with gr.Row():
                    with gr.Column():
                        clear = gr.ClearButton([msg, chatbot])
                    with gr.Column():
                        submit_btn = gr.Button("Send")
    with gr.Tab("Images"):
        example = gr.Textbox()

    def chat(kwargs):
        history = kwargs[chatbot]
        model_name = kwargs[models]
        system_msg = kwargs[system_message_box]
        temperature = kwargs[temp_slider]
        print(system_msg)
        yield from outils.get_response(history, model_name, system_msg, temperature)

    def handle_retry(history, retry_data: gr.RetryData):
        new_history = history[:retry_data.index]
        previous_prompt = history[retry_data.index]
        new_history.append(previous_prompt)
        return new_history

    gr.on(triggers=[msg.submit, submit_btn.click],
          fn=user, inputs=[msg, chatbot], outputs=[msg, chatbot], queue=False).then(
        chat, {chatbot, models, system_message_box, temp_slider}, chatbot)

    chatbot.retry(handle_retry, [chatbot], [chatbot]).then(
        chat, {chatbot, models, system_message_box, temp_slider}, chatbot)

    providers.change(get_list_of_model_names, providers, models)
    sys_msg_box_btn.click(lambda: [], outputs=chatbot)


ui.launch()

