import openai
import base64
from PIL import Image
from io import BytesIO

from base_class import AIManager
import util as util

LANGUAGE_MODELS = ['gpt-4o-mini', 'gpt-4o', 'gpt-3.5-turbo-0125']
DEFAULT_LANGUAGE_MODEL = 'gpt-4o-mini'

IMAGE_MODELS = ["dall-e-3"]
DEFAULT_IMAGE_MODEL = "dall-e-3"


class OpenAi(AIManager):
    name = util.OPENAI

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

    @util.test_dec
    def get_language_response(self, history: list[dict], model_name: str,
                              system_msg: str, temperature: float):
        history = self.insert_system_role(history, system_msg)
        client = openai.OpenAI()
        stream = client.chat.completions.create(
            model=model_name,
            messages=history,
            stream=True,
            temperature=temperature
        )
        history.append({"role": "assistant", "content": ""})
        for chunk in stream:
            history[-1]['content'] += chunk.choices[0].delta.content or ''
            yield history

    @staticmethod
    def insert_system_role(history: list[dict], system_message: str) ->\
            list[dict]:
        if len(history) == 1:
            history.insert(0, {"role": "system", "content": system_message})
        else:
            history[0] = {"role": "system", "content": system_message}
        return history

    def get_image_response(self, prompt: str, model: str, is_test: bool):
        if is_test:
            return util.return_test_image()
        else:
            image_response = openai.images.generate(
                model=model,
                prompt=prompt,
                size="1024x1024",
                n=1,
                response_format="b64_json",
            )
            image_base64 = image_response.data[0].b64_json
            image_data = base64.b64decode(image_base64)
            return Image.open(BytesIO(image_data))
