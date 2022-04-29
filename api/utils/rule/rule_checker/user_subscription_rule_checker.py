from api.utils.rule.rule_checker._rule_checker import RuleChecker
from api.utils.rule.check_rule.user_subscription_check_rule import UserSubscriptionCheckRule

class CreateCampaignRuleChecker(RuleChecker):

    check_list=[
        UserSubscriptionCheckRule.is_expired,
        UserSubscriptionCheckRule.campaigns_limit,
    ]