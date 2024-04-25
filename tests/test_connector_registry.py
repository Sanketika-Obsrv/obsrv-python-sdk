import unittest
import pytest
import os
import yaml
from obsrv.connector.registry import ConnectorRegistry, ConnectorInstance

from tests.batch_setup import setup_obsrv_database

@pytest.mark.usefixtures("setup_obsrv_database")
class TestConnectorRegistry(unittest.TestCase):
    def setUp(self) -> None:
        self.connector_id = 'test.1'
        self.connector_instance_id = 'test.new-york-taxi-data.1'
        self.connector_registry = ConnectorRegistry()

        with open(os.path.join(os.path.dirname(__file__), 'config/config.yaml')) as config_file:
            config = yaml.safe_load(config_file)
            self.postgres_config = config['postgres']

    def test_get_connector_instances(self):
        connector_instances = self.connector_registry.get_connector_instances(self.connector_id, self.postgres_config)
        self.assertIsInstance(connector_instances, list)
        self.assertEqual(len(connector_instances), 1)

    def test_get_connector_instance(self):
        connector_instance = ConnectorRegistry.get_connector_instance(self.connector_instance_id, self.postgres_config)
        self.assertIsInstance(connector_instance, ConnectorInstance)
