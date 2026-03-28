import pandas as pd
import chromadb
from tqdm import tqdm

import os
_dir = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(_dir, "food_densities.csv"))

client = chromadb.PersistentClient(os.path.join(_dir, "ragclient_density"))

def _ensure_collection():
    try:
        return client.get_collection("food_density")
    except Exception:
        col = client.create_collection("food_density")
        name = df["Food Name and Description"]
        BATCH_SIZE = 1000
        total = len(df)
        for i in tqdm(range(0, total, BATCH_SIZE), desc="Embedding densities"):
            end_idx = min(i + BATCH_SIZE, total)
            names = name.iloc[i:end_idx].to_list()
            batch_ids = [f"food_{j}" for j in range(i, end_idx)]
            batch_metas = [{"idx": j} for j in range(i, end_idx)]
            col.add(documents=names, ids=batch_ids, metadatas=batch_metas)
        return col

collection = _ensure_collection()


def query(food):
    res = collection.query(query_texts=[food], n_results=1)
    idx = int(res["ids"][0][0].removeprefix("food_"))
    d = df.iloc[idx]["Density"]
    if "-" in d:
        d = d.split("-")
        return (float(d[1]) + float(d[0])) / 2, df.iloc[idx][
            "Food Name and Description"
        ]
    else:
        return float(d), df.iloc[idx]["Food Name and Description"]
