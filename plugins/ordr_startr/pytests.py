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
from api import models
import database


@pytest.mark.django_db(reset_sequences=True)
def test_a():
    # print("setup_class(self)：每個類之前執行一次,只執行一次")
    print('test_a')
    # print(models.campaign.campaign.Campaign.objects.filter(id=1000).first())
    # campaigns = models.campaign.campaign.Campaign.objects.all()
    # for campaign in campaigns:
    #     print(campaign)
    campaign = models.campaign.campaign.Campaign.objects.create()
    print(campaign.id)

    # print(database.lss.campaign.Campaign.filter(id=1000))


# pytestmark = pytest.mark.django_db


# @pytest.mark.django_db
# class TestProductSync(object):

#     pytestmark = pytest.mark.django_db

#     @pytest.mark.django_db
#     def setup_class(self):
#         print("setup_class(self)：每個類之前執行一次,只執行一次")
#         print(models.campaign.campaign.Campaign.objects.filter(id=1000).first())
#         # print(database.lss.campaign.Campaign.filter(id=1000))

#     def teardown_class(self):
#         print("teardown_class(self)：每個類之後執行一次,只執行一次")

#     @pytest.mark.django_db
#     def test_valid(self):
#         print("正在執行用例A")
#         x = "this"
#         assert 'h' in x

#     @pytest.mark.django_db
#     def test_invalid(self):
#         print("正在執行B")
#         assert 1 == 1
