# import sys
# import logging
# import unittest
# from obsrv.connector.registry import ConnectorRegistry, ConnectorInstance

# logger = logging.getLogger()
# logger.level = logging.INFO
# logger.addHandler(logging.StreamHandler(sys.stdout))

# class TestConnectorRegistry(unittest.TestCase):
#     def setUp(self) -> None:
#         self.connector_id = '1'
#         self.connector_instance_id = 's3.new-york-taxi-data.1'
#         self.connector_registry = ConnectorRegistry()

#     def test_get_connector_instances(self):
#         connector_instances = self.connector_registry.get_connector_instances(self.connector_id)
#         self.assertIsInstance(connector_instances, list)
#         self.assertEqual(len(connector_instances), 1)

#     def test_get_connector_instance(self):
#         connector_instance = ConnectorRegistry.get_connector_instance(self.connector_instance_id)
#         self.assertIsInstance(connector_instance, ConnectorInstance)

# # if __name__ == '__main__': # pragma: no cover
# #     unittest.main()