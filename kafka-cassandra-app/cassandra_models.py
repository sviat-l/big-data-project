from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model

class BaseModel(Model):
    """
    Base model for all the tables in the Cassandra DB
    """
    __abstract__ = True
    __keyspace__ = 'transactions'
    @classmethod
    def insert_into_table_model(self,  row: dict[str, str]) -> None:
        """
        Inserts a row into a table model with the columns that are present in the row and the table model
        """
        joint_columns: set[str] = row.keys() & self._defined_columns.keys()
        entry = self.create(
            **{column: row[column] for column in joint_columns})
        entry.save()

class ClientTransactions(BaseModel):
    __table_name__ = 'client_transactions'
    
    transaction_id = columns.UUID(primary_key=True)
    type = columns.Text()
    amount = columns.Decimal()
    name_orig = columns.Text()
    oldbalance_orig = columns.Text()
    newbalance_orig = columns.Text()
    name_dest = columns.Text()
    is_fraud = columns.Boolean()
    transaction_date = columns.Text()
    
    __primary_key__ = (('name_orig', 'is_fraud'), 'amount', 'transactions_id')
    __clustering_order__ = {'amount': 'DESC'}


class TransactionsByDate(BaseModel):
    __keyspace__ = 'transactions'
    __table_name__ = 'transactions_by_date'
    
    transaction_date = columns.Text(primary_key=True)
    transaction_id = columns.UUID()
    type = columns.Text()
    amount = columns.Decimal()
    name_orig = columns.Text()
    name_dest = columns.Text()
    is_fraud = columns.Boolean()
    
    __primary_key__ = (('transaction_date', 'name_dest'), 'transactions_id')
    __clustering_order__ = {'transactions_id': 'DESC'}

    