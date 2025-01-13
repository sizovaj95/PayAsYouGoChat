from PIL import Image
from datetime import datetime as dt
from pathlib import Path
import os
import json

OPENAI = "OpenAI"
ANTHROPIC = "Anthropic"

DATE_FORMAT_SAVE = "%d%m%y"
TIME_FORMAT_SAVE = "%H%M%S"

DATE_FORMAT_READ = "%d %b %Y"
TIME_FORMAT_READ = "%H:%M:%S"

SAVE_FMT = "{}_{}"
READ_FMT = "{} {}"

HISTORY_FOLDER = Path(__file__).parent.parent.resolve() / 'history'


def save_image(image, save_path):
    pil_image = Image.fromarray(image)
    pil_image.save(save_path)

def create_unique_file_name() -> str:
    now = dt.now()
    now_date_str = now.strftime(DATE_FORMAT_SAVE)
    now_time_str = now.strftime(TIME_FORMAT_SAVE)
    file_name = f"{now_date_str}_{now_time_str}"
    return file_name


def return_test_image():
    return Path(__file__).parent.parent.resolve() / "test_image.jpg"


def test_dec(func):
    def wrapper(*args, **kwargs):
        model_name = args[0].name
        history = kwargs['history']
        res = func(*args, **kwargs)
        return res
    return wrapper

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

def dict_to_html(history: list[dict]) -> str:
    html_content = "<div style='font-family: Arial, sans-serif;'>"
    for dict_ in history:
        html_content += f"<p><strong>{dict_['role']}:</strong> {dict_['content']}</p>"
    html_content += "</div>"
    return html_content

def dict_to_markdown(history: list[dict]) -> str:
    md_content = ""
    for dict_ in history:
        if dict_['role'] == "system":
            md_content += f"_**{dict_['role']}**: {dict_['content']}_<br>"
        elif dict_['role'] == "user":
            md_content += f"<div align='right'><i><b>{dict_['role']}</b></i><br>{dict_['content']}\n</div>"
        elif dict_["role"] == "assistant":
            md_content += f"<i><b>{dict_['role']}</b></i><br>{dict_['content']}<br>"
    return md_content

def code_dt_to_readable(date_str: str) -> str:
    as_dt = dt.strptime(date_str, SAVE_FMT.format(DATE_FORMAT_SAVE, TIME_FORMAT_SAVE))
    converted = as_dt.strftime(READ_FMT.format(DATE_FORMAT_READ, TIME_FORMAT_READ))
    return converted

def readable_to_code_dt(date_str: str) -> str:
    as_dt = dt.strptime(date_str, READ_FMT.format(DATE_FORMAT_READ, TIME_FORMAT_READ))
    converted = as_dt.strftime(SAVE_FMT.format(DATE_FORMAT_SAVE, TIME_FORMAT_SAVE))
    return converted


if __name__ == "__main__":
    code_dt_to_readable("090125_182818")