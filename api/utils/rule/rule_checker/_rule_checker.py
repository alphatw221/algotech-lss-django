class RuleChecker():
    check_list=[]

    @classmethod
    def check(cls, **kwargs):

        for check_rule in cls.check_list:
            ret = check_rule(**kwargs)
            if ret:
                kwargs.update(ret)
        return kwargs