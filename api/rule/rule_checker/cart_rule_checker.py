from api.rule.check_rule.cart_check_rule import CartCheckRule
from api.rule.rule_checker.rule_checker import RuleChecker

class CartEditProductRuleChecker(RuleChecker):

    check_list=[
        CartCheckRule.is_campaign_product_exist,
        CartCheckRule.is_cart_lock,
        CartCheckRule.is_qty_valid,
        CartCheckRule.is_campaign_product_editable,
        CartCheckRule.is_stock_avaliable,
        CartCheckRule.is_under_max_limit,
        ]

class CartDeleteProductRuleChecker(RuleChecker):

    check_list=[
        
        CartCheckRule.is_cart_lock,
        CartCheckRule.is_campaign_product_removeable
    ]

class CartCheckoutRuleChecker(RuleChecker):

    check_list=[
        CartCheckRule.allow_checkout,
        CartCheckRule.is_cart_lock,
        CartCheckRule.is_cart_empty
    ]

