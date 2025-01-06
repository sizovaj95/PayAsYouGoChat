from PIL import Image
from datetime import datetime as dt
from pathlib import Path
import os
import json

OPENAI = "OpenAI"
ANTHROPIC = "Anthropic"

HISTORY_FOLDER = Path(__file__).parent.parent.resolve() / 'history'


def save_image(image, save_path):
    pil_image = Image.fromarray(image)
    pil_image.save(save_path)

def create_unique_file_name() -> str:
    now = dt.now()
    now_str = now.strftime("%d%m%y")
    hour, minute, second = now.hour, now.minute, now.second
    file_name = f"{now_str}_{hour}{minute}{second}"
    return file_name


def return_test_image():
    return Path(__file__).parent.parent.resolve() / "test_image.jpg"

def save_chat_history(history: list[dict], provider: str):
    if history:
        folder = HISTORY_FOLDER / provider
        if not os.path.exists(folder):
            os.mkdir(folder)
        file_name = create_unique_file_name()
        with open(folder / f"{file_name}.json", "w") as f:
            json.dump(history, f)

def get_history_file_names() -> dict:
    files_dict = {}
    for provider in os.scandir(HISTORY_FOLDER):
        files = list(os.scandir(provider.path))
        files_dict[provider.name] = files
    return files_dict

def dict_to_html(history):
    html_content = "<div style='font-family: Arial, sans-serif;'>"
    for dict_ in history:
        html_content += f"<p><strong>{dict_['role']}:</strong> {dict_['content']}</p>"
    html_content += "</div>"
    return html_content


if __name__ == "__main__":
    get_history_file_names()