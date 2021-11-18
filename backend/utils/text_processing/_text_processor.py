from abc import ABC, abstractmethod


class TextProcessor(ABC):
    @staticmethod
    @abstractmethod
    def process(text: str):
        ...
