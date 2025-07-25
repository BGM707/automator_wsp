import schedule
import pywhatkit
import json
import time
import logging
from datetime import datetime

logging.basicConfig(
    filename="scheduler.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def load_schedule(schedule_file):
    try:
        if os.path.exists(schedule_file):
            with open(schedule_file, "r") as f:
                return json.load(f)
    except Exception as e:
        logging.error(f"Error loading schedule: {str(e)}")
    return {}

def load_history(history_file):
    try:
        if os.path.exists(history_file):
            with open(history_file, "r") as f:
                return json.load(f)
    except Exception as e:
        logging.error(f"Error loading history: {str(e)}")
    return []

def send_whatsapp(number, message, hour, minute):
    try:
        logging.info(f"Attempting to send message to {number} at {hour:02d}:{minute:02d}")
        pywhatkit.sendwhatmsg(number, message, hour, minute, wait_time=40, tab_close=True)
        logging.info(f"Message sent successfully to {number}")
        history_file = "send_history.json"
        history = load_history(history_file)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        history.append({
            "timestamp": timestamp,
            "number": number,
            "message": message,
            "status": "Success",
            "error": ""
        })
        with open(history_file, "w") as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        logging.error(f"Failed to send message to {number}: {str(e)}")
        history_file = "send_history.json"
        history = load_history(history_file)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        history.append({
            "timestamp": timestamp,
            "number": number,
            "message": message,
            "status": "Failed",
            "error": str(e)
        })
        with open(history_file, "w") as f:
            json.dump(history, f, indent=2)

def check_schedule():
    schedule_file = "schedule.json"
    schedule_data = load_schedule(schedule_file)
    if not schedule_data.get("active"):
        return
    try:
        year = int(schedule_data.get("year"))
        month = int(schedule_data.get("month"))
        day = int(schedule_data.get("day"))
        hour = int(schedule_data.get("hour"))
        minute = int(schedule_data.get("minute"))
        number = schedule_data.get("number")
        message = schedule_data.get("message")
        schedule_time = datetime(year, month, day, hour, minute)
        now = datetime.now()
        if now.year == year and now.month == month and now.day == day:
            schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(
                send_whatsapp, number, message, hour, minute
            )
            logging.info(f"Scheduled message for {number} at {year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}")
        if now >= schedule_time:
            schedule_data["active"] = False
            with open(schedule_file, "w") as f:
                json.dump(schedule_data, f, indent=2)
            logging.info("Schedule deactivated after sending")
    except Exception as e:
        logging.error(f"Error in scheduler: {str(e)}")

def main():
    schedule.every(60).seconds.do(check_schedule)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()