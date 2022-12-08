from subprocess import check_call
from api_v2.rule.rule_checker.rule_checker import RuleChecker
from api_v2.rule import check_rule
class AdminCreateAccountRuleChecker(RuleChecker):
    check_list=[
        check_rule.user_check_rule.AdminCheckRule.is_role_valid_for_creation,
        check_rule.user_check_rule.UserCheckRule.is_activated_country_valid,
        check_rule.user_check_rule.UserCheckRule.is_months_valid,
        check_rule.user_check_rule.UserCheckRule.is_plan_valid,
        check_rule.user_check_rule.UserCheckRule.has_email_been_registered,
        check_rule.user_check_rule.UserCheckRule.is_timezone_valid,
    ]


class DealerCreateAccountRuleChecker(RuleChecker):

    check_list=[
        check_rule.user_check_rule.UserCheckRule.is_months_valid,
        check_rule.user_check_rule.UserCheckRule.is_activated_country_valid,
        check_rule.user_check_rule.UserCheckRule.is_plan_valid,
        check_rule.user_check_rule.UserCheckRule.has_email_been_registered,
        check_rule.user_check_rule.DealerCheckRule.is_dealer_status_valid,
        check_rule.user_check_rule.DealerCheckRule.is_dealer_license_sufficient,
    ]

class SellerChangePasswordRuleChecker(RuleChecker):

    check_list=[
        check_rule.user_check_rule.UserCheckRule.is_new_password_valid,
    ]

class SellerResetPasswordRuleChecker(RuleChecker):

    check_list=[
        check_rule.user_check_rule.UserCheckRule.is_new_password_valid,
    ]

class RegistrationPaymentCompleteChecker(RuleChecker):
    
    check_list=[
        check_rule.stripe_check_rule.StripeCheckRule.is_payment_successed,
    ]


class RegistrationDataRuleChecker(RuleChecker):

    check_list=[
        check_rule.user_check_rule.UserCheckRule.is_email_format_valid,
        check_rule.user_check_rule.UserCheckRule.has_email_been_registered,
        check_rule.stripe_check_rule.StripeCheckRule.is_period_valid,
        check_rule.stripe_check_rule.StripeCheckRule.is_promo_code_valid,
        check_rule.stripe_check_rule.StripeCheckRule.adjust_price_if_promo_code_valid,
        check_rule.stripe_check_rule.StripeCheckRule.adjust_price_if_marketing_plan, # This is a activity, if activity end, remove this rule, also remove from RegistrationRequireRefundChecker class below
    ]
class RegistrationRequireRefundChecker(RuleChecker):

    check_list=[
        check_rule.user_check_rule.UserCheckRule.is_email_format_valid,
        check_rule.user_check_rule.UserCheckRule.has_email_been_registered,
        check_rule.stripe_check_rule.StripeCheckRule.is_period_valid,
        check_rule.stripe_check_rule.StripeCheckRule.is_promo_code_valid,
        check_rule.stripe_check_rule.StripeCheckRule.adjust_price_if_promo_code_valid,
        check_rule.stripe_check_rule.StripeCheckRule.adjust_price_if_marketing_plan, # remove it if this rule is not in RegistrationDataRuleChecker class above
        check_rule.stripe_check_rule.StripeCheckRule.does_amount_match,
    ]