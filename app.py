import streamlit as st
import pandas as pd
import sys
import time
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from pinecone_model import searcher as pine_searcher
import json
from langchain_groq import ChatGroq
from db import db_setup, queries
import pandas.io.sql as psql
import psycopg2
from typing import Tuple, Dict, List
import os

st.set_page_config(layout="wide") 

llm = ChatGroq(model="llama3-70b-8192", api_key=os.environ.get('LLAMA_KEY'))

def connect_to_db(host: str, name: str, user: str, password: str) -> Tuple[psycopg2.extensions.connection, psycopg2.extensions.cursor]:
	"""
	Connects to a PostgreSQL database.

	Args:
		host (str): The database host.
		name (str): The database name.
		user (str): The username for authentication.
		password (str): The password for authentication.

	Returns:
		Tuple[psycopg2.extensions.connection, psycopg2.extensions.cursor]: A connection object and a cursor object.
	"""
	
	conn = psycopg2.connect(f"host={host} dbname={name} user={user} password={password}")
	curr = conn.cursor()

	return conn, curr

def parse_pine(results: Dict) -> List[str]:
	"""
	Parses Pinecone search results to extract IDs and metadata.

	Args:
		results (Dict): The results returned from a Pinecone query.

	Returns:
		List[str]: A list of extracted IDs from the results.
	"""
	
	table_data = []
	ids = []

	for i, result in enumerate(results['matches'], start=1):
		ids.append(result['id'])
		result_data = {
			"ID": result['id'],
			"metadata": result['metadata']["Categories"],
			"score": result['score']
		}
		table_data.append(result_data)		

	return ids


def convert_to_df(ids: List[str], data: pd.DataFrame) -> pd.DataFrame:
	"""
	Converts Pinecone IDs to a DataFrame with corresponding offers and categories.

	Args:
		ids (List[str]): The list of IDs to convert.
		data (pd.DataFrame): The dataset to match IDs with offers and categories.

	Returns:
		pd.DataFrame: A DataFrame containing IDs, offers, and categories.
	"""
	categories = []
	offers = []
	for id in ids:
		offers.append(data[data["UNIQUE_ID"] == id]["OFFER"].values[0])
		categories.append(data[data["UNIQUE_ID"] == id]["CATEGORY"].values[0])

	df = pd.DataFrame({'ids': ids, 'offers': offers, "categories": categories})

	return df


def execute_search(query: str, k: int) -> Tuple[float, Dict]:
	"""
	Executes a search query using the Pinecone model.

	Args:
		query (str): The search query.
		k (int): The number of results to return.

	Returns:
		Tuple[float, Dict]: The execution time and search results.
	"""
	
	s = st.session_state.pinecone_object

	start_time = time.time()
	res = s.execute_query(query, k=k)

	execution_time = time.time() - start_time

	return execution_time, res


@st.cache_data
def get_data() -> pd.DataFrame:
	"""
	Loads the processed offers data and caches data for efficiency.

	Returns:
		pd.DataFrame: The processed offers data.
	"""
	
	data = pd.read_csv('data/processed_offers.csv')
	return data


def perform_rag(df: pd.DataFrame) -> str:
	"""
	Performs retrieval-augmented generation (RAG) using the extracted categories.

	Args:
		df (pd.DataFrame): The DataFrame containing categories.

	Returns:
		str: The generated recommendations based on categories.
	"""
	
	categories = list(df["categories"])
	parsed_cats = set()
	for full_cat in categories:
		full_cat = full_cat.replace("{", "").replace("}", "")
		full_cat = full_cat.split(", ")
		for c in full_cat:
			parsed_cats.add(c)
		
	cat_str = ", ".join(parsed_cats)

	prompt = """
	Given these categories of items:

	{CAT_STR}

	Could you provide recommendations of items to purchase and where to find them?
	Provide your response in the following format:

	Category 1 name: \n
	Recommendation: \n
	Where to find: \n 

	Category 2: \n
	Recommendation: \n
	Where to find: \n  
	...
	Use a bulleted list
	"""


	template = PromptTemplate(template=prompt, input_variables=["cat_str"])
	chain = LLMChain(llm=llm, prompt=template)
	response = chain.invoke({"CAT_STR":cat_str})
	# print(response)
	return response


def get_corresponding_ret_brands(conn: psycopg2.extensions.connection, ids: List[str]) -> pd.DataFrame:
	"""
	Fetches corresponding retailers and brands for a list of IDs.

	Args:
		conn (psycopg2.extensions.connection): The database connection.
		ids (List[str]): The list of IDs to fetch data for.

	Returns:
		pd.DataFrame: A DataFrame containing retailer and brand information.
	"""

	placeholders = ', '.join(['%s'] * len(ids))
	query = f"SELECT * FROM coupons.offer WHERE offer_id IN ({placeholders})"
	test_df = psql.read_sql(query, conn, params=ids)
	return test_df


def main():
	host = "localhost"
	name = "couponsdb"
	user = "calvinyu"
	password = "password"

	conn, curr = connect_to_db(host, name, user, password)

	data = get_data()

	if "searcher" not in st.session_state:
		pine = pine_searcher.Searcher("beta-index")
		st.session_state.pinecone_object = pine

	col1, col2 = st.columns(2)

	with col1:
		selected_query = st.selectbox('Select a query', ["im looking for coupons related to pepsi",
														"thanksgiving coupons",
														"offers for cheap candy"])
		k = st.slider('Number of results (k)', 1, 10, 5)  # default value is 5

	with col2:
		query = st.text_input('Or enter a custom query')

		
	search_button = col2.button('Get Results')


	query = query or selected_query

	if search_button:
		if query:
			execution_time, res = execute_search(query, k)
			st.header(f"Execution time: {execution_time} seconds")
			pine_ids = parse_pine(res)
			df = convert_to_df(pine_ids, data)
			brand_df = get_corresponding_ret_brands(conn, pine_ids)
			result_df = pd.merge(df, brand_df, left_on='ids', right_on='offer_id', how='inner')

			st.dataframe(result_df[["offer", "retailer", "brand"]])
			response = perform_rag(df)
			st.write(response["text"])


if __name__ == "__main__":
	main()