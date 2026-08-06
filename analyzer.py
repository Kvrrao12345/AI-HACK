import os
import json

from dotenv import load_dotenv
from groq import Groq


load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

PROMPT = """
You are an expert business analyst.

Analyze the website text and extract business information.

Rules:
1. Use ONLY the provided website text.
2. Never invent information.
3. If information is missing, return an empty string "".
4. Return ONLY valid JSON.
5. Do NOT wrap the JSON in markdown.

Return exactly this schema:

{
  "website_name":"",
  "company_name":"",
  "address":"",
  "core_service":"",
  "target_customer":"",
  "probable_pain_point":"",
  "outreach_opener":""
}

Website Text:
"""


def enrich_company(scraped_data):

    default_result = {
        "website_name": "",
        "company_name": "",
        "address": "",
        "core_service": "",
        "target_customer": "",
        "probable_pain_point": "",
        "outreach_opener": "",
        "mail": scraped_data.get("emails", []),
        "mobile_number": (
            scraped_data["phones"][0]
            if scraped_data.get("phones")
            else ""
        )
    }

    try:

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": PROMPT + scraped_data["text"][:12000]
                }
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )

        text = completion.choices[0].message.content.strip()

        result = json.loads(text)

        result["mail"] = scraped_data.get("emails", [])

        result["mobile_number"] = (
            scraped_data["phones"][0]
            if scraped_data.get("phones")
            else ""
        )

        return result

    except Exception as e:

        print(f"Groq Error: {e}")

        return default_result