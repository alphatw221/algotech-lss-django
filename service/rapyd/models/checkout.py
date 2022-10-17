from typing import Optional
from pydantic import BaseModel


class CreateCheckoutModel(BaseModel):
    amount: float
    country: str
    currency: str
    customer: Optional[str] = ""
    complete_checkout_url: Optional[str] = ""
    cancel_checkout_url: Optional[str] = ""
    requested_currency: Optional[str] = ""
    fixed_side: Optional[str] = None
    custom_elements: Optional[dict] = {}
    payment_method_type_categories: Optional[list] =[]
    metadata: Optional[dict] = {}
    complete_payment_url: Optional[str] = ""
    error_payment_url: Optional[str] = ""
    

class CheckoutModel(BaseModel):
    id: str
    redirect_url: str
    