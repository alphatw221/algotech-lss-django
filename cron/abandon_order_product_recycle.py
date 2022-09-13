from django_cron import CronJobBase, Schedule
import database
import lib
import traceback
from datetime import datetime, timedelta
class AbandonOrderProductRecycleCronJob(CronJobBase):
    RUN_EVERY_MINS = 10
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS,)
    code = 'abandon_order_product_recycle_cron_job'


    def do(self):
        campaign_products = database.lss.campaign.get_ongoing_campaign_disallow_overbook_campaign_product()

        for campaign_product in campaign_products:
            campaign_product_id = campaign_product.get('id')
            
            pre_orders = database.lss.pre_order.get_abandon_pre_order_which_contain_campaign_product(campaign_product_id,havent_updated_in=timedelta(minutes=10))

            for pre_order in pre_orders:
                pre_order_id=pre_order.get('id')
                try:
                    lib.helper.order_helper.PreOrderHelper.delete_product_by_comment(pre_order_id, campaign_product_id)
                except Exception:
                    
                    print(traceback.format_exc())
                    continue

