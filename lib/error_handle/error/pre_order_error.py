
from backend.cart.cart_product.request import RequestState

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