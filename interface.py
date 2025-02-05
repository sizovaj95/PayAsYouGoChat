import json
import functools
import gradio as gr
import logging
import os
from pathlib import Path

import utils.openai_manager as oman
import utils.anthropic_manager as aman
import utils.util as util


IS_TEST = False

SYSTEM_MESSAGE = "You are a helpful, friendly assistant."

OPENAI = "OpenAI"
ANTHROPIC = "Anthropic"

LIST_OF_PROVIDERS = [OPENAI, ANTHROPIC]
DEFAULT_PROVIDER = OPENAI


class Interface:
    ai_manager = oman.OpenAi()
    prev_provider = OPENAI

    providers_dd = None
    models_dd = None
    temp_slider = None
    system_message_box = None
    sys_msg_box_btn = None
    chatbot = None
    msg_box = None
    clear_btn = None
    submit_btn = None
    save_btn = None

    image_models_dd = None
    image_prompt_box = None
    image_out = None
    image_submit_btn = None
    image_download_btn = None
    image_status_out_box = None

    history_prov_dd = None
    dates_dd = None
    provider_dict = None
    history_out = None

    def history_tab(self):
        with gr.Tab("History"):
            with gr.Row():
                with gr.Column(scale=1):
                    self.history_prov_dd, self.dates_dd = self.update_providers_history_dict()
                with gr.Column(scale=3):
                    self.history_out = gr.Markdown("")

    def language_tab(self):
        with gr.Tab("Text"):
            with gr.Row():
                with gr.Column(scale=1):
                    self.providers_dd = gr.Dropdown(LIST_OF_PROVIDERS, value=OPENAI, label="Choose provider: ",
                                            interactive=True)
                    self.models_dd = gr.Dropdown([self.ai_manager.default_language_model], label="Choose model: ",
                                         value=self.ai_manager.default_language_model, interactive=True)
                    with gr.Accordion("More settings", open=False):
                        self.temp_slider = gr.Slider(0, 1.5, value=0, step=0.1, interactive=True,
                                                info="Higher values will increase diversity of model's output")
                        self.system_message_box = gr.Textbox(label="System message", value=SYSTEM_MESSAGE)
                        self.sys_msg_box_btn = gr.Button("Submit")
                with gr.Column(scale=3):
                    self.chatbot = gr.Chatbot(height=700, type="messages")
                    self.msg_box = gr.Textbox(placeholder="Your message", label="")
                    with gr.Row():
                        with gr.Column():
                            self.clear_btn = gr.Button("Clear")
                        with gr.Column():
                            self.submit_btn = gr.Button("Send")
                        with gr.Column():
                            self.save_btn = gr.Button("Save")

    def image_tab(self):
        with gr.Tab("Images"):
            self.image_models_dd = gr.Dropdown([self.ai_manager.default_image_model], label="Choose model: ",
                                       value=self.ai_manager.default_image_model, interactive=True)
            self.image_prompt_box = gr.Textbox(placeholder="Your image description")
            self.image_submit_btn = gr.Button("Submit")
            self.image_out = gr.Image(height=500, visible=False)
            self.image_download_btn = gr.Button("Save Image", visible=False)
            self.image_status_out_box = gr.Textbox(visible=True)

    def download_image(self, image):
        save_folder = os.path.expanduser(Path(__file__).parent.resolve() / r"images")
        file_name = util.create_unique_file_name()
        file_name = f"{file_name}.jpg"
        save_path = os.path.join(save_folder, file_name)
        logging.info(f"Save path: {save_path}")
        util.save_image(image, save_path)
        return gr.Textbox(f"Saved image as <{file_name}>", visible=True, show_label=False)

    def chat(self, kwargs):
        history = kwargs[self.chatbot]
        model_name = kwargs[self.models_dd]
        system_msg = kwargs[self.system_message_box]
        temperature = kwargs[self.temp_slider]
        yield from self.ai_manager.get_language_response(history=history, model_name=model_name,
                                                         system_msg=system_msg, temperature=temperature)

    def image(self, kwargs):
        image_prompt = kwargs[self.image_prompt_box]
        model_name = kwargs[self.image_models_dd]
        return (gr.Image(self.ai_manager.get_image_response(image_prompt, model_name, IS_TEST),
                        visible=True),
                gr.Textbox(visible=False), gr.Button(visible=True))

    @staticmethod
    def handle_retry(history, retry_data: gr.RetryData):
        new_history = history[:retry_data.index]
        previous_prompt = history[retry_data.index]
        new_history.append(previous_prompt)
        return new_history

    def get_list_of_model_names(self, provider):
        self.prev_provider = provider
        if provider == OPENAI:
            self.ai_manager = oman.OpenAi()
        elif provider == ANTHROPIC:
            self.ai_manager = aman.Anthropic()
        return gr.Dropdown(self.ai_manager.language_models,
                           value=self.ai_manager.default_language_model,
                           label="Choose model: ", interactive=True)

    def get_dates_dd(self, provider):
        dates = self.provider_dict[provider]
        dates = [d.name[:-5] for d in dates]
        dates = [util.code_dt_to_readable(d) for d in dates]
        dates = sorted(dates)
        return gr.Dropdown(dates)

    def update_providers_history_dict(self):
        self.provider_dict = util.get_history_file_names()
        providers = list(self.provider_dict.keys())
        if providers:
            prov_dd = gr.Dropdown(providers, label="Choose provider: ", value=providers[0], interactive=True)
            date_dd = self.get_dates_dd(providers[0])
        else:
            prov_dd = gr.Dropdown([], label="Choose provider: ", interactive=True)
            date_dd = gr.Dropdown([])
        return prov_dd, date_dd

    def save_chat_history(self, history):
        util.save_chat_history(history, self.prev_provider)

    @functools.lru_cache()
    def load_history(self, provider, date):
        dates = self.provider_dict[provider]
        date = util.readable_to_code_dt(date)
        date_path = [d.path for d in dates if date in d.name][0]
        with open(date_path, "r") as f:
            history = json.load(f)
        html_content = util.dict_to_markdown(history)
        return gr.Markdown(html_content)

    def ui(self):
        with gr.Blocks() as ui:
            self.language_tab()
            self.image_tab()
            self.history_tab()

            gr.on(triggers=[self.msg_box.submit, self.submit_btn.click],
                  fn=user, inputs=[self.msg_box, self.chatbot], outputs=[self.msg_box, self.chatbot], queue=False).then(
                self.chat, {self.chatbot, self.models_dd, self.system_message_box, self.temp_slider}, self.chatbot)

            self.chatbot.retry(self.handle_retry, [self.chatbot], [self.chatbot]).then(
                self.chat, {self.chatbot, self.models_dd, self.system_message_box, self.temp_slider}, self.chatbot)

            gr.on(triggers=[self.providers_dd.change, self.sys_msg_box_btn.click,
                            self.clear_btn.click, self.save_btn.click],
                  fn=self.save_chat_history, inputs=self.chatbot).then(
                self.update_providers_history_dict, outputs=[self.history_prov_dd, self.dates_dd])

            self.clear_btn.click(lambda : [], outputs=self.chatbot)

            self.providers_dd.change(lambda: [], outputs=self.chatbot).then(
                self.get_list_of_model_names, self.providers_dd, self.models_dd)
            self.sys_msg_box_btn.click(lambda: [], outputs=self.chatbot)

            self.image_submit_btn.click(lambda: gr.Image(height=500), None, self.image_out).then(
                self.image, {self.image_prompt_box, self.image_models_dd},
                [self.image_out, self.image_status_out_box, self.image_download_btn])

            self.image_download_btn.click(self.download_image, self.image_out, self.image_status_out_box)

            self.history_prov_dd.change(self.get_dates_dd, self.history_prov_dd, self.dates_dd)
            self.dates_dd.change(self.load_history, [self.history_prov_dd, self.dates_dd], self.history_out)

        return ui


def user(message, history):
    return "", history + [{"role": "user", "content": message}]



if __name__ == "__main__":
    logging.info("Starting interface")
    ui = Interface().ui()
    # ui.launch(server_name="0.0.0.0", server_port=7860)
    ui.launch()
