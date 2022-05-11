from api.rule.rule_checker.rule_checker import RuleChecker
from api.rule import check_rule

class UpgradeIntentDataRuleChecker(RuleChecker):

    check_list = [
        check_rule.stripe_check_rule.StripeCheckRule.is_period_valid,
        check_rule.stripe_check_rule.StripeCheckRule.is_promo_code_valid,
    ]