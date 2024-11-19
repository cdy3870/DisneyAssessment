import psycopg2
from db.queries import create_schema, delete_tables, create_tables, insert_values
import pandas.io.sql as psql
import pandas as pd

class DBDriver:
	def __init__(self, host, name, user, password):
		self.conn = psycopg2.connect(f"host={host} dbname={name} user={user} password={password}")
		self.curr = self.conn.cursor()

	def execute_query(self, query):
		# try:
		# 	self.curr.execute(query)
		# 	self.conn.commit()  # Commit the transaction
		# 	print("Query executed successfully.")
		# except Exception as e:
		# 	print(f"Error executing query: {e}")
		# 	self.conn.rollback()  # Rollback in case of failure
		self.curr.execute(query)
		self.conn.commit()  # Commit the transaction

	def show_data(self):
		# dataframe = psql.read_sql(
		#     "SELECT * FROM jeopardy.clues", self.conn)
		dataframe = psql.read_sql(
			"SELECT * FROM jeopardy.games", self.conn)		
		print(dataframe)	

	def setup(self):
		self.execute_query(create_schema)
		
		for d in delete_tables:
			self.execute_query(d)

		for c in create_tables:
			self.execute_query(c)
			
		self.insert_from_csv('../data/categories.csv', 'coupons.categories')
		self.insert_from_csv('../data/brand_category.csv', 'coupons.brand')
		self.insert_from_csv('../data/offer_retailer.csv', 'coupons.offer')
		
	def escape_single_quotes(self, text):
		if isinstance(text, str):
			return text.replace("'", "''")
		return text
			
	def insert_from_csv(self, csv_file, table_name):
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
	host = "localhost"
	name = "couponsdb"
	user = "calvinyu"
	password = "password"
	
	db = DBDriver(host=host, name=name, user=user, password=password)
	db.setup()

	return db	

if __name__ == "__main__":
	main()