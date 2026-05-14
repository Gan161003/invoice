import json
import os
import sys
from apscheduler.schedulers.background import BackgroundScheduler

# ----------------------------------
# ADD PROJECT ROOT TO PYTHON PATH
# ----------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Now scraper import works
from scraper.alert import run_alert

# ----------------------------------
# FILE PATH
# ----------------------------------

DATA_DIR = os.path.join(BASE_DIR, "backend", "data")
ALERT_FILE = os.path.join(DATA_DIR, "alerts.json")

scheduler = BackgroundScheduler()

# def schedule_alerts():

#     print("Loading alerts...")

#     scheduler.remove_all_jobs()

#     try:
#         with open(ALERT_FILE) as f:
#             alerts = json.load(f)
#     except:
#         alerts = []

#     print("Alerts found:", alerts)

#     for alert in alerts:

#         print("Processing alert:", alert)

#         if alert["status"] != "active":
#             continue

#         if not alert.get("time") or ":" not in alert["time"]:
#             print(f"Skipping invalid alert: {alert}")
#             continue

#         hour, minute = alert["time"].split(":")

#         print("Scheduling job at", hour, minute)

#         scheduler.add_job(
#             run_alert,
#             "cron",
#             hour=int(hour),
#             minute=int(minute),
#             args=[alert],
#             id=str(alert["id"]),
#             replace_existing=True
#         )

#     if not scheduler.running:
#         print("Starting scheduler...")
#         scheduler.start()


def schedule_alerts():

    global scheduler

    print("Resetting scheduler...")

    try:
        if scheduler.running:
            scheduler.shutdown(wait=False)
    except:
        pass

    scheduler = BackgroundScheduler()

    print("Loading alerts...")

    try:
        with open(ALERT_FILE) as f:
            alerts = json.load(f)
    except:
        alerts = []

    print("Alerts found:", alerts)

    for alert in alerts:

        if alert["status"] != "active":
            continue

        if not alert.get("time") or ":" not in alert["time"]:
            print("Skipping invalid alert:", alert)
            continue

        hour, minute = alert["time"].split(":")

        scheduler.add_job(
            run_alert,
            "cron",
            hour=int(hour),
            minute=int(minute),
            args=[alert],
            id=str(alert["id"]),
            replace_existing=True
        )

    print("Starting scheduler...")
    scheduler.start()