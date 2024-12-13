from dotenv import load_dotenv
import gradio as gr
import logging
from pathlib import Path

import utils.openai_util as outils


load_dotenv()

SYSTEM_MESSAGE = "You are a helpful, friendly assistant."

OPENAI = "OpenAI"

LIST_OF_PROVIDERS = [OPENAI]
DEFAULT_PROVIDER = OPENAI


class Interface:
    providers = None
    models = None
    temp_slider = None
    system_message_box = None
    sys_msg_box_btn = None
    chatbot = None
    msg = None
    clear = None
    submit_btn = None

    image_models_dd = None
    image_prompt_box = None
    image_out = None
    image_submit_btn = None
    image_download_btn = None

    def language_tab(self):
        with gr.Tab("Text"):
            with gr.Row():
                with gr.Column(scale=1):
                    self.providers = gr.Dropdown(LIST_OF_PROVIDERS, value=OPENAI, label="Choose provider: ",
                                            interactive=True)
                    self.models = gr.Dropdown([outils.DEFAULT_LANGUAGE_MODEL], label="Choose model: ",
                                         value=outils.DEFAULT_LANGUAGE_MODEL, interactive=True)
                    with gr.Accordion("More settings", open=False):
                        self.temp_slider = gr.Slider(0, 1.5, value=0, step=0.1, interactive=True,
                                                info="Higher values will increase diversity of model's output")
                        self.system_message_box = gr.Textbox(label="System message", value=SYSTEM_MESSAGE)
                        self.sys_msg_box_btn = gr.Button("Submit")
                with gr.Column(scale=3):
                    self.chatbot = gr.Chatbot(height=800, type="messages")
                    self.msg = gr.Textbox(placeholder="Your message", label="")
                    with gr.Row():
                        with gr.Column():
                            self.clear = gr.ClearButton([self.msg, self.chatbot])
                        with gr.Column():
                            self.submit_btn = gr.Button("Send")

    def download_image(self):
        return gr.DownloadButton(visible=False)

    def image_tab(self):
        with gr.Tab("Images"):
            self.image_models_dd = gr.Dropdown([outils.DEFAULT_IMAGE_MODEL], label="Choose model: ",
                                       value=outils.DEFAULT_IMAGE_MODEL, interactive=True)
            self.image_prompt_box = gr.Textbox(placeholder="Your image description")
            self.image_submit_btn = gr.Button("Submit")
            self.image_out = gr.Image(height=500)
            self.image_download_btn = gr.DownloadButton("Save Image", value="image.jpg")

    def chat(self, kwargs):
        history = kwargs[self.chatbot]
        model_name = kwargs[self.models]
        system_msg = kwargs[self.system_message_box]
        temperature = kwargs[self.temp_slider]
        yield from outils.get_response(history, model_name, system_msg, temperature)

    def image(self, kwargs):
        image_prompt = kwargs[self.image_prompt_box]
        model_name = kwargs[self.image_models_dd]
        return outils.get_image(image_prompt, model_name)

    @staticmethod
    def handle_retry(history, retry_data: gr.RetryData):
        new_history = history[:retry_data.index]
        previous_prompt = history[retry_data.index]
        new_history.append(previous_prompt)
        return new_history

    def ui(self):
        with gr.Blocks() as ui:
            self.language_tab()
            self.image_tab()

            gr.on(triggers=[self.msg.submit, self.submit_btn.click],
                  fn=user, inputs=[self.msg, self.chatbot], outputs=[self.msg, self.chatbot], queue=False).then(
                self.chat, {self.chatbot, self.models, self.system_message_box, self.temp_slider}, self.chatbot)

            self.chatbot.retry(self.handle_retry, [self.chatbot], [self.chatbot]).then(
                self.chat, {self.chatbot, self.models, self.system_message_box, self.temp_slider}, self.chatbot)

            self.providers.change(get_list_of_model_names, self.providers, self.models)
            self.sys_msg_box_btn.click(lambda: [], outputs=self.chatbot)

            self.image_submit_btn.click(self.image, {self.image_prompt_box, self.image_models_dd}, self.image_out)
            # self.image_download_btn.click(self.download_image, None, [self.image_download_btn])
        return ui


def user(message, history):
    return "", history + [{"role": "user", "content": message}]

def get_list_of_model_names(provider):
    if provider == OPENAI:
        return gr.Dropdown(outils.LANGUAGE_MODELS, value=outils.DEFAULT_LANGUAGE_MODEL, label="Choose model: ", interactive=True)


if __name__ == "__main__":
    logging.info(f"Starting interface")
    ui = Interface().ui()
    # ui.launch(server_name="0.0.0.0", server_port=7860)
    ui.launch()
