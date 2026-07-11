import requests
import json
import os

# Define your API configuration
APIS = [
    {
        "name": "Arbeitnow",
        "url": "https://arbeitnow.com/api/job-board-api",
        "method": "get_arbeitnow"
    },
    {
        "name": "Adzuna",
        "url": "https://api.adzuna.com/v1/api/jobs/gb/search/1",
        "params": {"app_id": os.getenv("ADZUNA_ID"), "app_key": os.getenv("ADZUNA_KEY")},
        "method": "get_adzuna"
    }
]

def get_arbeitnow(api):
    response = requests.get(api["url"], timeout=10)
    data = response.json()
    # Arbeitnow uses 'slug' as a unique identifier for jobs
    return data.get('data', [])

def get_adzuna(api):
    response = requests.get(api["url"], params=api["params"], timeout=10)
    data = response.json()
    # Adzuna uses 'id' as a unique identifier
    return data.get('results', [])

def update_jobs():
    all_jobs = []
    
    for api in APIS:
        try:
            print(f"Attempting to fetch from {api['name']}...")
            if api["method"] == "get_arbeitnow":
                jobs = get_arbeitnow(api)
            elif api["method"] == "get_adzuna":
                # Only attempt if keys are provided
                if api["params"]["app_id"] and api["params"]["app_key"]:
                    jobs = get_adzuna(api)
                else:
                    print(f"Skipping {api['name']}: No API keys found.")
                    continue
            
            if jobs:
                all_jobs.extend(jobs)
                print(f"Successfully fetched {len(jobs)} jobs from {api['name']}.")
        except Exception as e:
            print(f"Failed to fetch from {api['name']}: {e}")
            continue

    # Ensure the data directory exists
    if not os.path.exists("data"):
        os.makedirs("data")

    # Save to local file with Deduplication
    if all_jobs:
        # Deduplication: uses 'slug' or 'id' as the key to prevent duplicates
        unique_jobs = {job.get('slug') or job.get('id'): job for job in all_jobs if job.get('slug') or job.get('id')}.values()
        
        with open("data/jobs.json", "w") as f:
            json.dump(list(unique_jobs), f)
        print(f"Data update complete. {len(unique_jobs)} unique jobs saved.")
    else:
        print("Error: No data could be fetched from any source.")

if __name__ == "__main__":
    update_jobs()