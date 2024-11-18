import numpy as np
import random 
import os
from sentence_transformers import SentenceTransformer
import torch

# initialize connection to pinecone (get API key at app.pinecone.io)
api_key = os.environ.get('PINECONE_API_KEY')

params = {"sim_mets": ["l2", "cosine", "dot_product"],
     "search_algo": ["exhaustive", "beam", "hierarchical"],
     "index_algo": ["flat", "hierarchical_navigable_small_world_graph", "annoy", "faiss", "ball_tree", "kd_tree"]}

cloud = os.environ.get('PINECONE_CLOUD') or 'aws'
region = os.environ.get('PINECONE_REGION') or 'us-east-1'

device = 'cuda' if torch.cuda.is_available() else 'cpu'
embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2', device=device)

def is_relevant(df, query, data_point, threshold=3):
    relevance = df[(df["query"] == query) & (df["doc"] == data_point)]["relevance"].tolist()
    if len(relevance) > 0:
      relevance = relevance[0]
    else:
      return 0
    if relevance >= threshold:
      return 1
    return 0

def ndcg_score(relevance, K):
  """Calculates the Normalized Discounted Cumulative Gain (NDCG) at rank K.

  Args:
      relevance: A list of relevance scores.
      K: The rank position to evaluate.

  Returns:
      The NDCG@K score.
  """  
  relevance = [len(relevance) - i - 1 for i in relevance]

  # print(relevance)
    
  # Calculate Discounted Cumulative Gain (DCG)
  DCG = sum([rel / np.log2(i + 2) for i, rel in enumerate(relevance[:K])])

  # Calculate Ideal Discounted Cumulative Gain (IDCG) by sorting ideal ranking
  ideal_relevance = sorted(relevance, reverse=True)
  IDCG = sum([rel / np.log2(i + 2) for i, rel in enumerate(ideal_relevance[:K])])

  # Avoid division by zero
  if IDCG == 0:
     return 0

  return DCG / IDCG 

def apk(actual, predicted, k=10):
    if not actual:
        return 0.0

    if len(predicted)>k:
        predicted = predicted[:k]

    score = 0.0
    num_hits = 0.0

    for i,p in enumerate(predicted):
        # first condition checks whether it is valid prediction
        # second condition checks if prediction is not repeated
        if p in actual and p not in predicted[:i]:
            num_hits += 1.0
            score += num_hits / (i+1.0)

    return score / min(len(actual), k)

def mapk(actual, predicted, k=10):
    return np.mean([apk(a,p,k) for a,p in zip(actual, predicted)])


def get_map(K, test_samples, test_queries, query_results, df):
    actual = []
    predicted = []
    retrieved_results = list(query_results.values())

    for query, results in zip(test_queries, retrieved_results):
      relevant_items = [test_samples.index(doc) for doc in results if is_relevant(df, query, doc)]
      actual.append(relevant_items)
      
      predicted_items = [test_samples.index(doc) for doc in results[:K]]
      predicted.append(predicted_items)

    map = mapk(actual, predicted, K)

    return map


# def get_ndcg(self, parsed_data, query_results):
#   """
#   Calculates the Normalized Discounted Cumulative Gain (NDCG) scores.

#   Args:
#     query_results: The query results.

#   Returns:
#     A dictionary containing the ranked results and NDCG scores, and the average NDCG score.
#   """
#   # Dummy representation of NDCG, relevance ranking determined randomly
#   results = {}
#   ndcg_scores = []

#   temp_data = {d[0]:d for d in parsed_data}

#   for query, items in query_results.items():
#     temp_dict = {}
#     for item in items:
#       temp_dict[item] = reranker.compute_score([query, item])
#     sorted_results = dict(sorted(temp_dict.items(), key=lambda x: x[1], reverse=True))

#     ground_truth_relevance = list(range(0, len(items)))
#     random.shuffle(ground_truth_relevance)

#     ndcg_value = utils.ndcg_score(ground_truth_relevance, K=len(items))
#     ndcg_scores.append(ndcg_value)
    
#     ranked_results = [{"id":k, "rr score": v, "experience": temp_data[k][2]["experience"]}
#               for i, (k, v) in enumerate(sorted_results.items())]
    
#     results[id(query)] = {
#       "Query": query,
#       "Ranked Results": ranked_results,
#       "NDCG Score": ndcg_value
#     }

#   average_ndcg = sum(ndcg_scores) / len(ndcg_scores)

#   return results, average_ndcg