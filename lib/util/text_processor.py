from enum import Enum, auto
from abc import ABC, abstractmethod
import string

class TextProcessor(ABC):
    @staticmethod
    @abstractmethod
    def process(text: str):
        ...

class OrderCodeTextProcessor():
    ordering_chars = set('+*Xx')
    aborting_chars = set('?')
    null_chars = set(' ')

    @classmethod
    def process(cls, text: str, order_code: str):
        if not text or not order_code:
            return None
        text = text.lower()
        text_after_order_code = cls.__get_text_after_order_code(text, order_code)
        if not text_after_order_code:
            return None

        if cls.__text_has_aborting_chars(text_after_order_code):
            return None

        return cls.__get_order_qty(text_after_order_code)

    @staticmethod
    def __get_text_after_order_code(text: str, order_code: str):
        # check if order code in text (-1 means negative)
        cursor_idx = text.find(order_code)
        if cursor_idx == -1:
            return None
        return text[cursor_idx+len(order_code):]

    @classmethod
    def __get_order_qty(cls, text: str):
        is_ordering, order_qty = False, []

        for c in text:
            if is_ordering:
                if c.isdigit():
                    order_qty.append(c)
                elif not order_qty and cls.__is_null_chars(c):
                    continue
                else:
                    break
            elif cls.__is_null_chars(c):
                continue
            elif cls.__is_ordering_chars(c):
                is_ordering = True
                continue
            else:
                break

        if not is_ordering or not order_qty:
            return None
        return int(''.join(order_qty))

    @classmethod
    def __is_ordering_chars(cls, char: str):
        return char in cls.ordering_chars

    @classmethod
    def __is_null_chars(cls, char: str):
        return char in cls.null_chars

    @classmethod
    def __text_has_aborting_chars(cls, text: str):
        return cls.__text_has_chars(text, cls.aborting_chars)

    @staticmethod
    def __text_has_chars(text: str, chars_set: set):
        return any([c in text for c in chars_set])

def remove_punctuation(text:str):
    return text.translate(str.maketrans('','',string.punctuation))

def get_bi_grams(text:str):
    return [ _tuple[0]+" "+_tuple[1] for _tuple in zip(text.split(" ")[:-1], text.split(" ")[1:])]


def get_tri_grams(text:str):
    return [ _tuple[0]+" "+_tuple[1]+" "+_tuple[2] for _tuple in zip(text.split(" ")[:-2], text.split(" ")[1:-1], text.split(" ")[2:])]