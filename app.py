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

st.set_page_config(layout="wide") 

llm = ChatGroq(model="llama3-70b-8192", api_key="")

def setup_db(host, name, user, password):
	db = db_setup.DBDriver(host=host, name=name, user=user, password=password)
	db.setup()

	return db	

def parse_pine(results):
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
    
    print(table_data)
        

    return table_data, ids


def convert_to_df(ids, data):
    categories = []
    offers = []
    for id in ids:
        offers.append(data[data["UNIQUE_ID"] == id]["OFFER"].values[0])
        categories.append(data[data["UNIQUE_ID"] == id]["CATEGORY"].values[0])

    df = pd.DataFrame({'ids': ids, 'offers': offers, 'categories': categories})

    st.write(df)

    return df


def execute_search(query, k, model="pine"):
    s = st.session_state.pinecone_object

    start_time = time.time()
    res = s.execute_query(query, k=k)

    execution_time = time.time() - start_time

    return execution_time, res

@st.cache_data
def get_data():
    data = pd.read_csv('data/processed_offers.csv')
    return data

def perform_rag(df):
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

def get_corresponding_ret_brands(conn, ids):
    placeholders = ', '.join(['%s'] * len(ids))
    query = f"SELECT * FROM coupons.offer WHERE offer_id IN ({placeholders})"
    test_df = psql.read_sql(query, conn, params=ids)
    print(test_df)
    return test_df


def main():
    host = "localhost"
    name = "couponsdb"
    user = "calvinyu"
    password = "password"

    db = setup_db(host, name, user, password)

    data = get_data()

    if "searcher" not in st.session_state:
        pine = pine_searcher.Searcher("beta-index")
        st.session_state.pinecone_object = pine

    col1, col2 = st.columns(2)

    with col1:
        selected_query = st.selectbox('Select a query', ["test", "test2"])
        k = st.slider('Number of results (k)', 1, 10, 5)  # default value is 5

    with col2:
        query = st.text_input('Or enter a custom query')

        
    search_button = col2.button('Get Results')


    query = query or selected_query

    if search_button:
        if query:
            execution_time, res = execute_search(query, k, model="pine")
            st.header(f"Execution time: {execution_time} seconds")
            table_data, pine_ids = parse_pine(res)
            other_df = get_corresponding_ret_brands(db.conn, pine_ids)
            st.dataframe(other_df)
            df = convert_to_df(pine_ids, data)
            response = perform_rag(df)
            st.write(response["text"])




if __name__ == "__main__":
    main()