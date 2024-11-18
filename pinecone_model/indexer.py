# Manages vector indexing in Pinecone

from pinecone import Pinecone
from pinecone import ServerlessSpec
import time
from . import utils
import json
import pandas as pd

class PineCone():
	def __init__(self, index_name):
		"""
		Initializes the Pinecone client and creates an index if it doesn't exist.

		Args:
			index_name: The specific index used.

		Returns:
			The Pinecone index.
		"""
		pc = Pinecone(api_key=utils.api_key,
					  similarity_metric=utils.params["sim_mets"][0],
					  search_algorithm=utils.params["search_algo"][0])
		
		spec = ServerlessSpec(cloud=utils.cloud, region=utils.region)

		existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]

		# check if index already exists (it shouldn't if this is first time)
		if index_name not in existing_indexes:
			# if does not exist, create index
			pc.create_index(index_name,
							dimension=384,  # dimensionality of minilm
							metric='dotproduct',
							spec=spec)
			# wait for index to be initialized
			while not pc.describe_index(index_name).status['ready']:
				time.sleep(1)

		self.index = pc.Index(index_name, algorithm=utils.params["index_algo"][0])


	def create_embeddings(self, test_data):
		"""
		Creates embeddings for the test data using the embedding model.

		Args:
			test_data: The test data to create embeddings for.

		Returns:
			The test data with embeddings added.
		"""

		for d in test_data:
			d[1] = utils.embedding_model.encode(d[1]).tolist()
			d[2] = {"Categories": d[2]}
			d = tuple(d)

		data = [tuple(d) for d in test_data]

		return data

	def upsert_embeddings(self, embeddings):
		"""
		Upserts embeddings into the vector db.
		"""

		self.index.upsert(embeddings)

def connect_to_db(index_name):
	"""
	Connects to the vector db with a specified index.

	Args:
		index_name: The specific index used.

	Returns:
		The index to query from.
	"""

	pc = Pinecone(api_key=utils.api_key,
				  similarity_metric=utils.params["sim_mets"][0],
				  search_algorithm=utils.params["search_algo"][0])

	index = pc.Index(index_name, algorithm=utils.params["index_algo"][0])

	return index

def parse_data(data):
	"""
	Extracts experiences and skills to create a string that will be embedded. Also
	included is the metadata for each resume.

	Returns:
		The parsed data.
	"""


	
	parsed_data = data.applymap(str).values.tolist()





	return parsed_data

# def parse_data_test(data):
# 	parsed_data = []
# 	docs = data[["doc_id", "doc"]].drop_duplicates().dropna()
# 	for index, row in docs.iterrows():
# 		parsed_data.append([str(row["doc_id"]), [], {"experience": row["doc"]}])

# 	return parsed_data




def main():
	"""
	The main function that initializes the Pinecone client, creates embeddings, and upserts them into the index.
	"""

	# Store actual data
	data = pd.read_csv("../data/processed_offers.csv")
	# print(data)
	parsed_data = parse_data(data)
	# print(parsed_data)

	pc = PineCone(index_name = 'beta-index')
	embeddings = pc.create_embeddings(parsed_data)
	# print(embeddings)
	pc.upsert_embeddings(embeddings)

	
if __name__ == "__main__":
	main()