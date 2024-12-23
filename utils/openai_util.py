import openai
import base64
from PIL import Image
from io import BytesIO
from pathlib import Path

LANGUAGE_MODELS = ['gpt-4o-mini', 'gpt-4o', 'gpt-3.5-turbo-0125']
DEFAULT_LANGUAGE_MODEL = 'gpt-4o-mini'

IMAGE_MODELS = ["dall-e-3"]
DEFAULT_IMAGE_MODEL = "dall-e-3"

def insert_system_role(history: list[dict], system_message: str) -> list[dict]:
    if len(history) == 1:
        history.insert(0, {"role": "system", "content": system_message})
    else:
        history[0] = {"role": "system", "content": system_message}
    return history


def get_response(history: list[dict], model_name: str, system_msg: str, temperature: float):
    history = insert_system_role(history, system_msg)
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

def get_image(prompt: str, model: str):
    # image_response = openai.images.generate(
    #     model=model,
    #     prompt=prompt,
    #     size="1024x1024",
    #     n=1,
    #     response_format="b64_json",
    # )
    # image_base64 = image_response.data[0].b64_json
    # image_data = base64.b64decode(image_base64)
    # return Image.open(BytesIO(image_data))
    return Path(__file__).parent.parent.resolve() / "capybara.jpg"

def save_image(image, save_path):
    pil_image = Image.fromarray(image)
    pil_image.save(save_path)
