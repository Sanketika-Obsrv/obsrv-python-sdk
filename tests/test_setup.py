# import os
# import pytest
from testcontainers.postgres import PostgresContainer
from testcontainers.kafka import KafkaContainer
import yaml
# import psycopg2


# def test_create_dataset():
#     with open(os.path.join(os.path.dirname(__file__), 'config.yaml'), 'r') as config_file:
#         config = yaml.safe_load(config_file)
#         conn = psycopg2.connect(
#             host=config['postgres']['host'],
#             port=config['postgres']['port'],
#             user=config['postgres']['user'],
#             password=config['postgres']['password'],
#             dbname=config['postgres']['dbname']
#         )

#         cur = conn.cursor()
#         cur.execute("SELECT * FROM public.datasets;")
#         result = cur.fetchone()

#         assert result[0] == 'new-york-taxi-data'