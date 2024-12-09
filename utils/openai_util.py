from openai import OpenAI

MODELS = ['gpt-4o-mini', 'gpt-4o', 'gpt-3.5-turbo-0125']
DEFAULT_MODEL = 'gpt-4o-mini'

def insert_system_role(history: list[dict], system_message: str) -> list[dict]:
    if len(history) == 1:
        history.insert(0, {"role": "system", "content": system_message})
    else:
        history[0] = {"role": "system", "content": system_message}
    return history


def get_response(history: list[dict], model_name: str, system_msg: str, temperature: float):
    history = insert_system_role(history, system_msg)
    client = OpenAI()
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
