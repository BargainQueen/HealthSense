import streamlit as st
import google.generativeai as genai
import speech_recognition as sr
from PIL import Image

# -------------------------
# Gemini Setup
# -------------------------

genai.configure(api_key="GEMINI_API_KEY")

model = genai.GenerativeModel("gemini-2.5-flash")

# -------------------------
# Page Setup
# -------------------------

st.set_page_config(page_title="HealthSense AI", layout="wide")

st.title("🩺 HealthSense – AI Medical Assistant")

# -------------------------
# Session State
# -------------------------

if "history" not in st.session_state:
    st.session_state.history = []

if "questions" not in st.session_state:
    st.session_state.questions = []

if "answers" not in st.session_state:
    st.session_state.answers = {}

# -------------------------
# Sidebar
# -------------------------

st.sidebar.title("HealthSense")

menu = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Symptom Diagnosis",
        "Medical Report Interpreter",
        "Medicine Safety Checker",
        "Nearby Hospitals"
    ]
)

# -------------------------
# Dashboard
# -------------------------

if menu == "Dashboard":

    st.header("HealthSense Dashboard")

    col1, col2, col3 = st.columns(3)

    col1.metric("AI Model", "Gemini")
    col2.metric("Tools", "4")
    col3.metric("Languages", "3")

    st.info(
        "HealthSense analyzes symptoms, medical reports "
        "and medicine safety using AI."
    )

# -------------------------
# Symptom Diagnosis
# -------------------------

elif menu == "Symptom Diagnosis":

    st.header("🩺 Symptom Diagnosis")

    symptoms = st.text_area("Enter symptoms")

    language = st.selectbox(
        "Explanation language",
        ["English", "Tamil", "Hindi"]
    )

    # Voice input
    if st.button("🎤 Speak Symptoms"):

        recognizer = sr.Recognizer()

        with sr.Microphone() as source:

            st.info("Listening...")

            audio = recognizer.listen(source)

            try:
                text = recognizer.recognize_google(audio)
                st.success(text)
                symptoms = text

            except:
                st.error("Voice recognition failed")

    # Emergency detection
    emergency_words = [
        "chest pain",
        "difficulty breathing",
        "unconscious",
        "severe bleeding"
    ]

    if any(word in symptoms.lower() for word in emergency_words):

        st.error("⚠ Possible medical emergency! Seek immediate help.")

    # Analyze symptoms
    if st.button("Analyze Symptoms"):

        prompt = f"""
        Symptoms: {symptoms}

        Provide:

        1 Possible diseases
        2 Disease probability
        3 Risk level (Low / Moderate / High)
        4 Recommended doctor
        5 Health advice
        6 Explanation in {language}
        7 Give Health Score from 0 to 100

        Then ask 3 follow-up medical questions.
        """

        response = model.generate_content(prompt)

        result = response.text

        st.subheader("AI Diagnosis")

        st.write(result)

        # Risk meter
        if "high" in result.lower():

            st.progress(90)
            st.error("High Risk")

        elif "moderate" in result.lower():

            st.progress(60)
            st.warning("Moderate Risk")

        else:

            st.progress(30)
            st.success("Low Risk")

        # Extract questions
        questions = []

        for line in result.split("\n"):
            if "?" in line:
                questions.append(line)

        st.session_state.questions = questions

        st.session_state.history.append(
            {"symptoms": symptoms, "result": result}
        )

# Follow-up questions

    if st.session_state.questions:

        st.subheader("AI Follow-up Questions")

        for q in st.session_state.questions:

            ans = st.text_input(q)

            st.session_state.answers[q] = ans

        if st.button("Refine Diagnosis"):

            answer_text = ""

            for q, a in st.session_state.answers.items():

                answer_text += f"{q} {a}\n"

            prompt2 = f"""
            Original symptoms:
            {symptoms}

            Patient answers:
            {answer_text}

            Update diagnosis, risk level and advice.
            """

            response2 = model.generate_content(prompt2)

            st.subheader("Refined Diagnosis")

            st.write(response2.text)

# -------------------------
# Medical Report Interpreter
# -------------------------

elif menu == "Medical Report Interpreter":

    st.header("📄 Medical Report Interpreter")

    uploaded_file = st.file_uploader(
        "Upload report image",
        type=["jpg", "png", "jpeg"]
    )

    if uploaded_file:

        image = Image.open(uploaded_file)

        st.image(image, caption="Uploaded Report")

        if st.button("Analyze Report"):

            response = model.generate_content(
                [
                    "Explain this medical report in simple language. "
                    "Provide risk level, key findings, and advice.",
                    image
                ]
            )

            result = response.text

            st.subheader("AI Report Explanation")

            st.write(result)

            st.download_button(
                "Download Explanation",
                result,
                file_name="healthsense_report.txt"
            )

# -------------------------
# Medicine Safety Checker
# -------------------------

elif menu == "Medicine Safety Checker":

    st.header("💊 Medicine Safety Checker")

    medicine = st.text_input("Medicine name")

    condition = st.text_input("Existing condition")

    if st.button("Check Safety"):

        prompt = f"""
        Medicine: {medicine}
        Patient condition: {condition}

        Is it safe?

        Provide side effects and warnings.
        """

        response = model.generate_content(prompt)

        st.write(response.text)

# -------------------------
# Nearby Hospitals
# -------------------------

elif menu == "Nearby Hospitals":

    st.header("📍 Nearby Hospitals")

    city = st.text_input("Enter your city")

    if city:

        link = f"https://www.google.com/maps/search/hospitals+near+{city}"

        st.markdown(f"[Open Hospitals in Google Maps]({link})")

# -------------------------
# History
# -------------------------

if st.session_state.history:

    st.subheader("Previous Analyses")

    for record in st.session_state.history[::-1]:

        st.write("Symptoms:", record["symptoms"])

        st.write(record["result"])

        st.write("---")

# -------------------------
# Disclaimer
# -------------------------

st.write("---")

st.caption(
    "HealthSense provides informational guidance only. "
    "It is not a medical diagnosis."
)
