import pandas as pd
import hashlib
from transformers import pipeline

def generate_unique_id(offer, retailer):
    key = f"{offer}-{retailer if retailer else 'Unknown'}"
    return hashlib.sha256(key.encode('utf-8')).hexdigest()

def add_unique_ids_offers():
    processed_df = pd.read_csv("data/processed_offers.csv")
    offer_df = pd.read_csv("data/offer_retailer.csv")

    offer_df['UNIQUE_ID'] = offer_df.apply(lambda row: generate_unique_id(row['OFFER'], row['RETAILER']), axis=1)
    offer_id_mapping = offer_df.set_index('OFFER')['UNIQUE_ID'].to_dict()

    processed_df['UNIQUE_ID'] = processed_df['OFFER'].map(offer_id_mapping)

    offer_df.to_csv("offer_retailer.csv", index=False)
    processed_df.to_csv("processed_offers.csv", index=False)


def add_unique_ids_categories():
    categories_df = pd.read_csv("data/categories.csv")
    brand_category_df = pd.read_csv("data/brand_category.csv")
    category_mapping = dict(zip(categories_df['PRODUCT_CATEGORY'], categories_df['CATEGORY_ID']))
    brand_category_df['CATEGORY_ID'] = brand_category_df['BRAND_BELONGS_TO_CATEGORY'].map(category_mapping)


    brand_category_df.to_csv("brand_category.csv", index=False)

def fill_retailer():
    offer_rets = pd.read_csv("data/offer_retailer.csv")
    offer_rets['RETAILER'] = offer_rets['RETAILER'].replace("", "not retailer specific").fillna("not retailer specific")

    offer_rets.to_csv("data/offer_retailer.csv", index=False)


def group_offers():
    pipe = pipeline(task="zero-shot-classification", model="facebook/bart-large-mnli")
    brand_cats = pd.read_csv("data/brand_category.csv")
    offer_rets = pd.read_csv("data/offer_retailer.csv")

    generic_offers = offer_rets[offer_rets["RETAILER"] == offer_rets["BRAND"]].merge(brand_cats, left_on="BRAND", right_on="BRAND")
    grouped_generic = generic_offers.groupby('RETAILER').agg({'BRAND_BELONGS_TO_CATEGORY':lambda x: set(x)})
    labeled_generic_offers = offer_rets[offer_rets["RETAILER"] == offer_rets["BRAND"]].merge(grouped_generic, left_on="RETAILER", right_on="RETAILER")
        
    generic_offers_new = labeled_generic_offers[["OFFER", "BRAND_BELONGS_TO_CATEGORY"]].rename({"BRAND_BELONGS_TO_CATEGORY":"CATEGORY"}, axis=1)
    specific_offers = offer_rets[offer_rets["RETAILER"] != offer_rets["BRAND"]].merge(brand_cats, left_on="BRAND", right_on="BRAND").head(500)


    completed_set = set()
    new_offers = {"OFFER": [], "CATEGORY":[]}
    threshold = 0.20
    for i in range(len(specific_offers)):
        offer = specific_offers.iloc[i]["OFFER"]
        if offer not in completed_set:
            related_cats = list(specific_offers[specific_offers["OFFER"] == offer]["BRAND_BELONGS_TO_CATEGORY"])

            labels = pipe(offer,
            candidate_labels=related_cats)

            thresholded_labels = [l for i, l in enumerate(labels["labels"]) if labels["scores"][i] > threshold]
            if len(thresholded_labels) == 0:
                new_offers["CATEGORY"].append({labels["labels"][0]})
            else:
                new_offers["CATEGORY"].append(set(thresholded_labels))
            new_offers["OFFER"].append(offer)
            completed_set.add(offer)

            print(offer)
            print(set(thresholded_labels))

    specific_offers_new = pd.DataFrame(new_offers)
    processed_offers = pd.concat([specific_offers_new, generic_offers_new]).reset_index()
    processed_offers.to_csv("data/processed_offers.csv", index=False)



    
def main():
    fill_retailer()
    # add_unique_ids_offers()
    # add_unique_ids_categories()
    # group_offers()


if __name__ == "__main__":
    main()
