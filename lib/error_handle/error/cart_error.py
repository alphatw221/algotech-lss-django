# from backend.cart.cart_product.request import RequestState


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
    SERVER_BUSY = 'server_busy'

class CartErrors():
        
    class CartException(Exception):
        def __init__(self, message, params={}):
            self.params = params
            self.message = message
            super().__init__(self.message)

    class UnderStock(CartException):
        state=RequestState.INSUFFICIENT_INV

    class ProductNotActivated(CartException):
        state=RequestState.INVALID_PRODUCT_NOT_ACTIVATED

    class ExceedMaxOrderAmount(CartException):
        state=RequestState.INVALID_EXCEED_MAX_ORDER_AMOUNT

    class RemoveNotAllowed(CartException):
        state=RequestState.INVALID_REMOVE_NOT_ALLOWED

    class EditNotAllowed(CartException):
        state=RequestState.INVALID_EDIT_NOT_ALLOWED

    class NegativeQty(CartException):
        state=RequestState.INVALID_NEGATIVE_QTY

    class AddZeroQty(CartException):
        state=RequestState.INVALID_ADD_ZERO_QTY

    class ServerBusy(CartException):
        state=RequestState.SERVER_BUSY