import abc

class BaseService(abc.ABC):
    @abc.abstractmethod
    def process(self, prompt: str) -> str:
        pass
