import psycopg2
from db.queries import create_schema, delete_tables, create_tables, insert_values
import pandas.io.sql as psql
import pandas as pd

class DBDriver:
    """
    A class to manage PostgreSQL database operations, including executing queries,
    setting up schemas and tables, and inserting data from CSV files.

    Attributes:
        conn (psycopg2.extensions.connection): The connection object for the database.
        curr (psycopg2.extensions.cursor): The cursor object for executing SQL queries.
    """

    def __init__(self, host: str, name: str, user: str, password: str) -> None:
        """
        Initializes the DBDriver with the specified database connection parameters.

        Args:
            host (str): The hostname or IP address of the PostgreSQL server.
            name (str): The name of the PostgreSQL database.
            user (str): The username for authentication.
            password (str): The password for authentication.
        """

        self.conn = psycopg2.connect(f"host={host} dbname={name} user={user} password={password}")
        self.curr = self.conn.cursor()


    def execute_query(self, query: str) -> None:
        """
        Executes a given SQL query and commits the transaction.

        Args:
            query (str): The SQL query to execute.

        Raises:
            Exception: If an error occurs during query execution.
        """

        self.curr.execute(query)
        self.conn.commit()


    def show_data(self) -> None:
        """
        Displays the data from a specified table in the database as a Pandas DataFrame.
        """

        dataframe = psql.read_sql("SELECT * FROM jeopardy.games", self.conn)
        print(dataframe)


    def setup(self) -> None:
        """
        Sets up the database by creating the schema, deleting existing tables, 
        creating new tables, and inserting initial data from CSV files.
        """

        self.execute_query(create_schema)
        
        for d in delete_tables:
            self.execute_query(d)

        for c in create_tables:
            self.execute_query(c)

        self.insert_from_csv('../data/categories.csv', 'coupons.categories')
        self.insert_from_csv('../data/brand_category.csv', 'coupons.brand')
        self.insert_from_csv('../data/offer_retailer.csv', 'coupons.offer')


    def escape_single_quotes(self, text: str) -> str:
        """
        Escapes single quotes in a string to prevent SQL errors.

        Args:
            text (str): The input string.

        Returns:
            str: The escaped string.
        """
        
        if isinstance(text, str):
            return text.replace("'", "''")
        return text


    def insert_from_csv(self, csv_file: str, table_name: str) -> None:
        """
        Inserts data from a CSV file into a specified database table.

        Args:
            csv_file (str): The path to the CSV file.
            table_name (str): The name of the target table.

        Raises:
            Exception: If the table name is unknown or insertion fails.
        """

        dataframe = pd.read_csv(csv_file)

        if table_name == 'coupons.categories':
            insert_query = insert_values[0]
        elif table_name == 'coupons.brand':
            insert_query = insert_values[1]
        elif table_name == 'coupons.offer':
            insert_query = insert_values[2]
        else:
            print(f"Unknown table: {table_name}")
            return

        for _, row in dataframe.iterrows():
            print(row)
            row = [self.escape_single_quotes(value) for value in row]
            formatted_query = insert_query.format(*row)
            self.execute_query(formatted_query)


def main():
    """
    The main function that initializes the DBDriver and sets up the database.

    Returns:
        DBDriver: An instance of the DBDriver class.
    """
    
    host = "localhost"
    name = "couponsdb"
    user = "calvinyu"
    password = "password"
    
    db = DBDriver(host=host, name=name, user=user, password=password)
    db.setup()

    return db


if __name__ == "__main__":
    main()
