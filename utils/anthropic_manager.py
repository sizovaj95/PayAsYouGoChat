import anthropic
import base64
from PIL import Image
from io import BytesIO

from base_class import AIManager
import util as util

LANGUAGE_MODELS = ['claude-3-5-sonnet-20241022']
DEFAULT_LANGUAGE_MODEL = 'claude-3-5-sonnet-20241022'

IMAGE_MODELS = ["dall-e-3"]
DEFAULT_IMAGE_MODEL = "dall-e-3"


class Anthropic(AIManager):
    @property
    def language_models(self):
        return LANGUAGE_MODELS

    @property
    def default_language_model(self):
        return DEFAULT_LANGUAGE_MODEL

    @property
    def image_models(self):
        return IMAGE_MODELS

    @property
    def default_image_model(self):
        return DEFAULT_IMAGE_MODEL

    def get_language_response(self, history: list[dict], model_name: str,
                              system_msg: str, temperature: float):
        client = anthropic.Anthropic()
        new_history = [{"role": hist["role"], "content": hist["content"]} for hist in history]
        new_history.append({"role": "assistant", "content": ""})
        with client.messages.stream(
                model=model_name,
                messages=new_history,
                temperature=temperature,
                max_tokens=1024,
                system=system_msg
        ) as stream:
            for text in stream.text_stream:
                new_history[-1]['content'] += text or ''
                yield new_history

    def insert_system_role(self, history: list[dict], system_message: str) ->\
            list[dict]:
        pass

    def get_image_response(self, prompt: str, model: str, is_test: bool):
        if is_test:
            return util.return_test_image()
        else:
            pass