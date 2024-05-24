
class CassandraClient:
    def __init__(self, host, port, keyspace):
        self.host = host
        self.port = port
        self.keyspace = keyspace
        self.session = None
            
    def connect(self):
        from cassandra.cluster import Cluster
        cluster = Cluster([self.host], port=self.port)
        self.session = cluster.connect(self.keyspace)

    def execute(self, *args, **kwargs):
        return self.session.execute(*args, **kwargs)
    
    def close(self):
        self.session.shutdown()

    def __del__(self):
        if self.session is not None:
            self.close()
