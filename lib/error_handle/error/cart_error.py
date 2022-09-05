from backend.cart.cart_product.request import RequestState

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