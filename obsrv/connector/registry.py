import json
from dataclasses import dataclass
from typing import Optional

from obsrv.common import ObsrvException
from obsrv.models import ErrorData
from obsrv.utils import PostgresConnect


@dataclass
class ConnectorContext:
    connector_id: str
    dataset_id: str
    connector_instance_id: str
    connector_type: str
    entry_topic: Optional[str] = None
    building_block: Optional[str] = None
    env: Optional[str] = None
    state: Optional["ConnectorState"] = None
    stats: Optional["ConnectorStats"] = None


@dataclass
class ConnectorInstance:
    connector_context: ConnectorContext
    connector_config: str
    operations_config: str
    status: str


class ConnectorState:
    def __init__(self, postgres_config, connector_instance_id, state_json=None):
        self.connector_instance_id = connector_instance_id
        self.postgres_config = postgres_config
        self.state = state_json if state_json else {}

    def get_state(self, attribute, default_value=None):
        return self.state.get(attribute, default_value)

    def put_state(self, attribute, value):
        self.state[attribute] = value

    def remove_state(self, attribute):
        return self.state.pop(attribute, None)

    def contains(self, attribute):
        return attribute in self.state

    def to_json(self):
        return json.dumps(self.state, default=str)

    # @staticmethod
    def save_state(self):
        count = ConnectorRegistry.update_connector_state(
            self.connector_instance_id, self.postgres_config, self.to_json()
        )
        if count != 1:
            raise ObsrvException(
                ErrorData(
                    "CONN_STATE_SAVE_FAILED", "Unable to save the connector state"
                )
            )


class ConnectorStats:
    def __init__(self, postgres_config, connector_instance_id, stats_json=None):
        self.connector_instance_id = connector_instance_id
        self.postgres_config = postgres_config
        self.stats = stats_json if stats_json else {}

    def get_stat(self, metric, default_value=None):
        return self.stats.get(metric, default_value)

    def put_stat(self, metric, value):
        self.stats[metric] = value

    def remove_stat(self, metric):
        return self.stats.pop(metric, None)

    def to_json(self):
        return json.dumps(self.stats, default=str)

    def save_stats(self):
        upd_count = ConnectorRegistry.update_connector_stats(
            self.connector_instance_id, self.postgres_config, self.to_json()
        )
        if upd_count != 1:
            raise ObsrvException(
                ErrorData(
                    "CONN_STATS_SAVE_FAILED", "Unable to save the connector stats"
                )
            )


class ConnectorRegistry:
    @staticmethod
    def get_connector_instances(connector_id, postgres_config):
        postgres_connect = PostgresConnect(postgres_config)
        query = """
            SELECT ci.*, d.dataset_config, cr.type
            FROM connector_instances as ci
            JOIN datasets d ON ci.dataset_id = d.id
            JOIN connector_registry cr on ci.connector_id = cr.id
            WHERE ci.connector_id = '{}' AND d.status = 'Live' AND ci.status = 'Live'
        """.format(
            connector_id
        )
        result = postgres_connect.execute_select_all(query)
        return [parse_connector_instance(row, postgres_config) for row in result]

    @staticmethod
    def get_connector_instance(connector_instance_id, postgres_config):
        postgres_connect = PostgresConnect(postgres_config)
        query = """
            SELECT ci.*, cr.type, d.entry_topic
            FROM connector_instances as ci
            JOIN datasets d ON ci.dataset_id = d.id
            JOIN connector_registry cr on ci.connector_id = cr.id
            WHERE ci.id = '{}' AND d.status = 'Live' AND ci.status = 'Live'
        """.format(
            connector_instance_id
        )
        result = postgres_connect.execute_select_one(query)
        return parse_connector_instance(result, postgres_config) if result else None

    @staticmethod
    def update_connector_state(connector_instance_id, postgres_config, state):
        postgres_connect = PostgresConnect(postgres_config)
        query = """
            UPDATE connector_instances SET connector_state = '{}' WHERE id = '{}'
        """.format(
            state, connector_instance_id
        )
        return postgres_connect.execute_upsert(query)

    @staticmethod
    def update_connector_stats(connector_instance_id, postgres_config, stats):
        postgres_connect = PostgresConnect(postgres_config)
        query = """
            UPDATE connector_instances SET connector_stats = '{}' WHERE id = '{}'
        """.format(
            stats, connector_instance_id
        )
        return postgres_connect.execute_upsert(query)


def parse_connector_instance(rs, postgres_config) -> ConnectorInstance:
    id = rs["id"]
    dataset_id = rs["dataset_id"]
    connector_id = rs["connector_id"]
    connector_type = rs["type"]
    connector_config = rs["connector_config"]
    operations_config = rs["operations_config"]
    status = rs["status"]
    connector_state = rs.get("connector_state", {})
    connector_stats = rs.get("connector_stats", {})
    entry_topic = rs.get("entry_topic", "ingest")

    return ConnectorInstance(
        connector_context=ConnectorContext(
            connector_id=connector_id,
            dataset_id=dataset_id,
            connector_instance_id=id,
            connector_type=connector_type,
            entry_topic=entry_topic,
            state=ConnectorState(postgres_config, id, connector_state),
            stats=ConnectorStats(postgres_config, id, connector_stats),
        ),
        connector_config=connector_config,
        operations_config=operations_config,
        status=status,
    )
