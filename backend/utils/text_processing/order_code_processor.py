from backend.utils.text_processing._text_processor import TextProcessor


class OrderCodeTextProcessor(TextProcessor):
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




# 6:33:32 comment_queue: automation.jobs.comment_job.comment_job({'_id': ObjectId('63466189e207cddce605d30c'), 'id': 1340, 'created_by_id': ..., {'_id': ObjectId('630f2a2e4a978a2722d68136'), 'id': 617, 'name': 'Canlian L..., 'facebook', {'_id': ObjectId('632936d0b73cc55058c5137f'), 'id': 200, 'page_id': '669953..., {'platform': 'facebook', 'id': '3388473664715801_813741523006918', 'campaig..., {'test': {'_id': ObjectId('6346760be207cddce605d3f4'), 'id': 9937, 'campaig...) (5db73f54-d984-4a2b-a0ee-9519886ec825)
# Traceback (most recent call last):
# File "/home/test/liveshowseller/./lib/error_handle/error_handler/add_or_update_by_comment_error_handler.py", line 16, in wrapper
# return func(*args, **kwargs)
# File "/home/test/liveshowseller/./lib/helper/order_helper.py", line 372, in add_or_update_by_comment
# cls.add_product_by_comment(
# File "/home/test/liveshowseller/./lib/helper/order_helper.py", line 84, in add_product_by_comment
# cls._add_product(None, pre_order, campaign_product, qty, qty_difference ,session=session)
# File "/home/test/liveshowseller/./lib/helper/order_helper.py", line 89, in _add_product
# order_product = database.lss.order_product.OrderProduct.create_object(
# File "/home/test/liveshowseller/./database/lss/_config.py", line 45, in create_object
# template['id'] = cls.__get_incremented_field(session=session)
# File "/home/test/liveshowseller/./database/lss/_config.py", line 65, in __get_incremented_field
# db['_schema_'].update_one({"name":cls.collection_name},{"$inc":{"auto.seq":1}}, session=session)
# File "/root/.cache/pypoetry/virtualenvs/liveshowseller-Iafg9aqK-py3.9/lib/python3.9/site-packages/pymongo/collection.py", line 1028, in update_one
# self._update_retryable(
# File "/root/.cache/pypoetry/virtualenvs/liveshowseller-Iafg9aqK-py3.9/lib/python3.9/site-packages/pymongo/collection.py", line 877, in _update_retryable
# return self.__database.client._retryable_write(
# File "/root/.cache/pypoetry/virtualenvs/liveshowseller-Iafg9aqK-py3.9/lib/python3.9/site-packages/pymongo/mongo_client.py", line 1552, in _retryable_write
# return self._retry_with_session(retryable, func, s, None)
# File "/root/.cache/pypoetry/virtualenvs/liveshowseller-Iafg9aqK-py3.9/lib/python3.9/site-packages/pymongo/mongo_client.py", line 1438, in _retry_with_session
# return self._retry_internal(retryable, func, session, bulk)
# File "/root/.cache/pypoetry/virtualenvs/liveshowseller-Iafg9aqK-py3.9/lib/python3.9/site-packages/pymongo/mongo_client.py", line 1470, in _retry_internal
# return func(session, sock_info, retryable)
# File "/root/.cache/pypoetry/virtualenvs/liveshowseller-Iafg9aqK-py3.9/lib/python3.9/site-packages/pymongo/collection.py", line 869, in _update
# return self._update(
# File "/root/.cache/pypoetry/virtualenvs/liveshowseller-Iafg9aqK-py3.9/lib/python3.9/site-packages/pymongo/collection.py", line 838, in _update
# result = sock_info.command(
# File "/root/.cache/pypoetry/virtualenvs/liveshowseller-Iafg9aqK-py3.9/lib/python3.9/site-packages/pymongo/pool.py", line 710, in command
# return command(self, dbname, spec, secondary_ok,
# File "/root/.cache/pypoetry/virtualenvs/liveshowseller-Iafg9aqK-py3.9/lib/python3.9/site-packages/pymongo/network.py", line 158, in command
# helpers._check_command_response(
# File "/root/.cache/pypoetry/virtualenvs/liveshowseller-Iafg9aqK-py3.9/lib/python3.9/site-packages/pymongo/helpers.py", line 167, in _check_command_response
# raise OperationFailure(errmsg, code, response, max_wire_version)
# pymongo.errors.OperationFailure: WriteConflict error: this operation conflicted with another operation. Please retry your operation or multi-document transaction., full error: {'errorLabels': ['TransientTransactionError'], 'ok': 0.0, 'errmsg': 'WriteConflict error: this operation conflicted with another operation. Please retry your operation or multi-document transaction.', 'code': 112, 'codeName': 'WriteConflict', '$clusterTime': {'clusterTime': Timestamp(1665563614, 3), 'signature': {'hash': b'Gxd4`x99xf0x1dnx8ax15xe29xfax95Gxbexb1ox19nJ', 'keyId': 7093700795052326913}}, 'operationTime': Timestamp(1665563614, 3)}