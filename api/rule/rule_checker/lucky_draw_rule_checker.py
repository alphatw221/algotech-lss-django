from api.rule.check_rule.lucky_draw_check_rule import LuckyDrawCheckRule
from api.rule.rule_checker.rule_checker import RuleChecker
class LuckyDrawCreateRuleChecker(RuleChecker):

    check_list=[
        LuckyDrawCheckRule.is_draw_type_valid,
        LuckyDrawCheckRule.is_draw_prize_valid,
        LuckyDrawCheckRule.is_connected_to_any_platform
    ]
    
class LuckyDrawUpdateRuleChecker(RuleChecker):

    check_list=[
        LuckyDrawCheckRule.is_draw_type_valid,
        LuckyDrawCheckRule.is_draw_prize_valid,
        LuckyDrawCheckRule.is_connected_to_any_platform
    ]