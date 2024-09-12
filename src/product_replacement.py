# %%
import json
import os
import re

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

product_sys_prompt = """\
You are an assistant tasked with enhancing customer support queries by introducing product names into the queries wherever applicable. The goal is to increase the diversity and number of queries while keeping them meaningful.

For the given intents you will insert product names from the list provided wherever applicable in the queries. If the query naturally fits a mention of specific products, you should replace or introduce the relevant products in the form of a list enclosed in square brackets `[ ]`. If adding products does not make sense for a particular query, leave it unchanged.

### Input Format ###

You will be provided with a JSON object containing the intent and a list of seed queries. For example:

{
  "intent": "PRODUCT_refund_policy",
  "seed_queries": [
    "1. What is your refund policy for products?",
    "2. How do I request a refund?",
    "3. Will I receive a full refund for a returned item?",
    "4. What items are eligible for a refund?",
    "5. How long does it take to process a refund?"
  ]
}

### List of Applicable Products ###
[ camera, laptop, microwave oven, groceries, tank top t-shirt ]

### Output Format ###

You will output the same JSON object with the seed queries modified as follows:
- Insert the list of applicable products in `[ ]` wherever relevant.
- Ensure that the products only appear where they make sense in the context of the query.

For example:

{
  "intent": "PRODUCT_refund_policy",
  "seed_queries": [
    "1. What is your refund policy for [camera, laptop, microwave oven, groceries, tank top t-shirt]?",
    "2. How do I request a refund?",
    "3. Will I receive a full refund for a returned [camera, laptop, microwave oven, groceries, tank top t-shirt]?",
    "4. What [camera, laptop, microwave oven, groceries, tank top t-shirt] are eligible for a refund?",
    "5. How long does it take to process a refund?",
    ...
  ]
}

### Guidelines ###
- Apply products where they logically fit in the query. Use your wise judgment and incredible intelligence to not include certain products where they are simply not applicable (subsets of products are allowed).
- Do not introduce product mentions if it doesn't add meaning to the query.
- Ensure the queries remain natural and useful for e-commerce customer support scenarios.
- Pay attention to the list of products given above. Do not include products outside of this list.
"""

intents = [
    "DELIVERY_damaged_item",
    "PAYMENT_report_payment_issue",
    "PRODUCT_exchange_product",
]
user_prompt = """\
{
    "intent": "PRODUCT_product_issue",
    "seed_queries": [
        "1. I'm having trouble with my product. What should I do?",
        "2. The item I bought isn't working properly. Can you help?",
        "3. My product has a defect. How do I proceed?",
        "4. There's an issue with my order. Can I get support?",
        "5. How can I fix the problem with my item?",
        "6. The product I received is malfunctioning. What are my options?",
        "7. Can you assist me with a problem I'm facing with my purchase?",
        "8. I need help with a product that isn't functioning as it should.",
        "9. What steps should I take if my product is not working?",
        "10. I'm experiencing some issues with my recent order. Can you help me?",
        "11. My device is acting up. Is there a way to troubleshoot it?",
        "12. I received a product that doesn't work. How do I get it fixed?",
        "13. Can you guide me on what to do about my faulty item?",
        "14. I'm unsure about how to resolve an issue with a product I bought.",
        "15. The item I got has some problems. Who do I contact?",
        "16. Can you provide me with support for my defective product?",
        "17. I'm frustrated with a malfunctioning product. What can I do?",
        "18. Do you have any troubleshooting tips for my item?",
        "19. My product is not performing well. Can I return it?",
        "20. I need assistance with a product that isn't working as expected."
    ]
}
"""

# %%
res = [
    client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": product_sys_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.5,
    )
]

# %%
res = res[0].choices[0].message.content
print(res)

# %%
res = json.loads(res)

# %%
for i, q in enumerate(res["seed_queries"]):
    res["seed_queries"][i] = re.sub(r"^\d+\.\s*", "", q)

# %%
print(res["seed_queries"])

# %%
t = res["seed_queries"][0]
# t = "this is a plain text lol"
matches = re.search(r"\w*\[(.*)\]\w*", t)
list(map(str.strip, matches.group(1).split(",")))

# %%
for r in res["seed_queries"]:
    products = re.search(r"\w*\[(.*)\]\w*", r)
    if products is None:
        continue

    products = list(map(str.strip, products.group(1).split(",")))
    for p in products:
        print(re.sub(r"\w*(\[.*\])\w*", p, r))
    break
