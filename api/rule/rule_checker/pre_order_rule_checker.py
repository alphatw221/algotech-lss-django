from api.rule.check_rule.order_product_check_rule import OrderProductCheckRule
from api.rule.check_rule.pre_order_check_rule import PreOrderCheckRule
from api.rule.rule_checker.rule_checker import RuleChecker

class PreOrderUpdateProductRuleChecker(RuleChecker):

    check_list=[
        PreOrderCheckRule.is_campaign_product_exist,
        PreOrderCheckRule.is_order_lock,
        PreOrderCheckRule.is_qty_valid,
        PreOrderCheckRule.campaign_product_type,
        PreOrderCheckRule.is_order_product_editable,
        PreOrderCheckRule.is_stock_avaliable,
        PreOrderCheckRule.is_under_max_limit,
        ]

class PreOrderAddProductRuleChecker(RuleChecker):

    check_list=[
        PreOrderCheckRule.is_campaign_product_exist,
        PreOrderCheckRule.is_order_lock,
        PreOrderCheckRule.is_qty_valid,
        PreOrderCheckRule.is_order_product_addable,
        PreOrderCheckRule.campaign_product_type,
        PreOrderCheckRule.is_stock_avaliable,
        PreOrderCheckRule.is_under_max_limit,
        ]

class PreOrderDeleteProductRuleChecker(RuleChecker):

    check_list=[
        PreOrderCheckRule.is_order_lock,
        PreOrderCheckRule.is_order_product_removeable
    ]

class PreOrderCheckoutRuleChecker(RuleChecker):

    check_list=[
        PreOrderCheckRule.allow_checkout,
        PreOrderCheckRule.is_order_lock,
        PreOrderCheckRule.is_order_empty
    ]

class OrderProductCheckoutRuleChecker(RuleChecker):

    check_list=[
        OrderProductCheckRule.is_stock_avaliable_for_checkout
    ]    