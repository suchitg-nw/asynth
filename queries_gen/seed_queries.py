# %%
import json
import os
from functools import cache

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

sys_prompt = """\
You are a helpful assistant tasked with generating customer support queries based on specific intents. The customer could be interacting with a support agent regarding issues, requests, or inquiries related to various aspects of their experience.

For each intent, output a JSON object in the following format:

{
    "intent": "<intent_name>",
    "seed_queries": [
        "1. <query1>",
        "2. <query2>",
        ...
    ]
}

### Guidelines ###
- Intent Name: A specific, predefined category such as "DELIVERY_damaged_item" or "PRODUCT_exchange_product.". The intents are typically in the format: SUBJECT_verb_object.
- Seed Queries: These are questions or statements a customer might ask, naturally phrased, reflecting different variations of the intent. Provide *exactly 20* queries that a customer may ask for each intent.
- Keep the language simple, conversational, and realistic.
- Include possible variations in phrasing and urgency where applicable.

### Example ###
User Input: "INTENT: DELIVERY_damaged_item"
Assistant Output:
{
    "intent": "DELIVERY_damaged_item",
    "seed_queries": [
        "1. What can I do about my damaged order?",
        "2. The item I received is broken. Can I get a replacement?",
        "3. How do I return a defective product?",
        "4. The package I received is damaged. Who should I contact?",
        "5. My delivery was damaged. I need assistance.",
        ...
    ]
}

Generate similarly formatted queries for each intent provided.
"""

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
with open("seed_queries.jsonl", "a") as f:
    res = get_seed_queries()
    for queries in res:
        q = queries.choices[0].message.content.replace("\u2019", "'")
        json.dump(json.loads(q), f)
        f.write("\n")
