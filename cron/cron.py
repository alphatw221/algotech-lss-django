from django_cron import CronJobBase, Schedule


class TestCronJob(CronJobBase):
    RUN_EVERY_MINS = 60
    RUN_AT_TIMES = ['10:00', ]
    RETRY_AFTER_FAILURE_MINS = 60

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS,
                        run_at_times=RUN_AT_TIMES,
                        retry_after_failure_mins=RETRY_AFTER_FAILURE_MINS)
    code = 'TestCronJob'

    def do(self):
        ret = ''

        result = 'ok'
        ret += f'result: {result}\n'

        return ret
