from enum import Enum, auto

from backend.utils.text_processing._text_processor import TextProcessor


class Command(Enum):
    ORDER = auto()
    CART = auto()

    def __repr__(self):
        return self.name


class CommandTextProcessor(TextProcessor):
    @staticmethod
    def process(text: str):
        # Ignore incorrect text length before parsing to increase efficiency
        if len(text) == 4 and text.lower() == 'cart':
            return Command.CART
        if len(text) == 5 and text.lower() == 'order':
            return Command.ORDER

        return None
