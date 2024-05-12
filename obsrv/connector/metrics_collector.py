import time
import uuid
from typing import Dict, List

from obsrv.models import EventID, Metric, MetricContext, MetricData


class MetricsCollector:
    def __init__(self, ctx):
        self.metric_labels = [
            {"key": "type", "value": "Connector"},
            {"key": "job", "value": ctx.connector_id},
            {"key": "instance", "value": ctx.connector_instance_id},
            {"key": "dataset", "value": ctx.dataset_id},
        ]
        self.metric_context = MetricContext(
            pdata={"id": "Connector", "pid": ctx.connector_id}
        )
        self.metric_actor = {"id": ctx.connector_id, "type": "SYSTEM"}
        self.metric_object = {"id": ctx.dataset_id, "type": "Dataset"}

        self.metrics = []

    def collect(self, metric, value=None, addn_labels=[]):
        if isinstance(metric, str):
            self.metrics.append(self.generate({metric: value}, addn_labels))
        elif isinstance(metric, dict):
            self.metrics.append(self.generate(metric, addn_labels))

    def generate(self, metric_map: Dict, addn_labels: List):
        return Metric(
            eid=EventID.METRIC.value,
            ets=int(time.time() * 1000),
            mid=str(uuid.uuid4()),
            actor=self.metric_actor,
            context=self.metric_context,
            object=self.metric_object,
            edata=MetricData(
                metric=metric_map, labels=self.metric_labels + addn_labels
            ),
        )

    def to_seq(self):
        return [metric.to_json() for metric in self.metrics]
