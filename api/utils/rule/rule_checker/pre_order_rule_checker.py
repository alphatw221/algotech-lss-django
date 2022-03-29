from utils.rule.rule_checker._rule_checker import RuleChecker
from utils.rule.check_rule.pre_order_check_rule import PreOrderCheckRule


class PreOrderUpdateProductRuleChecker(RuleChecker):

    check_list=[
        PreOrderCheckRule.is_order_lock,
        PreOrderCheckRule.is_qty_valid,
        PreOrderCheckRule.campaign_product_type,
        PreOrderCheckRule.is_order_product_editable,
        PreOrderCheckRule.is_stock_avaliable
        ]