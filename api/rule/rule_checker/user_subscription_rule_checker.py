from api.rule.check_rule.user_subscription_check_rule import UserSubscriptionCheckRule
from api.rule.rule_checker.rule_checker import RuleChecker
from api.rule import check_rule

class UpgradeIntentDataRuleChecker(RuleChecker):

    check_list = [
        check_rule.stripe_check_rule.StripeCheckRule.is_upgrade_plan_valid,
        check_rule.stripe_check_rule.StripeCheckRule.is_period_valid,
        check_rule.stripe_check_rule.StripeCheckRule.is_promo_code_valid,
        check_rule.stripe_check_rule.StripeCheckRule.adjust_price_if_promo_code_valid,
        check_rule.stripe_check_rule.StripeCheckRule.adjust_amount_if_subscription_undue,
        check_rule.stripe_check_rule.StripeCheckRule.adjust_price_if_welcome_gift_not_used,
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
        check_rule.stripe_check_rule.StripeCheckRule.adjust_price_if_promo_code_valid,
        check_rule.stripe_check_rule.StripeCheckRule.adjust_amount_if_subscription_undue,
        check_rule.stripe_check_rule.StripeCheckRule.adjust_price_if_welcome_gift_not_used,
        check_rule.stripe_check_rule.StripeCheckRule.does_amount_match,
    ]

class CreateCampaignRuleChecker(RuleChecker):

    check_list=[
        UserSubscriptionCheckRule.is_expired,
        UserSubscriptionCheckRule.campaign_end_time_over_subscription_period,
        UserSubscriptionCheckRule.max_concurrent_live,
        UserSubscriptionCheckRule.campaign_limit,
    ]

class UpdateCampaignRuleChecker(RuleChecker):
    check_list=[
        UserSubscriptionCheckRule.is_expired,
        UserSubscriptionCheckRule.campaign_end_time_over_subscription_period,
        UserSubscriptionCheckRule.max_concurrent_live,
        UserSubscriptionCheckRule.campaign_limit,
    ]
