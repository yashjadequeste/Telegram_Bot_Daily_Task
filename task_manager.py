import json
import os
from datetime import datetime

from excel_handler import complete_rows_in_excel, update_existing_status

TASK_FILE = "reports/tasks.json"
ACTIVE_STATUSES = ("Pending", "In Progress")


def load_tasks():
    if not os.path.exists(TASK_FILE):
        return []

    with open(TASK_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_tasks(tasks):
    with open(TASK_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=4)


def get_task_by_id(task_id):
    for task in load_tasks():
        if task["id"] == task_id:
            return task
    return None


def add_task(task_data):
    tasks = load_tasks()
    task_data.setdefault("date", datetime.now().strftime("%Y-%m-%d"))
    tasks.append(task_data)
    save_tasks(tasks)


def get_pending_tasks():
    tasks = load_tasks()
    return [task for task in tasks if task.get("status") in ACTIVE_STATUSES]


def update_task_status(task_id, new_status):
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            task["status"] = new_status
    save_tasks(tasks)


def change_task_status(task_id, new_status):
    task = get_task_by_id(task_id)
    if not task:
        return None

    excel_path = update_existing_status(task["row"], new_status)
    update_task_status(task_id, new_status)
    return excel_path


def complete_tasks_by_ids(task_ids):
    if not task_ids:
        return None

    rows = []
    for task_id in task_ids:
        task = get_task_by_id(task_id)
        if task and task.get("row"):
            rows.append(task["row"])

    if not rows:
        return None

    path = complete_rows_in_excel(rows)
    for task_id in task_ids:
        update_task_status(task_id, "Completed")
    return path
