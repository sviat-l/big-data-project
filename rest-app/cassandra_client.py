
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
            
    def get_customer_reviews(self, customer_id):
        query = (f"SELECT "
                 f"*"
                 f" FROM {self.keyspace}.customers_reviews WHERE customer_id='{customer_id}'")
        result= self.execute(query).all()
        return result
    
    def get_product_reviews(self, product_id, star_rating=None):
        query = (f"SELECT "
                 f"*"
                 f" FROM {self.keyspace}.products_reviews WHERE product_id='{product_id}'" +
                 (f" AND star_rating={star_rating}" if star_rating is not None else
                 f" AND star_rating IN (1,2,3,4,5)")
                 )
        result= self.execute(query).all()
        return result
    
    def get_products_reviwed_at_date(self, date):
        query = (f"SELECT "
                 f"*"
                 f" FROM {self.keyspace}.products_reviews_on_date WHERE review_date='{date}'")
        result = self.execute(query).all()
        return result
    
    def get_clients_reviewing_at_date(self, date, verified_only=False, star_rating_range=(1,2,3,4,5)):
        query = (f"SELECT "
                 f"*"
                 f" FROM {self.keyspace}.customers_reviews_on_date WHERE review_date='{date}'"
                 f" AND verified_purchase " + ("=True" if verified_only else "IN (True, False)") +
                 f" AND star_rating IN {star_rating_range}")
        result = self.execute(query).all()
        return result

