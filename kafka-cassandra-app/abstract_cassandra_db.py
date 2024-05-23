from cassandra.cqlengine.models import Model

class CassandraDB:
    """
    Class for Cassandra DB connection and operations
    """
    def __init__(self, host:str, port:int, keyspace:str, protocol_version:int = 4):
        self.host = host
        self.port = port
        self.keyspace = keyspace
        self.protocol_version = protocol_version
        self.tables = []
        
    def connect(self):
        from cassandra.cqlengine import connection
        connection.setup([self.host], self.keyspace, port=self.port, protocol_version=self.protocol_version)
        
    def add_tables(self, table:Model|list[Model]):
        if isinstance(table, list):
            self.tables.extend(table)
        else:
            self.tables.append(table)
        
    def remove_table(self, table:Model, remove_all:bool = False):
        self.tables.remove(table)
        if remove_all:
            self.tables = []

    def insert_into_db(self, message:dict[str]):
        for table in self.tables:
            table.insert_into_table_model(message)
