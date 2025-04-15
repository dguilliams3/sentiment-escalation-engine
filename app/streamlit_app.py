import streamlit as st
import json
import os

tab1, tab2, tab3, tab4 = st.tabs([
    "Feature 1: Classified Reviews",
    "Feature 2: Escalation Triggering",
    "Feature 3: Novelty Override Detection",
    "Feature 4: Decision Log"
])

with tab1:
    st.header("Sentiment Escalation Engine (Day 1 MVP)")
    st.write("This display shows classified product reviews.")
    output_file = os.path.join("output", "classified_reviews.json")
    
    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as f:
            reviews = json.load(f)
        
        for review in reviews:
            st.markdown(f"**Product ID:** {review.get('product_id')}")
            st.markdown(f"**Review:** {review.get('text')}")
            st.markdown(f"**Sentiment:** `{review.get('sentiment')}`")
            st.markdown(f"- Created at: `{review.get('created_at', 'unknown')}`")
            st.markdown(f"- Classified at: `{review.get('classified_at', 'unknown')}`")
            st.markdown("---")
    else:
        st.warning("No classified reviews found. Run the classification script first.")

with tab2:
    st.header("Sentiment Escalation Engine – Day 2: Escalation Triggering")
    st.write("Below are the escalated products based on review clustering.")
    escalation_file = os.path.join("output", "escalations.json")

    if os.path.exists(escalation_file):
        with open(escalation_file, "r", encoding="utf-8") as f:
            escalations = json.load(f)

        for esc in escalations:
            st.markdown(f"### ⚠️ Product: `{esc['product_id']}`")
            st.error(f"Escalation: {esc['reason']}")
            st.markdown(f"- Escalated at: `{esc.get('escalated_at', 'unknown')}`")
            for review in esc["reviews"]:
                st.markdown(f"* **Review:** {review.get('text')}")
                st.markdown(f"  - Sentiment: `{review.get('sentiment')}`")
                st.markdown(f"  - Created at: `{review.get('created_at', 'unknown')}`")
            st.markdown("----")
    else:
        st.info("No escalations yet. Run the escalation grouping script after classification.")

with tab3:
    st.header("Sentiment Escalation Engine – Day 3: Novelty Override Detection")
    st.write("These escalations were triggered despite cooldown due to novel issue detection.")

    escalation_file = os.path.join("output", "escalations.json")

    if os.path.exists(escalation_file):
        with open(escalation_file, "r", encoding="utf-8") as f:
            escalations = json.load(f)

        novelty_escalations = [e for e in escalations if "novel" in e.get("reason", "").lower()]

        if novelty_escalations:
            for esc in novelty_escalations:
                st.markdown(f"### 🧠 Novel Escalation: `{esc['product_id']}`")
                st.warning(f"Reason: {esc['reason']}")
                st.markdown(f"- Escalated at: `{esc.get('escalated_at', 'unknown')}`")
                for review in esc["reviews"]:
                    st.markdown(f"* **Review:** {review.get('text')}")
                    st.markdown(f"  - Sentiment: `{review.get('sentiment')}`")
                    st.markdown(f"  - Created at: `{review.get('created_at', 'unknown')}`")
                st.markdown("----")
        else:
            st.success("No novelty-triggered escalations detected yet.")
    else:
        st.info("Escalation file not found. Run the escalation script first.")

with tab4:
    st.header("Escalation Decision Log")
    st.write("This log records every evaluation, whether escalated or skipped.")

    log_path = os.path.join("output", "escalation_decision_log.jsonl")

    # Clear button
    if os.path.exists(log_path):
        if st.button("🧹 Clear Decision Log"):
            with open(log_path, "w", encoding="utf-8") as f:
                f.write("")  # Overwrite with nothing
            st.success("Decision log cleared.")

    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if not lines:
            st.info("No decision entries yet.")
        else:
            for line in reversed(lines[-50:]):  # Show latest 50
                try:
                    entry = json.loads(line)
                    status = "✅ Escalated" if entry["escalated"] else "🛑 Skipped"
                    st.markdown(f"### {status} — `{entry['product_id']}`")
                    st.markdown(f"- Reason: `{entry['reason']}`")
                    st.markdown(f"- Evaluated at: `{entry['evaluated_at']}`")
                    st.markdown("---")
                except json.JSONDecodeError:
                    st.warning("Corrupted log line skipped.")
    else:
        st.info("Log file not found yet. Run the escalation script to generate it.")
