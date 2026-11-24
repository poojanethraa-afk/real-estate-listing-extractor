# Real Estate Listing Extractor

Extracts structured data from free-text German real-estate listings with a large language model, validates every answer against a Pydantic schema, calculates the gross rental yield and measures the accuracy against an answer key.

> **The listings are synthetic.** The 20 listings in `data/exposes.jsonl` were written for this exercise. Cities and districts are real; properties, prices and rents are invented.

## How it works

```
exposes.jsonl -> LLM with JSON schema (Groq) -> Pydantic validation -> yield calculation -> results.json -> compare with answer key
```

1. [extractor/extract.py](extractor/extract.py) sends each listing to the model `openai/gpt-oss-120b` on Groq. The answer format is forced with a JSON schema (`response_format`), and the answer is validated with Pydantic. Listings that fail are written to `data/errors.json`.
2. The gross rental yield is calculated in code, not by the model: `monthly rent x 12 / price x 100`.
3. [extractor/compare.py](extractor/compare.py) compares the results with [data/expected.json](data/expected.json) field by field and prints the accuracy.

## The schema

[extractor/schema.py](extractor/schema.py) defines seven fields. The field descriptions are part of the prompt and carry the business rules.

| Field | Rule written into the description |
|---|---|
| `city` | German spelling: "München" instead of "Munich" |
| `district` | As written in the text, otherwise null |
| `property_type` | Eigentumswohnung, Pflegeapartment (care apartment) or Mikroapartment |
| `rooms` | As a number ("2,5 Zimmer" is 2.5), null if not stated |
| `size_m2` | Living area; if two values are given, take the one from the living area calculation |
| `price_eur` | Whole euros: "135 T€" is 135000, "349k" is 349000, "price on request" is null |
| `rent_month_eur` | Monthly **net** rent; a yearly rent is divided by 12; null if empty or no rent is given |

The system prompt tells the model not to invent values: if something is not in the text, the answer is null.

## The test data

The 20 listings are deliberately hard: yearly instead of monthly rent, decimal commas, "T€" and "k" notation, abbreviations ("Whg.", "KP", "qm"), a typo in a city name, an English listing with US number format, a missing price, a vacant apartment without rent, warm rent that must not be taken for cold rent, two contradicting area figures, contact details in the text, and a very short listing. [data/expected.json](data/expected.json) holds the correct answer for each one, with a note on the trap.

## Results

One run (saved in [data/results.json](data/results.json)) reaches **134 of 140 fields correct (95.7%)**. Model output can vary between runs.

| Field | Correct |
|---|---|
| city | 20 / 20 |
| size_m2 | 20 / 20 |
| price_eur | 20 / 20 |
| rent_month_eur | 20 / 20 |
| yield_pct | 20 / 20 |
| property_type | 19 / 20 |
| rooms | 15 / 20 |

The six misses:

- **`rooms` (5 listings):** the text never states a number of rooms (for example "Apartment in Seniorenresidenz, 38,5 m2"), so the model returned null, as instructed. The answer key expects an inferred 1. This is a design decision: either accept null, or add a rule to the schema that single apartments count as one room.
- **`property_type` (1 listing):** an English listing for a student apartment in Munich was classified as Eigentumswohnung instead of Mikroapartment.

## Run it

```bash
pip install -r requirements.txt
cp .env.example .env              # then enter your Groq API key in .env
python -m extractor.extract       # writes data/results.json and data/errors.json
python -m extractor.compare       # prints the accuracy per field
```

`check_groq.py` is a small script that tests the API connection. The API key is read from the environment and is not stored in the code.

## Tech stack

Python, Groq API, Pydantic, structured LLM output (JSON schema)
