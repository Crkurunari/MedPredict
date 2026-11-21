import streamlit as st
import pandas as pd
from datetime import date
from io import BytesIO

st.set_page_config(page_title="MediPredict AI", page_icon="🩺", layout="wide")

# Session state
if "profile" not in st.session_state:
    st.session_state.profile = {}
if "history" not in st.session_state:
    st.session_state.history = []
if "symptoms" not in st.session_state:
    st.session_state.symptoms = []
if "analysis" not in st.session_state:
    st.session_state.analysis = None

# Theme CSS
st.markdown("""
<style>
    .stApp { background: #f4f9fb; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg,#063c49,#07505c); }
    [data-testid="stSidebar"] * { color: #f4ffff !important; }
    .hero { background: linear-gradient(120deg,#e1f8f4,#eaf4ff); padding: 28px 32px; border-radius: 22px; border: 1px solid #d2ece9; }
    .hero h1 { color: #075365; font-size: 2.6rem; margin-bottom: 0; }
    .hero p { color: #23485a; font-size: 1.1rem; }
    .small-note { color: #607384; font-size: .9rem; }
    div[data-testid="stMetric"] { background: white; border: 1px solid #e0edf2; padding: 14px; border-radius: 14px; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🩺 MediPredict AI")
    st.caption("Your health history. Smarter health insights.")
    page = st.radio("Navigate", ["Home", "Health Profile", "Medical History", "AI Analysis", "Results", "About"])
    st.markdown("---")
    st.info("Demo privacy note: This prototype stores entries only in the current session. Avoid entering real, sensitive medical details.")

def make_summary():
    p = st.session_state.profile
    return {
        "Age": p.get("age", "Not entered"),
        "Recorded medical entries": len(st.session_state.history),
        "Symptom notes": len(st.session_state.symptoms),
        "Last analysis": "Completed" if st.session_state.analysis else "Not yet"
    }

def demo_analysis():
    """Educational summary of entries. Not a diagnosis or validated risk prediction."""
    p = st.session_state.profile
    history = st.session_state.history
    symptoms = st.session_state.symptoms
    observations = []
    next_steps = [
        "Use this report as a prompt for a conversation with a qualified healthcare professional.",
        "Keep medical records and medication lists updated, and seek care if symptoms are new, worsening, or concerning."
    ]
    if not p:
        observations.append("No profile information has been entered yet. Add a profile and medical-history entries to personalize this educational summary.")
    if history:
        conditions = [x["Condition/record"].strip() for x in history if x.get("Condition/record","").strip()]
        if conditions:
            observations.append(f"You entered {len(conditions)} medical-history record(s). This app organizes them but cannot determine what they mean medically.")
        dates = [x["Date"] for x in history if x.get("Date")]
        if dates:
            observations.append(f"Records span {min(dates)} to {max(dates)} based on the dates entered.")
    if symptoms:
        observations.append(f"You entered {len(symptoms)} symptom note(s). Consider tracking when they occur, how long they last, and whether they change.")
    if not history and not symptoms:
        observations.append("There are no medical-history or symptom records to summarize yet.")
    return {
        "observations": observations,
        "suggestions": next_steps,
        "disclaimer": "This is a classroom demonstration using simple summaries—not a trained medical model, diagnosis, or validated illness prediction."
    }

if page == "Home":
    st.markdown("""
    <div class="hero">
      <h1>Welcome to MediPredict AI</h1>
      <p>Organize past health information and explore simple, educational health insights.</p>
    </div>
    """, unsafe_allow_html=True)
    st.write("")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Medical records", len(st.session_state.history))
    c2.metric("Symptom notes", len(st.session_state.symptoms))
    c3.metric("Profile", "Complete" if st.session_state.profile else "Not started")
    c4.metric("Analysis", "Ready" if st.session_state.analysis else "Not run")
    st.subheader("How it works")
    a,b,c = st.columns(3)
    with a:
        st.markdown("### ① Enter your details")
        st.write("Add basic profile information and medical-history notes.")
    with b:
        st.markdown("### ② Review your information")
        st.write("The demo organizes entries and summarizes them.")
    with c:
        st.markdown("### ③ View your report")
        st.write("Read a simple report and download it for your project.")
    st.success("Start by opening Health Profile or Medical History in the sidebar.")
    st.warning("This school prototype does not diagnose or predict actual illnesses.")

elif page == "Health Profile":
    st.title("👤 Health Profile")
    with st.form("profile_form"):
        current = st.session_state.profile
        age = st.number_input("Age", min_value=0, max_value=120, value=int(current.get("age", 18)))
        name = st.text_input("Name or nickname (optional)", value=current.get("name", ""))
        family = st.text_area("Family medical history (optional)", value=current.get("family_history", ""), placeholder="You can list family health conditions, or leave blank.")
        lifestyle = st.selectbox("General activity level (optional)", ["Prefer not to say", "Mostly sitting", "Some activity", "Regular activity"], index=["Prefer not to say","Mostly sitting","Some activity","Regular activity"].index(current.get("lifestyle","Prefer not to say")))
        submitted = st.form_submit_button("Save Profile")
        if submitted:
            st.session_state.profile = {"age": age, "name": name, "family_history": family, "lifestyle": lifestyle}
            st.success("Profile saved for this session.")

elif page == "Medical History":
    st.title("📋 Medical History")
    st.caption("Add records you want to organize. Do not enter sensitive real-life details in this classroom demo.")
    with st.form("history_form", clear_on_submit=True):
        condition = st.text_input("Condition / record", placeholder="Example: seasonal allergy (sample)")
        record_date = st.date_input("Date (approximate is okay)", value=date.today())
        details = st.text_area("Notes (optional)", placeholder="Brief description or notes")
        add = st.form_submit_button("Add record")
        if add:
            if condition.strip():
                st.session_state.history.append({"Condition/record": condition.strip(), "Date": str(record_date), "Notes": details.strip()})
                st.success("Record added.")
            else:
                st.error("Please enter a condition or record name.")
    st.subheader("Saved entries")
    if st.session_state.history:
        st.dataframe(pd.DataFrame(st.session_state.history), use_container_width=True, hide_index=True)
        if st.button("Clear medical history"):
            st.session_state.history = []
            st.session_state.analysis = None
            st.rerun()
    else:
        st.info("No entries yet.")

elif page == "AI Analysis":
    st.title("🤖 Educational Health Analysis")
    st.write("This demo summarizes the information entered. It does not use a medical prediction model.")
    with st.form("symptom_form", clear_on_submit=True):
        symptom = st.text_input("Symptom note (optional)", placeholder="Example: occasional headache (sample)")
        duration = st.text_input("Duration / timing (optional)", placeholder="Example: noticed this week")
        submit_symptom = st.form_submit_button("Add symptom note")
        if submit_symptom:
            if symptom.strip():
                st.session_state.symptoms.append({"Symptom": symptom.strip(), "Timing": duration.strip()})
                st.success("Symptom note added.")
            else:
                st.error("Enter a symptom note, or leave this section and analyze your records.")
    st.markdown("---")
    if st.button("Analyze entered information", type="primary", use_container_width=True):
        st.session_state.analysis = demo_analysis()
        st.success("Educational summary created.")
    if st.session_state.analysis:
        st.subheader("Summary preview")
        for item in st.session_state.analysis["observations"]:
            st.write("•", item)
        st.caption("See Results for the full report.")

elif page == "Results":
    st.title("📊 Results")
    if not st.session_state.analysis:
        st.info("No report yet. Go to AI Analysis and click “Analyze entered information”.")
    else:
        st.subheader("Your information summary")
        for item in st.session_state.analysis["observations"]:
            st.markdown(f"- {item}")
        st.subheader("General next steps")
        for item in st.session_state.analysis["suggestions"]:
            st.markdown(f"- {item}")
        st.warning(st.session_state.analysis["disclaimer"])
        profile = st.session_state.profile
        report_text = "MediPredict AI — Educational Report\n\n"
        report_text += f"Age: {profile.get('age','Not entered')}\n"
        report_text += f"Medical-history entries: {len(st.session_state.history)}\n"
        report_text += f"Symptom notes: {len(st.session_state.symptoms)}\n\n"
        report_text += "Observations:\n" + "\n".join("- " + x for x in st.session_state.analysis["observations"])
        report_text += "\n\nGeneral next steps:\n" + "\n".join("- " + x for x in st.session_state.analysis["suggestions"])
        report_text += "\n\n" + st.session_state.analysis["disclaimer"]
        st.download_button("⬇️ Download report (.txt)", data=report_text, file_name="medipredict_report.txt", mime="text/plain")
        if st.session_state.history:
            st.subheader("Medical-history entries")
            st.dataframe(pd.DataFrame(st.session_state.history), use_container_width=True, hide_index=True)
        if st.session_state.symptoms:
            st.subheader("Symptom notes")
            st.dataframe(pd.DataFrame(st.session_state.symptoms), use_container_width=True, hide_index=True)

elif page == "About":
    st.title("ℹ️ About MediPredict AI")
    st.markdown("""
    **MediPredict AI** is a Class 12 AI project prototype that demonstrates how an app can collect and organize health-history information and generate a simple summary.

    **Project workflow:** Input → Organize information → Summarize → Report

    This prototype uses basic rules and summaries—not a trained machine-learning model. It must not be used to diagnose illness, predict disease, or guide treatment.
    """)
    st.subheader("Privacy and safety")
    st.write("The demo keeps information in the current browser session's app state. For a school demonstration, use fictional sample data rather than real health details.")
