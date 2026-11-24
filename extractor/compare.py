import json

FIELDS = ["city", "property_type", "rooms", "size_m2", "price_eur", "rent_month_eur", "yield_pct"]


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def is_equal(field, got, want):
    if got is None or want is None:
        return got == want
    if field == "yield_pct":
        return abs(got - want) < 0.01
    return got == want


if __name__ == "__main__":
    results = load_json("data/results.json")
    expected = load_json("data/expected.json")

    results_by_id = {r["id"]: r for r in results}
    correct = {f: 0 for f in FIELDS}
    total = len(expected)

    print("=== Fehler im Detail ===")
    for exp in expected:
        exp["yield_pct"] = exp["expected_yield_pct"]
        res = results_by_id.get(exp["id"])

        if res is None:
            print(f"ID {exp['id']}: keine Antwort vom LLM (siehe errors.json)")
            continue

        for f in FIELDS:
            if is_equal(f, res.get(f), exp.get(f)):
                correct[f] += 1
            else:
                print(f"ID {exp['id']} {f}: LLM={res.get(f)}, richtig={exp.get(f)}  ({exp['note']})")

    print("\n=== Ergebnis pro Feld ===")
    for f in FIELDS:
        print(f"{f:15} {correct[f]:2}/{total} richtig")

    all_checks = total * len(FIELDS)
    all_correct = sum(correct.values())
    print(f"\nGesamt: {all_correct}/{all_checks} = {all_correct / all_checks * 100:.1f} %")