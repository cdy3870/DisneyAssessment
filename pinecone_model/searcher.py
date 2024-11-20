# Manages vector search queries and results in Pinecone
from typing import List, Dict
from pinecone import Pinecone
from . import utils, indexer
from FlagEmbedding import FlagReranker
import json
import random
from pprint import pprint

# Setting use_fp16 to True speeds up computation with a slight performance degradation
reranker = FlagReranker('BAAI/bge-reranker-large', use_fp16=True)

class Searcher():
	def __init__(self, index_name: str) -> None:
		self.index = indexer.connect_to_db(index_name)

	def execute_query(self, q: str, k: int = 10):
		xq = utils.embedding_model.encode(q).tolist()
		xc = self.index.query(vector=xq, top_k=k, include_metadata=True)

		return xc

def main():
	test_queries = ["offers related to pepsi"]

	k = 5
	searcher = Searcher('beta-index')


if __name__ == "__main__":
	main()