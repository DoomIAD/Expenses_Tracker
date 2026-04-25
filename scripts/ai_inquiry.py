# ai_inquiry.py

import requests
import json
import re
from private_keys import api_key

CATEGORIES = [
    "groceries", "restaurant", "transport", "shopping",
    "entertainment", "utilities", "subscriptions",
    "health", "travel", "other"
]

def extract_json(text: str):
    # remove code fences if present
    text = text.strip()
    text = re.sub(r"```json|```", "", text)

    # try to find JSON object inside text
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON object found in: {text}")

    return json.loads(match.group(0))

def categorize_merchant(name: str) -> str:
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": "openai/gpt-5.2",
            "messages": [
                {
                    "role": "user",
                    "content": f"""
Categorize this merchant into ONE of the following categories:

{", ".join(CATEGORIES)}

Merchant: {name}

Return ONLY valid JSON in this format:
{{ "category": "<category>" }}
"""
                }
            ],
            "max_tokens": 200
        }
    )

    data = response.json()

    # check for API error first
    if "error" in data:
        raise Exception(f"API Error: {data['error']}")

    # extract content
    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as e:
        raise Exception(f"Unexpected API response format: {data}") from e

    if not content:
        raise Exception(f"Empty model response: {data}")

    # clean possible markdown fences
    content = content.strip().replace("```json", "").replace("```", "")

    data = extract_json(content)
    return data["category"].strip().lower()
