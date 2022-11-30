class RuleChecker():
    check_list=[]

    @classmethod
    def check(cls, check_list = None, **kwargs):
        _check_list = check_list if check_list else cls.check_list
        for check_rule in _check_list:
            ret = check_rule(**kwargs)
            if ret:
                kwargs.update(ret)
        return kwargs