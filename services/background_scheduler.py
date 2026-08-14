"""VisionBoard background job synchronization scheduler.

Runs outside Streamlit so opening/refreshing the HR portal never starts a
three-minute aggregation job. Keep this process running on the server/PC,
or register it with Windows Task Scheduler / a service manager.
"""

import time
from datetime import datetime

from services.sync_service import safe_sync, sync_is_due

INTERVAL_HOURS = 6
POLL_SECONDS = 60


def run_forever():
    print("=" * 70)
    print("VisionBoard Background Scheduler")
    print(f"Sync interval: every {INTERVAL_HOURS} hours")
    print("Streamlit remains read-only; HR users are not blocked by sync.")
    print("=" * 70)

    while True:
        try:
            if sync_is_due(INTERVAL_HOURS):
                print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] Scheduled sync due.")
                safe_sync()
            else:
                print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] No sync required yet.")
        except Exception as exc:
            print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] Scheduler error: {exc}")

        # Polling is deliberately short so an operator can stop/restart the
        # process cleanly without waiting for a six-hour sleep.
        for _ in range((INTERVAL_HOURS * 3600) // POLL_SECONDS):
            time.sleep(POLL_SECONDS)
            if sync_is_due(INTERVAL_HOURS):
                break


if __name__ == "__main__":
    run_forever()
