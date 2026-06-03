import datetime
import os
import traceback
from typing import Optional
from execution.hud_server import broadcast

HISTORY_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "history.md")


def _write_entry(entry: str):
    os.makedirs(os.path.dirname(HISTORY_PATH), exist_ok=True)
    try:
        with open(HISTORY_PATH, "a", encoding="utf-8") as f:
            f.write(entry)
    except Exception as e:
        print(f"[Logger] Failed to write history entry: {e}")


def _format_entry(level: str, component: str, message: str, details: Optional[str] = None) -> str:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"{timestamp} | {level.upper()} | {component} | {message}"
    if details:
        entry += f" | {details}"
    return entry + "\n"


def log_info(component: str, message: str, details: Optional[str] = None):
    entry = _format_entry("INFO", component, message, details)
    print(f"[INFO] {component}: {message}")
    _write_entry(entry)
    broadcast("log", {"level": "info", "component": component, "message": message, "details": details})


def log_error(component: str, message: str, exc: Optional[Exception] = None, details: Optional[str] = None):
    trace = None
    if exc is not None:
        trace = traceback.format_exception_only(type(exc), exc)
        trace = "".join(trace).strip()
    combined = details or ""
    if trace:
        combined = f"{combined} | exception={trace}" if combined else f"exception={trace}"
    entry = _format_entry("ERROR", component, message, combined or None)
    print(f"[ERROR] {component}: {message}")
    if trace:
        print(trace)
    _write_entry(entry)
    broadcast("log", {"level": "error", "component": component, "message": message, "details": combined})


def log_action(component: str, action: str, target: str = "", result: str = ""):
    details = []
    if target:
        details.append(f"target={target}")
    if result:
        details.append(f"result={result}")
    log_info(component, action, "; ".join(details) if details else None)
