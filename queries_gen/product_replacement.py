# %%
import json
import os
import re
from functools import cache

from dotenv import load_dotenv
from openai import OpenAI
from prompts import product_sys_prompt

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# %%
def extract_products(query: str) -> list[str] | None:
    """Extracts products enclosed in `[]` and return them as a list."""
    products = re.search(r"\w*\[(.*)\]\w*", query)

    if products is None:
        return None
    else:
        return list(map(str.strip, products.group(1).split(",")))


def insert_products(query: str, products: list[str]) -> list[str]:
    """Substitutes the product placeholder with individual products and returns a list of newly created queries."""
    updated: list[str] = []

    for product in products:
        # Substitute `\[.*\]` with product name
        temp = re.sub(r"\w*(\[.*\])\w*", product, query)
        updated.append(temp)

    return updated


def process_queries(json_inp: dict[str, str | list[str]]):
    """Gets the product list for each query and creates multiple queries having one product each."""
    updated: list[str] = []

    for query in json_inp["seed_queries"]:
        # Remove numbering
        query = re.sub(r"^\d+\.\s*", "", query)

        # Extract products to a list
        products = extract_products(query)

        # No products inserted by the LLM
        if products is None:
            updated.append(query)
            continue
        updated.extend(insert_products(query, products))

    return updated


# %%
@cache
def augment_queries(json_str: str):
    """Introduces products in the queries wherever applicable."""
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": product_sys_prompt},
            {"role": "user", "content": json.dumps(json_str, indent=4)},
        ],
        response_format={"type": "json_object"},
        temperature=0.6,
    )
    return res.choices[0].message.content


# %%
with open("./data/seed_queries.jsonl", "r") as f:
    out_f = open("./data/product_aug.jsonl", "a")

    for line in f:
        dict_repr = json.loads(line)

        if "PRODUCT" not in dict_repr["intent"]:
            json.dump(dict_repr, out_f)
            out_f.write("\n")
            continue

        # Get the queries augmented with products
        aug_queries = augment_queries(json.dumps(dict_repr, indent=4))
        # Process the queries to separate them and create new queries for individual products
        dict_repr["seed_queries"] = process_queries(json.loads(aug_queries))

        json.dump(dict_repr, out_f)
        out_f.write("\n")
    out_f.close()
