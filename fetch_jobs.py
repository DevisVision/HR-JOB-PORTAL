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
    # Add Adzuna or others here once your key is active
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
    # Arbeitnow structure: {'data': [...]}
    return data.get('data', [])

def get_adzuna(api):
    response = requests.get(api["url"], params=api["params"], timeout=10)
    data = response.json()
    # Adzuna structure: {'results': [...]}
    return data.get('results', [])

def update_jobs():
    all_jobs = []
    
    for api in APIS:
        try:
            print(f"Attempting to fetch from {api['name']}...")
            if api["method"] == "get_arbeitnow":
                jobs = get_arbeitnow(api)
            elif api["method"] == "get_adzuna":
                jobs = get_adzuna(api)
            
            if jobs:
                all_jobs.extend(jobs)
                print(f"Successfully fetched {len(jobs)} jobs from {api['name']}.")
                # If you only need one successful source, you can 'break' here
                # break 
        except Exception as e:
            print(f"Failed to fetch from {api['name']}: {e}")
            continue # Move to the next API in the list

    # Save to local file
    if all_jobs:
        with open("data/jobs.json", "w") as f:
            json.dump(all_jobs, f)
        print("Data update complete.")
    else:
        print("Error: No data could be fetched from any source.")

if __name__ == "__main__":
    update_jobs()