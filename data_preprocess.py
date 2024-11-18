import pandas as pd
import hashlib

# df = pd.read_csv("data/processed_offers.csv").drop(columns=["index", "Unnamed: 0"], axis=1)
# df.reset_index(inplace=True)

# print(df.columns)

# df.to_csv("data/processed_offers.csv", index=False)


# df = pd.read_csv("data/processed_offers.csv").drop(columns=["index", "Unnamed: 0"], axis=1)


# dataframe['unique_id'] = [self.generate_unique_id() for _ in range(len(dataframe))]

processed_df = pd.read_csv("data/processed_offers.csv")
offer_df = pd.read_csv("data/offer_retailer.csv")

# processed_df['OFFER_ID'] = processed_df['OFFER'] + processed_df['CATEGORY'].apply(lambda x: ' '.join(x))

# offer_df['OFFER_ID'] = offer_df['OFFER'] + offer_df['RETAILER'].fillna('') + offer_df['BRAND']


# def generate_unique_id(text):
#     return hashlib.sha256(text.encode('utf-8')).hexdigest()


# processed_df['OFFER_ID'] = processed_df['OFFER'].apply(generate_unique_id)
# offer_df['OFFER_ID'] = offer_df['OFFER'].apply(generate_unique_id)
# offer_df = offer_df.drop_duplicates(subset='OFFER_ID', keep='first')

# offer_df.to_csv("offer_retailer.csv", index=False)
# processed_df.to_csv("processed_offers.csv", index=False)

def generate_unique_id(offer, retailer):
    key = f"{offer}-{retailer if retailer else 'Unknown'}"
    return hashlib.sha256(key.encode('utf-8')).hexdigest()

offer_df['UNIQUE_ID'] = offer_df.apply(lambda row: generate_unique_id(row['OFFER'], row['RETAILER']), axis=1)

# Step 2: Map unique IDs back to the processed_offer DataFrame
# First, create a mapping of OFFER to UNIQUE_ID
offer_id_mapping = offer_df.set_index('OFFER')['UNIQUE_ID'].to_dict()

# Assign the unique ID to the processed_offer DataFrame
processed_df['UNIQUE_ID'] = processed_df['OFFER'].map(offer_id_mapping)

offer_df.to_csv("offer_retailer.csv", index=False)
processed_df.to_csv("processed_offers.csv", index=False)
