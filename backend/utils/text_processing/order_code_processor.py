from backend.utils.text_processing._text_processor import TextProcessor


class OrderCodeTextProcessor():
    ordering_chars = set('+*Xx')
    aborting_chars = set('?')
    null_chars = set(' ')

    @staticmethod
    def process(text: str, order_code: str):
        if not text or not order_code:
            return None

        cursor_idx = OrderCodeTextProcessor._get_idx_after_order_code(
            text, order_code)
        if cursor_idx is None:
            return None

        if OrderCodeTextProcessor._text_has_aborting_chars(text[cursor_idx:]):
            return None

        return OrderCodeTextProcessor._get_order_qty(text[cursor_idx:])

    @staticmethod
    def _get_idx_after_order_code(text: str, order_code: str):
        # check if order code in text (-1 means negative)
        cursor_idx = text.find(order_code)
        if cursor_idx == -1:
            return None
        # move cursor to the char after order code
        cursor_idx += len(order_code)
        # if cursor is out of bound
        if cursor_idx >= len(text):
            return None
        return cursor_idx

    @staticmethod
    def _get_order_qty(text: str):
        order_qty, is_ordering = [], False

        for c in text:
            if is_ordering:
                if c.isdigit():
                    order_qty.append(c)
                elif not order_qty and \
                        OrderCodeTextProcessor._is_null_chars(c):
                    continue
                else:
                    break
            elif OrderCodeTextProcessor._is_null_chars(c):
                continue
            elif OrderCodeTextProcessor._is_ordering_chars(c):
                is_ordering = True
                continue
            else:
                break

        if not is_ordering or not order_qty:
            return None
        return int(''.join(order_qty))

    @staticmethod
    def _is_ordering_chars(char: str):
        return char in OrderCodeTextProcessor.ordering_chars

    @staticmethod
    def _is_null_chars(char: str):
        return char in OrderCodeTextProcessor.null_chars

    @staticmethod
    def _text_has_aborting_chars(text: str):
        return OrderCodeTextProcessor._text_has_chars(
            text, OrderCodeTextProcessor.aborting_chars)

    @staticmethod
    def _text_has_chars(text: str, chars_set: set[str]):
        return any([c in text for c in chars_set])
