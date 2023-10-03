import abc

class BaseService(abc.ABC):
    @abc.abstractmethod
    def get_default_model(self) -> str:
        pass

    @abc.abstractmethod
    def process(self, prompt: str) -> str:
        pass
