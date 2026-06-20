"""
AI Based Healthcare System — Backend
======================================
College mini project.

This module contains all the "backend" logic: a tiny rule-based NLP
intent detector, a symptom triage scorer, a mental-health mood
evaluator, SQLite persistence, and a simulated ambulance dispatch
function.

It has ZERO Streamlit imports — it is pure Python so it can be reused,
unit-tested, or swapped for real ML models later without touching the
frontend.

Folder structure expected:

    project/
      backend/
        backend.py    <-- this file
        healthcare.db  (auto-created on first run)
      frontend/
        app.py

Run a quick self-test with:
    python backend.py
"""

import sqlite3
import os
from datetime import datetime, date


# -------------------------------------------------------------------
# DATABASE SETUP
# -------------------------------------------------------------------
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "healthcare.db")


def get_connection():
    """Returns a new SQLite connection. Call close() on it when done,
    or use it as a context manager."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Creates all required tables if they don't already exist.
    Safe to call every time the app starts."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS chat_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS mood_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mood_score INTEGER NOT NULL,
            note TEXT,
            log_date TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS medications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            dosage TEXT,
            reminder_time TEXT,
            taken_today INTEGER DEFAULT 0
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS sos_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT NOT NULL,
            reason TEXT,
            timestamp TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# -------------------------------------------------------------------
# CHAT LOGGING
# -------------------------------------------------------------------
def save_chat_message(role: str, message: str):
    conn = get_connection()
    conn.execute(
        "INSERT INTO chat_log (role, message, timestamp) VALUES (?, ?, ?)",
        (role, message, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def get_chat_history(limit: int = 50):
    conn = get_connection()
    rows = conn.execute(
        "SELECT role, message, timestamp FROM chat_log ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in reversed(rows)]


# -------------------------------------------------------------------
# CHATBOT / SYMPTOM NLP (rule-based placeholder for a trained model)
# -------------------------------------------------------------------
EMERGENCY_KEYWORDS = [
    "chest pain", "can't breathe", "cannot breathe", "suicidal",
    "unconscious", "heavy bleeding", "severe bleeding", "not breathing",
]

MENTAL_HEALTH_KEYWORDS = ["sad", "depressed", "anxious", "hopeless", "stressed", "panic"]

SYMPTOM_KEYWORDS = ["headache", "fever", "cough", "nausea", "fatigue", "dizziness", "sore throat"]


def get_bot_response(user_message: str) -> dict:
    """
    TODO(model): Replace this rule-based logic with a real trained
    intent-classification model, e.g.:

        import joblib
        clf = joblib.load("models/intent_classifier.pkl")
        intent = clf.predict([user_message])[0]

    Returns a dict: {"reply": str, "sos_triggered": bool}
    """
    text = user_message.lower()

    if any(k in text for k in EMERGENCY_KEYWORDS):
        return {
            "reply": ("⚠️ This sounds like it could be a medical emergency. "
                      "I've flagged this for an SOS alert — please check the Emergency tab, "
                      "or call your local emergency number immediately."),
            "sos_triggered": True,
        }

    if any(k in text for k in MENTAL_HEALTH_KEYWORDS):
        return {
            "reply": ("I'm sorry you're feeling this way. On a scale of 1-10, how would you rate your mood today? "
                      "You can also log it in the Mental Health tab."),
            "sos_triggered": False,
        }

    if any(k in text for k in SYMPTOM_KEYWORDS):
        return {
            "reply": ("Thanks for sharing your symptoms. This could range from a mild issue to something needing "
                      "attention. Please use the Symptom Checker tab for a more structured assessment. "
                      "This is not a medical diagnosis."),
            "sos_triggered": False,
        }

    return {
        "reply": "Got it - tell me more about your symptoms, or use the sidebar to navigate to a specific feature.",
        "sos_triggered": False,
    }


# -------------------------------------------------------------------
# SYMPTOM TRIAGE (rule-based placeholder for a trained classifier)
# -------------------------------------------------------------------
def check_symptoms(symptom_list: list, severity: int) -> dict:
    """
    TODO(model): Replace with your trained triage model
    (e.g. a Random Forest / classification model saved via joblib
    in the Model Saving stage):

        import joblib
        model = joblib.load("models/triage_model.pkl")
        risk = model.predict([[len(symptom_list), severity]])[0]
    """
    risk = "Low"
    if severity >= 8 or len(symptom_list) >= 4:
        risk = "High"
    elif severity >= 5:
        risk = "Medium"

    advice_map = {
        "Low": "Monitor your symptoms. Rest and stay hydrated.",
        "Medium": "Consider consulting a doctor within the next 24-48 hours.",
        "High": "Please seek medical attention soon. Consider using the SOS feature if this worsens.",
    }

    return {"risk_level": risk, "advice": advice_map[risk]}


# -------------------------------------------------------------------
# MENTAL HEALTH
# -------------------------------------------------------------------
def log_mood(mood_score: int, note: str = ""):
    conn = get_connection()
    conn.execute(
        "INSERT INTO mood_log (mood_score, note, log_date) VALUES (?, ?, ?)",
        (mood_score, note, date.today().isoformat()),
    )
    conn.commit()
    conn.close()

    return evaluate_mood(mood_score)


def evaluate_mood(mood_score: int) -> dict:
    """
    TODO(model): Replace with a trained sentiment/PHQ-9-style scoring
    model if you want something more rigorous than a threshold.
    """
    if mood_score <= 3:
        return {
            "level": "concerning",
            "message": ("It sounds like things are tough right now. Consider reaching out to a mental "
                        "health professional or a trusted person. You don't have to go through this alone."),
        }
    return {"level": "ok", "message": "Mood logged. Thanks for checking in with yourself today."}


def get_mood_history():
    conn = get_connection()
    rows = conn.execute("SELECT mood_score, note, log_date FROM mood_log ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


# -------------------------------------------------------------------
# MEDICATION REMINDERS
# -------------------------------------------------------------------
def add_medication(name: str, dosage: str, reminder_time: str):
    """reminder_time should be a string like '09:00 AM' (frontend formats this)."""
    conn = get_connection()
    conn.execute(
        "INSERT INTO medications (name, dosage, reminder_time, taken_today) VALUES (?, ?, ?, 0)",
        (name, dosage, reminder_time),
    )
    conn.commit()
    conn.close()


def get_medications():
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, name, dosage, reminder_time, taken_today FROM medications ORDER BY id"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def mark_medication_taken(med_id: int, taken: bool):
    conn = get_connection()
    conn.execute(
        "UPDATE medications SET taken_today = ? WHERE id = ?",
        (1 if taken else 0, med_id),
    )
    conn.commit()
    conn.close()

    # TODO(scheduler): For real reminders (not just tracking), integrate
    # APScheduler or a push-notification service here, keyed off reminder_time.


# -------------------------------------------------------------------
# DEVICE / VITALS ALERTS
# -------------------------------------------------------------------
def check_vitals(heart_rate: float, spo2: float, temperature_c: float) -> list:
    """
    TODO(device): Replace number_input simulation in the frontend with
    a real device API integration (Fitbit / Apple Health / custom IoT
    sensor webhook) and feed those readings into this same function.
    """
    alerts = []
    if heart_rate > 120 or heart_rate < 45:
        alerts.append(f"Abnormal heart rate detected: {heart_rate} bpm")
    if spo2 < 92:
        alerts.append(f"Low blood oxygen detected: {spo2}%")
    if temperature_c > 38.5:
        alerts.append(f"High fever detected: {temperature_c}C")
    return alerts


# -------------------------------------------------------------------
# EMERGENCY / SOS
# -------------------------------------------------------------------
def trigger_ambulance_call(location: str, reason: str = "User-triggered SOS") -> str:
    """
    TODO(integration): Replace this simulation with a real integration, e.g.:
      - Twilio Voice/SMS API to call/notify emergency contacts
      - Google Maps API to locate the nearest hospital
      - A webhook to a local emergency dispatch partner

    For a college project, simulating + logging this call is the
    appropriate (and safe) choice. Do not wire this to real dispatch
    services without proper authorization.
    """
    conn = get_connection()
    conn.execute(
        "INSERT INTO sos_log (location, reason, timestamp) VALUES (?, ?, ?)",
        (location, reason, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()

    return f"[SIMULATED] Ambulance dispatch requested for location: '{location}'. Reason: {reason}."


def get_sos_history():
    conn = get_connection()
    rows = conn.execute("SELECT location, reason, timestamp FROM sos_log ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


# -------------------------------------------------------------------
# SELF-TEST - run this file directly to sanity-check everything works
# -------------------------------------------------------------------
if __name__ == "__main__":
    init_db()
    print("Database initialized at:", DB_PATH)

    print("\n--- Chatbot test ---")
    print(get_bot_response("I have a bad headache and fever"))
    print(get_bot_response("I feel like I can't breathe"))

    print("\n--- Symptom checker test ---")
    print(check_symptoms(["Fever", "Cough", "Headache"], 7))

    print("\n--- Mood log test ---")
    print(log_mood(8, "Feeling good today"))
    print(get_mood_history())

    print("\n--- Medication test ---")
    add_medication("Paracetamol", "500mg", "09:00 AM")
    print(get_medications())

    print("\n--- Vitals test ---")
    print(check_vitals(130, 98, 37.0))

    print("\n--- SOS test ---")
    print(trigger_ambulance_call("123 MG Road, Bengaluru", reason="Self-test run"))
    print(get_sos_history())

    print("\nAll backend functions ran successfully.")
