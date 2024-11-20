# Coupon Recommendation
The purpose of this project to provide coupon recommendations based on items that a user is looking for.

## Usage
1. I used a local database so you would not be able to access but the video should showcase the stored data.
2. You would also need access to my Pinecode credentials to see the stored data and my LlaMA credentials to use the RAG.
3. If all of this information is obtained, then run:
```
streamlit run app.py
```
to use the app.

Otherwise, here is a demo of the app and the databases:

![demo](https://github.com/cdy3870/DisneyAssessment/blob/main/assets/demo.gif)


## Pipeline

### 1. Data Ingestion

a. Provide a dataset (e.g., JSON, CSV, or unstructured text files) that includes a mix of structured and unstructured data.

b. Ask the candidate to create a pipeline to load this data into a database of their choice, ensuring the schema is optimized for querying.

-  The datasets I used contain coupons for items, their corresponding brands, and categories/child categories that the products belong to. After processing the data, I stored the different tables into a postgres database for reference during querying.


### 2. Data Preprocessing:

a. The data may contain noise or require transformation (e.g., text cleaning, parsing nested JSON, handling missing values).

b. The candidate should demonstrate how they preprocess the data for efficient storage and later retrieval.


- The main issues with the datasets are the absence of primary keys so I added keys to link brands to their categories. Since certain coupons can be attributed to multiple categories, I furthered grouped offers according to multiple categories:

    1. Every offer that has the same retailer and brand is likely just a general offer for that particular store that applies to every good in that store. For example “Spend $10 at CVS” falls under medicine & treatments, skin care, and more. We assign all of these categories to that offer.
    2. Every offer that does not have the same retailer and brand is specific to a product brand. There are instances where every corresponding category applies. For example, “Beyond Meat Plant-Based products, spend $25” falls under all of its categories (plant-based meat, frozen plant-based, packaged meat). However, a deal on "GOYA Coconut Water" falls under water, rice & grains, sauces & marinades, etc. Obviously we only want to fall under "water". 
        * We deal with this using a zero-shot learning model from HuggingFace. Zero-shot learning is an NLP technique that is capable of categorizing text even when it has not been trained on specific provided labels
        * We iterate through each of these offers and categorize it according to its most likely labels (> 0.20 probability)
    3. We then concatenate that these tables so that we have a list of offers with its corresponding categor(ies)


### 3. Vectorization:

a. Using a pre-trained language model or embeddings model, ask the candidate to convert the unstructured text into embeddings.

b. Store these embeddings in a vector storage solution of their choice, ensuring the pipeline can handle batch processing for larger datasets.

- I used Pinecone as my vector database of choice rather than a simple vector index. Pinecone allows for easier data management, metadata storage and filtering, and real-time updates for better scalability and robustness. To embed the coupon details, I used the all-MiniLM-L6-v2. Then I used a model to rerank the results to get the best matches possible. 

### 4. Query and Retrieve:

a. Create a simple API or script that allows querying based on a given text prompt. The query should retrieve similar embeddings from the vector store and return the corresponding records from the database.

b. Include a use case for Retriever-Augmented Generation (RAG), where the retrieved data is used to generate a summary or response based on the query.

- I created a Streamlit app where you can input a request for an item and the most relevant coupons are returned. I also reference other information from the database and provide those as well. I then take the categories that I grouped the coupons into and used them with retrieval augmented generation. The LLaMA model (through the Groq API) provides a set of recommended items based on the categories found during vector indexing. 

## Tradeoffs and Considerations

1. Schema Design and Data
- The data did not have primary keys and relational consistency so I had to create unique keys to link brands, retailers and product categories. These relations allowed me to connect specific offers to their corresponding retailers and brands so that the user would know where to use the coupons.
    - Tradeoff: I have two scripts that need to be run every time the data is updated to insert data and preprocess the data. Given more time to create a robust pipeline, I would use a workflow management platform like Airflow to allows for the automatic processing of the data and inserting only unique rows back into the dataframe. I would then only group the new rows into categories.
2. Vector Storage and Embeddings
- As previously mentioned, I used Pinecone because of its metadata management, real-time updates, and scalable indexing capabilities over a simple vector index. For this application, I prioritized real-time usage and speed. However, given enough resources, Pinecone would be both highly effective and fast. 
    - Tradeoff: While Pinecone is incredibly fast, for larger applications, it is more costly than alternatives such as Chroma because it is managed.
- For my embeddings, I used MiniLM-L6, which is much faster (when it comes to embedding the query phrase) and better for real-time usage.
    - Tradeoff: This model is less accurate compared to BERT embeddings. However, from my experiments in this applications, the differences were not noticeable. I would need more data to evaluate choosing BERT over MiniLM.

## Included Files
```plaintext
DisneyAssessment/
├── data/
│   ├── brand_category.csv (brands and the possible categories they fall into)
│   ├── categories.csv (categories and their parent categories)
│   ├── offer_retailer.csv (coupons and their corresponding retailers and brands)
│   ├── processed_offers.csv (grouped coupons according to category)
├── db/
│   ├── db_setup.py (connects to postgres db, creates tables and inserts data from csv to db)
│   ├── queries.py (queries used for db setup)
|   └── data_preprocess.py (preprocesses csv files before db )
├── pinecone_model/
│   ├── indexer.py (parses data, creates vector index, embeds data, and stores)
│   ├── searcher.py (queries to vector database)
│   └── utils.py (stores pinecone credentials)
├── README.md
├── app.py (Streamlit app for coupon retrieval and RAG)
└── .gitignore