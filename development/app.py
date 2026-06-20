"""
AI Based Healthcare System — Streamlit Frontend
=================================================
College mini project.

This file is ONLY the frontend (UI layer) of the pipeline.
It currently uses MOCK / placeholder logic wherever a real trained
model, database, or external API (Twilio, Maps, etc.) would normally
plug in. Look for the "# TODO(backend)" comments — that is exactly
where your Backend Development + Model Saving + Database Integration
stages connect into this UI.

Run with:
    streamlit run app.py

Install dependencies first:
    pip install streamlit pandas
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date, time as dtime

# -------------------------------------------------------------------
# PAGE CONFIG — must be the first Streamlit command
# -------------------------------------------------------------------
st.set_page_config(
    page_title="AI Healthcare Assistant",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------------------------------------------------------
# SESSION STATE INITIALIZATION
# -------------------------------------------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "Hi, I'm your AI Health Assistant. How are you feeling today?"}
    ]

if "medications" not in st.session_state:
    # Each entry: {"name": str, "dosage": str, "time": time, "taken_today": bool}
    st.session_state.medications = []

if "mood_log" not in st.session_state:
    # Each entry: {"date": date, "mood_score": int, "note": str}
    st.session_state.mood_log = []

if "sos_triggered" not in st.session_state:
    st.session_state.sos_triggered = False


# -------------------------------------------------------------------
# MOCK BACKEND FUNCTIONS
# Replace these with real calls to your trained models / APIs.
# -------------------------------------------------------------------

def get_bot_response(user_message: str) -> str:
    """
    TODO(backend): Replace this with a call to your trained NLP model
    (e.g. intent classifier + symptom checker model loaded via
    pickle/joblib, or a call to an LLM API).

    Example real integration:
        from model_utils import predict_intent, predict_symptom_severity
        intent = predict_intent(user_message)
        ...
    """
    text = user_message.lower()

    emergency_keywords = ["chest pain", "can't breathe", "cannot breathe", "suicidal", "unconscious", "heavy bleeding"]
    if any(k in text for k in emergency_keywords):
        st.session_state.sos_triggered = True
        return ("⚠️ This sounds like it could be a medical emergency. "
                "I've flagged this for an SOS alert — please check the Emergency tab, "
                "or call your local emergency number immediately.")

    if "sad" in text or "depressed" in text or "anxious" in text:
        return ("I'm sorry you're feeling this way. On a scale of 1–10, how would you rate your mood today? "
                "You can also log it in the Mental Health tab.")

    if "headache" in text or "fever" in text or "cough" in text:
        return ("Thanks for sharing your symptoms. Based on what you described, this could range from a mild "
                "viral infection to something needing attention. Please use the Symptom Checker tab for a "
                "more structured assessment. This is not a medical diagnosis.")

    return "Got it — tell me more about your symptoms, or use the sidebar to navigate to a specific feature."


def check_symptoms(symptom_list: list, severity: int) -> dict:
    """
    TODO(backend): Replace with your trained triage model
    (e.g. Random Forest / classification model from the Model Saving stage).
    """
    risk = "Low"
    if severity >= 8 or len(symptom_list) >= 4:
        risk = "High"
    elif severity >= 5:
        risk = "Medium"

    return {
        "risk_level": risk,
        "advice": {
            "Low": "Monitor your symptoms. Rest and stay hydrated.",
            "Medium": "Consider consulting a doctor within the next 24-48 hours.",
            "High": "Please seek medical attention soon. Consider using the SOS feature if this worsens.",
        }[risk],
    }


def trigger_ambulance_call(location: str) -> str:
    """
    TODO(backend): Replace with a real integration, e.g.:
      - Twilio Voice/SMS API to call/notify emergency contacts
      - Google Maps API to find nearest hospital
      - A direct webhook to a local emergency dispatch partner

    For a college project, simulating this call and logging it is
    usually sufficient — calling real emergency services from a demo
    app would be inappropriate / unsafe.
    """
    return f"📞 [SIMULATED] Ambulance dispatch requested for location: '{location}'. In production, this would call Twilio/Maps APIs."


# -------------------------------------------------------------------
# SIDEBAR — NAVIGATION
# -------------------------------------------------------------------
st.sidebar.title("🩺 AI Healthcare Assistant")
st.sidebar.caption("College mini project — Streamlit frontend")

page = st.sidebar.radio(
    "Navigate",
    [
        "💬 Chatbot",
        "🤒 Symptom Checker",
        "🧠 Mental Health",
        "💊 Medication Reminder",
        "📟 Device Alerts",
        "🚑 Emergency / SOS",
    ],
)

if st.session_state.sos_triggered:
    st.sidebar.error("⚠️ SOS alert active — go to Emergency tab")

st.sidebar.markdown("---")
st.sidebar.caption("This app is a student project and does not provide real medical advice. "
                    "In a real emergency, call your local emergency number directly.")


# -------------------------------------------------------------------
# PAGE 1 — CHATBOT
# -------------------------------------------------------------------
if page == "💬 Chatbot":
    st.title("💬 Health Chat Assistant")
    st.caption("Describe how you're feeling. The assistant routes urgent cases to the SOS tab automatically.")

    # Render chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Chat input
    user_input = st.chat_input("Type your message...")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        bot_reply = get_bot_response(user_input)
        st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
        with st.chat_message("assistant"):
            st.write(bot_reply)

        if st.session_state.sos_triggered:
            st.rerun()


# -------------------------------------------------------------------
# PAGE 2 — SYMPTOM CHECKER
# -------------------------------------------------------------------
elif page == "🤒 Symptom Checker":
    st.title("🤒 Symptom Checker")
    st.caption("Select your symptoms and rate their severity for a quick triage suggestion.")

    common_symptoms = [
        "Fever", "Cough", "Headache", "Fatigue", "Nausea",
        "Shortness of breath", "Chest pain", "Sore throat",
        "Body ache", "Dizziness",
    ]

    selected_symptoms = st.multiselect("Select your symptoms", common_symptoms)
    severity = st.slider("Overall severity (1 = mild, 10 = severe)", 1, 10, 3)
    duration = st.selectbox("How long have you had these symptoms?", ["< 1 day", "1-3 days", "3-7 days", "> 1 week"])

    if st.button("Check symptoms", type="primary"):
        if not selected_symptoms:
            st.warning("Please select at least one symptom.")
        else:
            result = check_symptoms(selected_symptoms, severity)
            color = {"Low": "success", "Medium": "warning", "High": "error"}[result["risk_level"]]
            getattr(st, color)(f"Risk level: {result['risk_level']}")
            st.write(result["advice"])

            if result["risk_level"] == "High":
                st.info("Would you like to trigger an SOS alert? Go to the Emergency tab.")

    st.divider()
    st.caption("⚠️ This tool does not provide a medical diagnosis. Always consult a licensed physician.")


# -------------------------------------------------------------------
# PAGE 3 — MENTAL HEALTH
# -------------------------------------------------------------------
elif page == "🧠 Mental Health":
    st.title("🧠 Mental Health Check-in")
    st.caption("Track your mood over time and get a supportive response.")

    col1, col2 = st.columns([2, 1])

    with col1:
        mood_score = st.slider("How would you rate your mood today?", 1, 10, 5)
        note = st.text_area("Anything you'd like to note? (optional)")

        if st.button("Log my mood", type="primary"):
            st.session_state.mood_log.append({
                "date": date.today(),
                "mood_score": mood_score,
                "note": note,
            })
            if mood_score <= 3:
                st.warning("It sounds like things are tough right now. Consider reaching out to a mental "
                           "health professional or a trusted person. You don't have to go through this alone.")
            else:
                st.success("Mood logged. Thanks for checking in with yourself today.")

    with col2:
        st.metric("Entries logged", len(st.session_state.mood_log))

    if st.session_state.mood_log:
        st.subheader("Mood history")
        df = pd.DataFrame(st.session_state.mood_log)
        st.line_chart(df.set_index("date")["mood_score"])
        st.dataframe(df, use_container_width=True)

    st.divider()
    st.caption("⚠️ If you are in crisis or having thoughts of self-harm, please contact a crisis helpline "
               "or emergency services in your area immediately.")


# -------------------------------------------------------------------
# PAGE 4 — MEDICATION REMINDER
# -------------------------------------------------------------------
elif page == "💊 Medication Reminder":
    st.title("💊 Medication Reminder")
    st.caption("Add medications and track whether you've taken today's dose.")

    with st.form("add_medication_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            med_name = st.text_input("Medication name")
        with c2:
            dosage = st.text_input("Dosage (e.g. 500mg)")
        with c3:
            reminder_time = st.time_input("Reminder time", value=dtime(9, 0))

        submitted = st.form_submit_button("Add medication")
        if submitted:
            if med_name.strip() == "":
                st.warning("Please enter a medication name.")
            else:
                st.session_state.medications.append({
                    "name": med_name,
                    "dosage": dosage,
                    "time": reminder_time,
                    "taken_today": False,
                })
                st.success(f"Added {med_name}.")

    st.divider()

    if not st.session_state.medications:
        st.info("No medications added yet.")
    else:
        st.subheader("Today's schedule")
        for i, med in enumerate(st.session_state.medications):
            c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
            c1.write(f"**{med['name']}**")
            c2.write(med["dosage"] or "—")
            c3.write(med["time"].strftime("%I:%M %p"))
            taken = c4.checkbox("Taken", value=med["taken_today"], key=f"taken_{i}")
            st.session_state.medications[i]["taken_today"] = taken

        # TODO(backend): Replace with a real scheduler — e.g. APScheduler running
        # server-side, or push notifications, to actually alert the user at
        # reminder_time instead of relying on the user having the app open.


# -------------------------------------------------------------------
# PAGE 5 — DEVICE ALERTS
# -------------------------------------------------------------------
elif page == "📟 Device Alerts":
    st.title("📟 Connected Device Alerts")
    st.caption("Simulated readings from a wearable device. In production this would pull from a real device API "
               "(e.g. Fitbit, Apple Health, a custom IoT sensor).")

    # TODO(backend): Replace with real device API polling / webhook ingestion,
    # stored via the Database Integration stage.
    c1, c2, c3 = st.columns(3)
    heart_rate = c1.number_input("Heart rate (bpm)", min_value=30, max_value=220, value=78)
    spo2 = c2.number_input("Blood oxygen (SpO2 %)", min_value=50, max_value=100, value=97)
    temp = c3.number_input("Body temperature (°C)", min_value=30.0, max_value=43.0, value=36.8, step=0.1)

    if st.button("Check vitals", type="primary"):
        alerts = []
        if heart_rate > 120 or heart_rate < 45:
            alerts.append(f"Abnormal heart rate detected: {heart_rate} bpm")
        if spo2 < 92:
            alerts.append(f"Low blood oxygen detected: {spo2}%")
        if temp > 38.5:
            alerts.append(f"High fever detected: {temp}°C")

        if alerts:
            for a in alerts:
                st.error(a)
            st.warning("One or more vitals are outside normal range. Consider checking the Emergency tab.")
        else:
            st.success("All vitals look within normal range.")


# -------------------------------------------------------------------
# PAGE 6 — EMERGENCY / SOS
# -------------------------------------------------------------------
elif page == "🚑 Emergency / SOS":
    st.title("🚑 Emergency / SOS")

    if st.session_state.sos_triggered:
        st.error("An SOS condition was detected from your recent chat or vitals.")

    st.write("Press the button below to simulate calling an ambulance to your location.")

    location = st.text_input("Your current location / address", placeholder="e.g. 123 MG Road, Bengaluru")

    if st.button("🚨 CALL AMBULANCE NOW", type="primary", use_container_width=True):
        if location.strip() == "":
            st.warning("Please enter your location first.")
        else:
            result = trigger_ambulance_call(location)
            st.success(result)
            st.session_state.sos_triggered = False

    st.divider()
    st.subheader("Emergency contacts")
    st.write("- Local emergency number: **112** (India) / **911** (US) / **999** (UK)")
    st.write("- Add your personal emergency contacts here in a future version, stored via the Database "
             "Integration stage.")

    st.caption("⚠️ For a real college project demo, this button should remain simulated. Do NOT wire this "
               "directly to real emergency dispatch without proper authorization and safety review.")
