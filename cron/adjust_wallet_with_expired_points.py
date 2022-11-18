import django

from django_cron import CronJobBase, Schedule

import database
import service

from api import models
import lib
from datetime import datetime, timedelta

class AdjustWalletWithExpiredPointsCronJob(CronJobBase):

    RUN_AT_TIMES = ['00:00', ]


    schedule = Schedule(
                        # run_every_mins=RUN_EVERY_MINS,
                        run_at_times=RUN_AT_TIMES,
                        # retry_after_failure_mins=RETRY_AFTER_FAILURE_MINS
                        )
    code = 'adjust_wallet_with_expired_points'
    ALLOW_PARALLEL_RUNS = True

    def do(self):
        end_at = datetime.utcnow()
        start_from = end_at - timedelta(days=1)
        
        lib.helper.wallet_helper.WalletHelper.adjust_all_wallet_with_expired_points(start_from=start_from, end_at=end_at)
