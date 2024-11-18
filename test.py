import pandas as pd

df = pd.read_csv("data/processed_offers.csv").drop(columns=["index", "Unnamed: 0"], axis=1)
df.reset_index(inplace=True)

print(df.columns)

df.to_csv("data/processed_offers.csv", index=False)
