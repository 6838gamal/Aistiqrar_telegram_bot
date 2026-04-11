import json

def get_job():
    with open("data/jobs.json", "r", encoding="utf-8") as f:
        return json.load(f)[0]
