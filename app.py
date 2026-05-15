import streamlit as st
import re
import ollama
import matplotlib.pyplot as plt
from datetime import datetime

# ---------------- PAGE CONFIG ---------------- #

st.set_page_config(
    page_title="AI Scam Detector",
    page_icon="🛡️",
    layout="centered"
)

# ---------------- CUSTOM CSS ---------------- #

st.markdown("""
<style>

.stApp {
    background-color: #0e1117;
    color: white;
}

h1 {
    color: #00ffcc;
    text-align: center;
}

.stButton button {
    background-color: #00ffcc;
    color: black;
    border-radius: 10px;
    font-size: 16px;
    font-weight: bold;
    padding: 10px 20px;
}

.result-box {
    background-color: #1c1f26;
    padding: 15px;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ---------------- #

st.title("🛡️ AI Scam Detector")

st.markdown(
    "Analyze suspicious messages, emails, links, OTP scams, phishing attempts, and fraud texts using AI."
)

# ---------------- HISTORY ---------------- #

if "history" not in st.session_state:
    st.session_state.history = []

if "safe_count" not in st.session_state:
    st.session_state.safe_count = 0

if "scam_count" not in st.session_state:
    st.session_state.scam_count = 0

# ---------------- INPUT ---------------- #

message = st.text_area(
    "Enter suspicious message",
    height=220,
    placeholder="Paste suspicious message here..."
)

# ---------------- FILE UPLOAD ---------------- #

uploaded_file = st.file_uploader(
    "Upload text file (optional)",
    type=["txt"]
)

if uploaded_file:

    file_text = uploaded_file.read().decode("utf-8")

    message = file_text

    st.success("File uploaded successfully!")

# ---------------- ANALYZE BUTTON ---------------- #

if st.button("🔍 Analyze Message"):

    if not message.strip():

        st.error("Please enter a suspicious message.")

    else:

        # ---------------- SCAM KEYWORDS ---------------- #

        scam_keywords = [
            "otp",
            "urgent",
            "bank",
            "lottery",
            "winner",
            "free money",
            "click here",
            "verify now",
            "account blocked",
            "gift card",
            "crypto",
            "upi",
            "password"
        ]

        found_keywords = [
            word for word in scam_keywords
            if word.lower() in message.lower()
        ]

        # ---------------- URL DETECTION ---------------- #

        urls = re.findall(r'https?://\S+', message)

        # ---------------- EMAIL DETECTION ---------------- #

        emails = re.findall(r'\S+@\S+', message)

        # ---------------- PHONE DETECTION ---------------- #

        phones = re.findall(r'\d{10}', message)

        # ---------------- RISK SCORE ---------------- #

        risk_score = (
            len(found_keywords) * 10 +
            len(urls) * 20 +
            len(emails) * 10 +
            len(phones) * 5
        )

        risk_score = min(risk_score, 100)

        # ---------------- AI ANALYSIS ---------------- #

        with st.spinner("🛡️ Scanning for phishing and scam threats..."):

            try:

                response = ollama.chat(
                    model='gemma:2b',
                    messages=[
                        {
                            'role': 'system',
                            'content': '''
You are a cybersecurity expert.

Analyze the message carefully.

Detect:
- phishing
- scam attempts
- fake rewards
- urgency tactics
- banking fraud
- OTP fraud
- suspicious links

Provide response in this format:

Status:
Category:
Confidence:
Reason:
Safety Tips:
'''
                        },
                        {
                            'role': 'user',
                            'content': message
                        }
                    ]
                )

                analysis = response['message']['content']

                # ---------------- SHOW RESULT ---------------- #

                st.success("Analysis Complete")

                st.markdown("## 📋 AI Analysis")

                st.code(analysis)

                # ---------------- RISK METER ---------------- #

                st.markdown("## 🚨 Risk Meter")

                st.progress(risk_score)

                st.write(f"Risk Score: {risk_score}%")

                # ---------------- THREAT LEVEL ---------------- #

                if risk_score < 30:
                    st.success("🟢 LOW RISK")

                elif risk_score < 70:
                    st.warning("🟡 MEDIUM RISK")

                else:
                    st.error("🔴 HIGH RISK")

                # ---------------- KEYWORDS ---------------- #

                if found_keywords:

                    st.warning(
                        f"⚠️ Suspicious Keywords Found: {', '.join(found_keywords)}"
                    )

                # ---------------- URLS ---------------- #

                if urls:

                    st.info(f"🔗 Detected URLs: {urls}")

                # ---------------- EMAILS ---------------- #

                if emails:

                    st.info(f"📧 Detected Emails: {emails}")

                # ---------------- PHONES ---------------- #

                if phones:

                    st.info(f"📱 Detected Phone Numbers: {phones}")

                # ---------------- SAFETY TIPS ---------------- #

                st.markdown("## 🛡️ Safety Tips")

                tips = [
                    "Never share OTP or passwords.",
                    "Avoid clicking suspicious links.",
                    "Verify sender identity.",
                    "Use official banking apps only.",
                    "Block suspicious numbers immediately."
                ]

                for tip in tips:
                    st.write("✅", tip)

                # ---------------- DOWNLOAD REPORT ---------------- #

                st.download_button(
                    label="📥 Download Report",
                    data=analysis,
                    file_name="scam_report.txt",
                    mime="text/plain"
                )

                # ---------------- STORE HISTORY ---------------- #

                st.session_state.history.append({
                    "message": message,
                    "result": analysis,
                    "time": datetime.now().strftime("%H:%M:%S")
                })

                # ---------------- COUNT SAFE/SCAM ---------------- #

                if "SCAM" in analysis.upper():

                    st.session_state.scam_count += 1

                else:

                    st.session_state.safe_count += 1

            except Exception as e:

                st.error(f"Error: {e}")

# ---------------- HISTORY ---------------- #

if st.session_state.history:

    st.markdown("---")

    st.markdown("## 📜 Previous Scans")

    for item in reversed(st.session_state.history[-5:]):

        with st.expander(f"Scan at {item['time']}"):

            st.write("### Message")
            st.write(item["message"])

            st.write("### Result")
            st.code(item["result"])

# ---------------- ANALYTICS ---------------- #

if (
    st.session_state.safe_count > 0 or
    st.session_state.scam_count > 0
):

    st.markdown("---")

    st.markdown("## 📊 Scam Analytics")

    labels = ['Safe', 'Scam']

    sizes = [
        st.session_state.safe_count,
        st.session_state.scam_count
    ]

    fig, ax = plt.subplots()

    ax.pie(
        sizes,
        labels=labels,
        autopct='%1.1f%%'
    )

    st.pyplot(fig)

# ---------------- FOOTER ---------------- #

st.markdown("---")

st.markdown(
    "⚠️ Stay alert against phishing, fake banking alerts, and online fraud."
)