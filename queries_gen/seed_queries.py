# %%
import json
import os
from functools import cache

from dotenv import load_dotenv
from openai import OpenAI
from prompts import sys_prompt

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

intents = [
    "DELIVERY_damaged_item",
    "PAYMENT_report_payment_issue",
    "PRODUCT_exchange_product",
]


# %%
@cache
def get_seed_queries():
    res = [
        client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": f"INTENT: {intent}"},
            ],
            response_format={"type": "json_object"},
        )
        for intent in intents
    ]
    return res


# %%
with open("./data/seed_queries.jsonl", "a") as f:
    res = get_seed_queries()
    for queries in res:
        q = queries.choices[0].message.content.replace("\u2019", "'")
        json.dump(json.loads(q), f)
        f.write("\n")
