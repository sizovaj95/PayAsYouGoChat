from abc import ABC, abstractmethod


class AIManager(ABC):
    name: str

    def __repr__(self):
        return self.name

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
