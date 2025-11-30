#!/usr/bin/env python3
"""
Task Tracker CLI (task_cli.py)

Usage (examples):
  python task_cli.py add "Buy groceries"
  python task_cli.py update 1 "Buy groceries and cook dinner"
  python task_cli.py delete 1
  python task_cli.py mark-in-progress 1
  python task_cli.py mark-done 1
  python task_cli.py list
  python task_cli.py list done
  python task_cli.py list todo
  python task_cli.py list in-progress

Notes:
 - This script uses a `tasks.json` file in the current working directory to store tasks.
 - No external libraries required.
 - IDs are integers assigned incrementally.

Each task object stored in tasks.json has these properties:
  id (int), description (str), status ("todo"|"in-progress"|"done"),
  createdAt (ISO 8601 utc string), updatedAt (ISO 8601 utc string)

"""

import sys
import json
from pathlib import Path
from datetime import datetime

TASKS_FILE = Path("tasks.json")
VALID_STATUSES = {"todo", "in-progress", "done"}


def now_iso():
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def load_tasks():
    if not TASKS_FILE.exists():
        return []
    try:
        with TASKS_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, list):
                print("Corrupt tasks file: expected a list. Resetting to empty.")
                return []
            return data
    except json.JSONDecodeError:
        print("Corrupt JSON in tasks file. Resetting to empty.")
        return []


def save_tasks(tasks):
    with TASKS_FILE.open("w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)


def next_id(tasks):
    if not tasks:
        return 1
    return max(task.get("id", 0) for task in tasks) + 1


def find_task(tasks, task_id):
    for task in tasks:
        if task.get("id") == task_id:
            return task
    return None


def cmd_add(args):
    if len(args) < 1:
        print("Usage: add \"description\"")
        return
    description = args[0]
    tasks = load_tasks()
    tid = next_id(tasks)
    ts = now_iso()
    task = {
        "id": tid,
        "description": description,
        "status": "todo",
        "createdAt": ts,
        "updatedAt": ts,
    }
    tasks.append(task)
    save_tasks(tasks)
    print(f"Task added successfully (ID: {tid})")


def cmd_update(args):
    if len(args) < 2:
        print("Usage: update <id> \"new description\"")
        return
    try:
        tid = int(args[0])
    except ValueError:
        print("Invalid id. Id must be an integer.")
        return
    new_description = args[1]
    tasks = load_tasks()
    task = find_task(tasks, tid)
    if not task:
        print(f"Task with ID {tid} not found.")
        return
    task["description"] = new_description
    task["updatedAt"] = now_iso()
    save_tasks(tasks)
    print(f"Task {tid} updated successfully.")


def cmd_delete(args):
    if len(args) < 1:
        print("Usage: delete <id>")
        return
    try:
        tid = int(args[0])
    except ValueError:
        print("Invalid id. Id must be an integer.")
        return
    tasks = load_tasks()
    task = find_task(tasks, tid)
    if not task:
        print(f"Task with ID {tid} not found.")
        return
    tasks = [t for t in tasks if t.get("id") != tid]
    save_tasks(tasks)
    print(f"Task {tid} deleted successfully.")


def cmd_mark(args, status):
    if len(args) < 1:
        print(f"Usage: mark-{status} <id>")
        return
    try:
        tid = int(args[0])
    except ValueError:
        print("Invalid id. Id must be an integer.")
        return
    tasks = load_tasks()
    task = find_task(tasks, tid)
    if not task:
        print(f"Task with ID {tid} not found.")
        return
    task["status"] = status
    task["updatedAt"] = now_iso()
    save_tasks(tasks)
    print(f"Task {tid} marked as {status}.")


def cmd_list(args):
    status_filter = None
    if args:
        status_filter = args[0].lower()
        if status_filter == "todo":
            status_filter = "todo"
        elif status_filter in ("in-progress", "inprogress", "in_progress"):
            status_filter = "in-progress"
        elif status_filter in ("done", "completed"):
            status_filter = "done"
        elif status_filter == "all":
            status_filter = None
        elif status_filter not in VALID_STATUSES:
            print("Invalid status filter. Use: all | todo | in-progress | done")
            return

    tasks = load_tasks()
    if not tasks:
        print("No tasks found.")
        return

    def fmt(t):
        return f"[{t['id']}] ({t['status']}) {t['description']}  - created: {t['createdAt']} updated: {t['updatedAt']}"

    filtered = tasks if status_filter is None else [t for t in tasks if t.get("status") == status_filter]
    if not filtered:
        print("No tasks match the filter.")
        return
    for t in filtered:
        print(fmt(t))


def print_help():
    print("Task Tracker CLI")
    print("Usage:")
    print("  add \"description\"")
    print("  update <id> \"new description\"")
    print("  delete <id>")
    print("  mark-in-progress <id>")
    print("  mark-done <id>")
    print("  list [all|todo|in-progress|done]")


def main():
    if len(sys.argv) < 2:
        print_help()
        return
    cmd = sys.argv[1].lower()
    args = sys.argv[2:]

    if cmd == "add":
        # join remaining args so users don't need to quote perfectly
        if not args:
            print("Usage: add \"description\"")
        else:
            cmd_add([" ".join(args)])
    elif cmd == "update":
        if len(args) < 2:
            print("Usage: update <id> \"new description\"")
        else:
            tid = args[0]
            desc = " ".join(args[1:])
            cmd_update([tid, desc])
    elif cmd == "delete":
        cmd_delete(args)
    elif cmd == "mark-in-progress":
        cmd_mark(args, "in-progress")
    elif cmd == "mark-done":
        cmd_mark(args, "done")
    elif cmd == "list":
        cmd_list(args)
    elif cmd in ("-h", "--help", "help"):
        print_help()
    else:
        print(f"Unknown command: {cmd}")
        print_help()


if __name__ == "__main__":
    main()
