"""
Download our three AppEEARS land-cover requests straight into per-region folders.

Why: the browser download only saved some of the 1,950 files and gave them clashing
names. This script uses the AppEEARS API instead, so every file lands in the right folder
with its real name, and it skips files you already have (safe to re-run).

Run from the repo root:
    python scripts/download_appeears.py
It asks for your Earthdata username and password in the terminal (the password is not
shown or saved anywhere). Files go to data/raw/appeears/<region>/.
"""

import getpass
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import requests
except ImportError:
    sys.exit("Please run:  pip install requests   and then run this script again.")

API = "https://appeears.earthdatacloud.nasa.gov/api"

# Request IDs from the "Request Complete" emails.
TASKS = {
    "texas": "1fc6a5da-1238-4297-813f-325e6d6272b0",
    "amazon": "adcbd3b2-ca34-4c19-9171-7d371dd3aafa",
    "australia": "83e68c8e-5758-4553-968d-09525510b52d",
}

OUT_ROOT = os.path.join("data", "raw", "appeears")


def login():
    """Log in to AppEEARS with Earthdata credentials and return a bearer token."""
    user = input("Earthdata username: ").strip()
    password = getpass.getpass("Earthdata password (hidden): ")
    r = requests.post(f"{API}/login", auth=(user, password), timeout=60)
    if r.status_code != 200:
        sys.exit(f"Login failed ({r.status_code}). Check your username and password.")
    return r.json()["token"]


def download_one(token, task_id, f, folder):
    """Download one file unless a complete copy already exists."""
    path = os.path.join(folder, f["file_name"])
    if os.path.exists(path) and os.path.getsize(path) == f["file_size"]:
        return "skipped"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    url = f"{API}/bundle/{task_id}/{f['file_id']}"
    for attempt in range(3):
        try:
            with requests.get(url, headers={"Authorization": f"Bearer {token}"},
                              stream=True, allow_redirects=True, timeout=300) as r:
                r.raise_for_status()
                tmp = path + ".part"
                with open(tmp, "wb") as out:
                    for chunk in r.iter_content(chunk_size=1 << 20):
                        out.write(chunk)
                os.replace(tmp, path)
            return "downloaded"
        except Exception as e:  # retry network hiccups
            err = e
    return f"FAILED: {err}"


def main():
    token = login()
    headers = {"Authorization": f"Bearer {token}"}
    grand_ok = True
    for region, task_id in TASKS.items():
        folder = os.path.join(OUT_ROOT, region)
        bundle = requests.get(f"{API}/bundle/{task_id}", headers=headers, timeout=60)
        if bundle.status_code != 200:
            print(f"[{region}] couldn't list files ({bundle.status_code}). "
                  "The request may have expired; resubmit it in AppEEARS.")
            grand_ok = False
            continue
        files = bundle.json()["files"]
        print(f"[{region}] {len(files)} files, "
              f"{sum(f['file_size'] for f in files) / 1e6:.0f} MB -> {folder}")
        counts = {"downloaded": 0, "skipped": 0, "failed": 0}
        with ThreadPoolExecutor(max_workers=8) as pool:
            jobs = [pool.submit(download_one, token, task_id, f, folder) for f in files]
            for i, job in enumerate(as_completed(jobs), 1):
                result = job.result()
                if result.startswith("FAILED"):
                    counts["failed"] += 1
                    print(f"  {result}")
                else:
                    counts[result] += 1
                if i % 50 == 0 or i == len(files):
                    print(f"  {i}/{len(files)} done")
        print(f"[{region}] downloaded {counts['downloaded']}, "
              f"already had {counts['skipped']}, failed {counts['failed']}")
        grand_ok &= counts["failed"] == 0
    print("\nAll done." if grand_ok else "\nSome files failed. Run the script again to retry them.")


if __name__ == "__main__":
    main()
