import pandas as pd
import pickle
import os
import chromadb
from tqdm import tqdm

_dir = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(_dir, "13k-recipes.csv"))
del df["Unnamed: 0"]

client = chromadb.PersistentClient(os.path.join(_dir, "ragclient"))
# collection = client.create_collection("fucking_shit")
#
# ingredients = df["Ingredients"]
# titles = df["Title"]
#
# BATCH_SIZE = 1000
# total = len(ingredients)
#
# for i in tqdm(range(0, total, BATCH_SIZE), desc="Embedding recipes"):
#     end_idx = min(i + BATCH_SIZE, total)
#
#     batch_docs = ingredients.iloc[i:end_idx].to_list()
#     batch_ids = [f"recipe_{j}" for j in range(i, end_idx)]
#     batch_metas = [{"idx": j, "title": titles.iloc[j]} for j in range(i, end_idx)]
#
#     collection.add(documents=batch_docs, ids=batch_ids, metadatas=batch_metas)
#
# results = collection.query(
#     query_texts=["shit"],
#     n_results=10,
# )
#
# for doc, meta, dist in zip(
#     results["documents"][0], results["metadatas"][0], results["distances"][0]
# ):
#     print(f"{meta['title']} (dist: {dist:.3f})")
#     print(f"  Ingredients: {doc[:100]}...")

try:
    collection = client.get_collection("fucking_shit")
except:
    print("Creating collection, this may take a while...", flush=True)
    collection = client.create_collection("fucking_shit")
    ingredients = df["Ingredients"]
    titles = df["Title"]
    BATCH_SIZE = 1000
    total = len(ingredients)
    for i in range(0, total, BATCH_SIZE):
        end_idx = min(i + BATCH_SIZE, total)
        batch_docs = ingredients.iloc[i:end_idx].to_list()
        batch_ids = [f"recipe_{j}" for j in range(i, end_idx)]
        batch_metas = [{"idx": j, "title": titles.iloc[j]} for j in range(i, end_idx)]
        collection.add(documents=batch_docs, ids=batch_ids, metadatas=batch_metas)
    print("Collection created.", flush=True)


def query(q, n_results=25):
    res = collection.query(query_texts=[q], n_results=n_results)
    idxs = []
    for i in range(len(res["ids"][0])):
        idx = int(res["ids"][0][i].removeprefix("recipe_"))
        idxs.append(idx)
    return idxs


def format_options(idxs):
    options = df.iloc[idxs]
    # 'Ingredients'
    # 'Instructions'
    # 'Title'
    res = ""
    for x in options.index:
        ttl, ins, ing = options.loc[x][["Title", "Instructions", "Ingredients"]]
        res += f"{ttl}\nIngredients: {ing}\n\n"
    return res


if __name__ == "__main__":
    idxs = query("containing no potatos")
    res = format_options(idxs)
    print(res)
