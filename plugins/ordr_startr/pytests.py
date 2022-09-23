import pytest


# def setup_module():
#     print("setup_module():在模組最之前執行，且只執行一次")


# def teardown_module():
#     print("teardown_module：在模組之後執行，且只執行一次")


# def setup_function():
#     print("setup_function():每個方法之前執行")


# def teardown_function():
#     print("teardown_function():每個方法之後執行")


# def test_1():
#     print("正在執行用例1")
#     x = "this"
#     assert 'h' in x


# def test_2():
#     print("正在執行用例2")
#     assert 1 == 1

from automation.jobs.ordr_startr import export_product_job
class TestProductSync(object):

    def setup_class(self):
        print("setup_class(self)：每個類之前執行一次,只執行一次")

    def teardown_class(self):
        print("teardown_class(self)：每個類之後執行一次,只執行一次")

    def test_valid(self):
        print("正在執行用例A")
        x = "this"
        assert 'h' in x

    def test_invalid(self):
        print("正在執行B")
        assert 1 == 1
