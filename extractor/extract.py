import json
import time
from dotenv import load_dotenv
from groq import Groq
from pydantic import ValidationError

from extractor.schema import Expose

load_dotenv()
client = Groq()

MODEL = "openai/gpt-oss-120b"

SYSTEM_PROMPT = (
    "Du liest Immobilien-Exposés und extrahierst die Daten. "
    "Antworte nur mit JSON nach dem vorgegebenen Schema. "
    "Erfinde keine Werte: Wenn etwas nicht im Text steht, nimm null."
)


def extract(text):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {"name": "expose", "schema": Expose.model_json_schema()},
        },
    )
    answer = response.choices[0].message.content
    return Expose.model_validate_json(answer)


def calc_yield(price, rent):
    if price is None or rent is None:
        return None
    return round((rent * 12) / price * 100, 2)


def load_exposes(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f]


if __name__ == "__main__":
    exposes = load_exposes("data/exposes.jsonl")
    results = []
    errors = []

    for e in exposes:
        try:
            data = extract(e["text"])
            row = data.model_dump()
            row["id"] = e["id"]
            row["yield_pct"] = calc_yield(data.price_eur, data.rent_month_eur)
            results.append(row)
            print(f"✅ {e['id']}: {data.city}, {row['yield_pct']} %")
        except (ValidationError, Exception) as err:
            errors.append({"id": e["id"], "error": str(err)})
            print(f"❌ {e['id']}: {err}")
        time.sleep(1)

    with open("data/results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    with open("data/errors.json", "w", encoding="utf-8") as f:
        json.dump(errors, f, ensure_ascii=False, indent=2)

    print(f"\nFertig: {len(results)} ok, {len(errors)} Fehler")