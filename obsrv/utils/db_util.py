import psycopg2
import psycopg2.extras


class PostgresConnect:
    def __init__(self, config):
        self.config = config

    def connect(self):
        db_host = self.config.get("host")
        db_port = self.config.get("port")
        db_user = self.config.get("user")
        db_password = self.config.get("password")
        database = self.config.get("dbname")
        db_connection = psycopg2.connect(
            database=database,
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
        )
        db_connection.autocommit = True
        return db_connection

    def execute_select_one(self, sql):
        db_connection = self.connect()
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute(sql)
        result = dict(cursor.fetchone())
        db_connection.close()
        return result

    def execute_select_all(self, sql):
        db_connection = self.connect()
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute(sql)
        result = [dict(r) for r in cursor.fetchall()]
        db_connection.close()
        return result

    def execute_upsert(self, sql):
        db_connection = self.connect()
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute(sql)
        record_count = cursor.rowcount
        db_connection.close()
        return record_count
