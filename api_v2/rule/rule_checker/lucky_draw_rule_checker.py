from api_v2.rule.check_rule.lucky_draw_check_rule import LuckyDrawCheckRule
from api_v2.rule.rule_checker.rule_checker import RuleChecker
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
    
class LuckyDrawStartRuleChecker(RuleChecker):

    check_list=[
        LuckyDrawCheckRule.is_draw_type_valid,
        LuckyDrawCheckRule.is_draw_prize_valid,
        LuckyDrawCheckRule.is_connected_to_any_platform,
        # LuckyDrawCheckRule.is_needed_to_start_sharedpost_crawler
    ]