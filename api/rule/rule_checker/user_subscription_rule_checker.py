from api.rule.rule_checker.rule_checker import RuleChecker
from api.rule import check_rule

class UpgradeIntentDataRuleChecker(RuleChecker):

    check_list = [
        check_rule.stripe_check_rule.StripeCheckRule.is_upgrade_plan_valid,
        check_rule.stripe_check_rule.StripeCheckRule.is_period_valid,
        check_rule.stripe_check_rule.StripeCheckRule.is_promo_code_valid,
        check_rule.stripe_check_rule.StripeCheckRule.adjust_price_if_promo_code_valid,
    ]

class UpgradePaymentCompleteChecker(RuleChecker):
    
    check_list=[
        check_rule.stripe_check_rule.StripeCheckRule.is_payment_successed,
    ]

class UpgradeRequireRefundChecker(RuleChecker):

    check_list=[
        check_rule.stripe_check_rule.StripeCheckRule.is_upgrade_plan_valid,
        check_rule.stripe_check_rule.StripeCheckRule.is_period_valid,
        check_rule.stripe_check_rule.StripeCheckRule.is_promo_code_valid,
        check_rule.stripe_check_rule.StripeCheckRule.does_amount_match,
    ]