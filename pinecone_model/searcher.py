# Manages vector search queries and results in Pinecone

from pinecone import Pinecone
from . import utils, indexer
from FlagEmbedding import FlagReranker
import json
import random
from pprint import pprint

# Setting use_fp16 to True speeds up computation with a slight performance degradation
reranker = FlagReranker('BAAI/bge-reranker-large', use_fp16=True)

class Searcher():
	def __init__(self, index_name):
		self.index = indexer.connect_to_db(index_name)

	def execute_query(self, q, k=10):
		xq = utils.embedding_model.encode(q).tolist()
		xc = self.index.query(vector=xq, top_k=k, include_metadata=True)

		return xc

	def get_query_results(self, k, test_queries):
		"""
		Queries the index with the test queries and prints the results.

		Args:
			index: The Pinecone index.
			k: The number of results to return.
			test_queries: The test queries.
			query_results: A dictionary to store the query results.

		Returns:
			The query results.
		"""

		query_results = {q:[] for q in test_queries}

		for q in test_queries:
			xc = self.execute_query(q, k=k)

			for result in xc['matches']:
				print(result)
				# query_results[q].append(result['id'])
			#     print(f"{round(result['score'], 2)}: {result['id']}")
			# print("\n")

		return query_results

def main():
	"""
	The main function that queries the index, calculates MAP and NDCG scores, and saves the results to a JSON file.
	"""

	test_queries = ["offers related to pepsi"]

	k = 5
	searcher = Searcher('beta-index')
	query_results = searcher.get_query_results(k, test_queries)

	# Old evaluation code

	# k = 10

	# K = 10
	# test_samples = [t[0] for t in parsed_data]
	# map_val = utils.get_map(K, test_samples, test_queries, query_results)

	# results, average_ndcg = searcher.get_ndcg(parsed_data, query_results)

	# overall_results = {
	# 	"MAP@10": map_val,
	# 	"Average NDCG": average_ndcg
	# }

	# with open('reranked_results.json', 'w') as outfile:
	# 	json.dump({'results': results, 'overall_results': overall_results}, outfile, indent=4)


if __name__ == "__main__":
	main()