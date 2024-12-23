from abc import ABC, abstractmethod


class AIManager(ABC):

    # def __init__(self, language_models: list[str], default_lm: str,
    #              image_models: list[str], default_im: str):
    #     self.language_models = language_models
    #     self.default_language_model = default_lm
    #     self.image_models = image_models
    #     self.default_image_model = default_im

    @property
    @abstractmethod
    def language_models(self):
        pass

    @property
    @abstractmethod
    def default_language_model(self):
        pass

    @property
    @abstractmethod
    def image_models(self):
        pass

    @property
    @abstractmethod
    def default_image_model(self):
        pass

    @abstractmethod
    def get_language_response(self, history: list[dict], model_name: str,
                              system_msg: str, temperature: float):
        pass

    @abstractmethod
    def get_image_response(self, prompt: str, model: str, is_test: bool):
        pass

    @abstractmethod
    def insert_system_role(self, history: list[dict], system_message: str):
        if len(history) == 1:
            history.insert(0, {"role": "system", "content": system_message})
        else:
            history[0] = {"role": "system", "content": system_message}
        return history
