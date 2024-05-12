class Metric:
    def __init__(self, eid, ets, mid, actor, context, object, edata):
        self.eid = eid
        self.ets = ets
        self.mid = mid
        self.actor = actor
        self.context = context
        self.object = object
        self.edata = edata

    def to_json(self):
        return {
            "eid": self.eid,
            "ets": self.ets,
            "mid": self.mid,
            "actor": self.actor,
            "context": self.context.to_json(),
            "object": self.object,
            "edata": self.edata.to_json(),
        }


class MetricContext:
    def __init__(self, pdata):
        self.pdata = pdata

    def to_json(self):
        return {"pdata": self.pdata}


class MetricData:
    def __init__(self, metric, labels):
        self.metric = {k: float(v) for k, v in metric.items()}
        self.labels = labels

    def to_json(self):
        return {"metric": self.metric, "labels": self.labels}


class ExecutionMetric:
    def __init__(
        self,
        totalRecords,
        failedRecords,
        successRecords,
        connectorExecTime,
        frameworkExecTime,
        totalExecTime,
    ):
        self.totalRecords = totalRecords
        self.failedRecords = failedRecords
        self.successRecords = successRecords
        self.connectorExecTime = connectorExecTime
        self.frameworkExecTime = frameworkExecTime
        self.totalExecTime = totalExecTime

    def set(self, attr, value):
        setattr(self, attr, value)

    def to_json(self):
        return {
            "total_records_count": self.totalRecords,
            "failed_records_count": self.failedRecords,
            "success_records_count": self.successRecords,
            "total_exec_time_ms": self.totalExecTime,
            "connector_exec_time_ms": self.connectorExecTime,
            "fw_exec_time_ms": self.frameworkExecTime,
        }
