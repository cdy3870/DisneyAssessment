import numpy as np
import random 
import os
from sentence_transformers import SentenceTransformer
import torch

api_key = os.environ.get('PINECONE_API_KEY') or "2eb88fd4-ee3f-47ef-97b9-08a2cb42528e"

params = {"sim_mets": ["l2", "cosine", "dot_product"],
     "search_algo": ["exhaustive", "beam", "hierarchical"],
     "index_algo": ["flat", "hierarchical_navigable_small_world_graph", "annoy", "faiss", "ball_tree", "kd_tree"]}

cloud = os.environ.get('PINECONE_CLOUD') or 'aws'
region = os.environ.get('PINECONE_REGION') or 'us-east-1'

device = 'cuda' if torch.cuda.is_available() else 'cpu'
embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2', device=device)