from google.cloud import monitoring_v3
from  django.conf import settings

from google.api import metric_pb2 as ga_metric

import time

client = monitoring_v3.MetricServiceClient(credentials=settings.GS_CREDENTIALS)

class CommentQueueLengthMetric():

    redis_depth_metric_type = "custom.googleapis.com/lss_redis_comment_queue_length"
    project_name="projects/" + settings.GCP_PROJECT_ID

    @classmethod
    def create_metric_descriptor(cls):
        descriptor = ga_metric.MetricDescriptor()
        descriptor.type = cls.redis_depth_metric_type
        descriptor.metric_kind = ga_metric.MetricDescriptor.MetricKind.GAUGE
        descriptor.value_type = ga_metric.MetricDescriptor.ValueType.INT64
        descriptor.description = "This is a redis queue length custom metric."
        client.create_metric_descriptor(name=cls.project_name, metric_descriptor=descriptor)

    @classmethod
    def write_time_series(cls, value):

        series = monitoring_v3.TimeSeries()
        series.metric.type = cls.redis_depth_metric_type
        series.resource.type = "global"
        now = time.time()
        seconds = int(now)
        nanos = int((now - seconds) * 10 ** 9)
        interval = monitoring_v3.TimeInterval(
            {"end_time": {"seconds": seconds, "nanos": nanos}}
        )
        point = monitoring_v3.Point({"interval": interval, "value": {"int64_value": value}})
        series.points = [point]
        client.create_time_series(name=cls.project_name, time_series=[series])

    @classmethod
    def delete_metric_descriptor(cls):
        client.delete_metric_descriptor(name=f"{cls.project_name}/metricDescriptors/{cls.redis_depth_metric_type}")