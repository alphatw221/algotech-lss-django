from backend.utils.common.text_processing._text_processor import TextProcessor


class OrderCodeTextProcessor(TextProcessor):
    def process(text: str, order_code: str):
        if not order_code:
            return None

        # TODO: complete the function

        return 1


#! deprecated
def order_qty_in_comment(comment, order_code):
    porduct_name_index = comment.find(order_code)
    if porduct_name_index == -1:  # -1 means no match
        return None

    # If product_name is in the comment, calculate the amount
    order_amount = ""
    # We find the closest consecutive digits after product_name in the string
    begin_index = porduct_name_index + len(order_code)
    # Scan rest of the string for exception rules
    for char_index in range(begin_index, len(comment)):
        # If there's a "?" after order code, the order doesn't count
        if comment[char_index] == "?":
            return None

    plus_one_chars = set('+*Xx')
    having_plus_one_char = False
    # Find the first index that is a digit
    first_digit_index = len(comment)
    for char_index in range(begin_index, len(comment)):
        if having_plus_one_char:
            # Find the first digit
            if comment[char_index].isdigit():
                first_digit_index = char_index
                break
        else:
            if comment[char_index] in plus_one_chars:
                having_plus_one_char = True
            elif comment[char_index] == ' ':
                pass
            else:
                return None

    # Check the remaining char after order code
    for char_index in range(first_digit_index, len(comment)):
        if comment[char_index].isdigit():
            order_amount += comment[char_index]
        elif not order_amount:
            continue
        else:
            break

#    # If there's none, we find the closest consecutive digits before product_name
#    if not order_amount:
#         begin_index = porduct_name_index
#         for char_index in reversed(range(0, begin_index)):
#             if comment[char_index].isdigit():
#                 order_amount = comment[char_index] + order_amount
#             elif not order_amount:
#                 continue
#             else:
#                 break

    if not order_amount:
        return None
    return int(order_amount)
