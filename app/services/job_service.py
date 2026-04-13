import json

def _load_jobs():
    with open("app/data/jobs.json", "r", encoding="utf-8") as f:
        return json.load(f)

def get_job():
    return _load_jobs()[0]

def get_jobs_by_categories(category_indices: list) -> list:
    if not category_indices:
        return []
    jobs = _load_jobs()
    return [j for j in jobs if j.get("category") in category_indices]

def generate_jobs_by_categories(category_indices: list, per_category: int = 1000) -> list:
    if not category_indices:
        return []
    base_jobs = _load_jobs()
    result = []
    for cat_idx in sorted(category_indices):
        templates = [j for j in base_jobs if j.get("category") == cat_idx]
        if not templates:
            continue
        n = len(templates)
        for i in range(per_category):
            t = templates[i % n]
            batch = i // n + 1
            job = t.copy()
            job["_seq"] = len(result) + 1
            job["_cat_seq"] = i + 1
            if batch > 1:
                job = {**t, "_seq": len(result) + 1, "_cat_seq": i + 1,
                       "title_ar": f"{t['title_ar']} #{batch}",
                       "title_en": f"{t['title_en']} #{batch}"}
            result.append(job)
    return result
