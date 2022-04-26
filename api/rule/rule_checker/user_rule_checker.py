from idna import check_initial_combiner
from api.rule.rule_checker.rule_checker import RuleChecker
from api.rule.check_rule.user_check_rule import UserCheckRule, AdminCheckRule, DealerCheckRule

class AdminCreateAccountRuleChecker(RuleChecker):

    check_list=[
        AdminCheckRule.is_role_valid_for_creation,
        UserCheckRule.is_activated_country_valid,
        UserCheckRule.is_months_valid,
        UserCheckRule.is_plan_valid,
        UserCheckRule.has_email_been_registered
    ]


class DealerCreateAccountRuleChecker(RuleChecker):

    check_list=[
        UserCheckRule.is_months_valid,
        UserCheckRule.is_activated_country_valid,
        UserCheckRule.is_plan_valid,
        UserCheckRule.has_email_been_registered,
        DealerCheckRule.is_dealer_status_valid,
        DealerCheckRule.is_dealer_license_sufficient,
    ]

class SellerChangePasswordRuleChecker(RuleChecker):

    check_list=[
        UserCheckRule.is_password_valid,
        UserCheckRule.is_new_password_valid,
    ]

class SellerResetPasswordRuleChecker(RuleChecker):

    check_list=[
        UserCheckRule.is_new_password_valid,
    ]