
# from backend.cart.cart_product.request import RequestState
# from lib.helper.order_helper import RequestState

class RequestState():
    INIT = 'init'
    ADDING = 'adding'
    ADDED = 'added'
    UPDATING = 'updating'
    UPDATED = 'updated'
    DELETING = 'deleting'
    DELETED = 'deleted'
    INSUFFICIENT_INV = 'insufficient_inv'
    INVALID_PRODUCT_NOT_ACTIVATED = 'invalid_product_not_activated'
    INVALID_EXCEED_MAX_ORDER_AMOUNT = 'invalid_exceed_max_order_amount'
    INVALID_REMOVE_NOT_ALLOWED = 'invalid_remove_not_allowed'
    INVALID_EDIT_NOT_ALLOWED = 'invalid_edit_not_allowed'
    INVALID_NEGATIVE_QTY = 'invalid_negative_qty'
    INVALID_ADD_ZERO_QTY = 'invalid_add_zero_qty'
    INVALID_UNKNOWN_REQUEST = 'invalid_unknown_request'


class PreOrderErrors():

    class PreOrderException(Exception):
        pass

    class UnderStock(PreOrderException):
        state=RequestState.INSUFFICIENT_INV

    class ProductNotActivated(PreOrderException):
        state=RequestState.INVALID_PRODUCT_NOT_ACTIVATED

    class ExceedMaxOrderAmount(PreOrderException):
        state=RequestState.INVALID_EXCEED_MAX_ORDER_AMOUNT

    class RemoveNotAllowed(PreOrderException):
        state=RequestState.INVALID_REMOVE_NOT_ALLOWED

    class EditNotAllowed(PreOrderException):
        state=RequestState.INVALID_EDIT_NOT_ALLOWED

    class NegativeQty(PreOrderException):
        state=RequestState.INVALID_NEGATIVE_QTY

    class AddZeroQty(PreOrderException):
        state=RequestState.INVALID_ADD_ZERO_QTY