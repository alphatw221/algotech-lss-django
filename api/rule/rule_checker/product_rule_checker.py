from api.rule.rule_checker.rule_checker import RuleChecker
from api.rule import check_rule




class ProductCreateRuleChecker(RuleChecker):

    check_list=[
        check_rule.product_check_rule.ProductCheckRule.is_max_order_amount_less_than_qty,
        check_rule.product_check_rule.ProductCheckRule.is_images_type_supported,
        check_rule.product_check_rule.ProductCheckRule.is_images_exceed_max_size
    ]

class ProductUpdateRuleChecker(RuleChecker):

    check_list=[
        check_rule.product_check_rule.ProductCheckRule.is_max_order_amount_less_than_qty,
        check_rule.product_check_rule.ProductCheckRule.is_images_type_supported,
        check_rule.product_check_rule.ProductCheckRule.is_images_exceed_max_size
    ]