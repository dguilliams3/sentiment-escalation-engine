import streamlit as st
import json
import os

# Create two tabs: one for Day 1 and one for Day 2
tab1, tab2 = st.tabs(["Day 1: Classified Reviews", "Day 2: Escalation Triggering"])

with tab1:
    st.header("Sentiment Escalation Engine (Day 1 MVP)")
    st.write("This display shows classified product reviews.")
    output_file = os.path.join("output", "classified_reviews.json")
    if os.path.exists(output_file):
        with open(output_file, "r") as f:
            reviews = json.load(f)
        for review in reviews:
            st.markdown(f"**Product ID:** {review.get('product_id')}")
            st.markdown(f"**Review:** {review.get('text')}")
            st.markdown(f"**Sentiment:** `{review.get('sentiment')}`")
            st.markdown("---")
    else:
        st.write("No classified reviews found. Run the classification script first.")

with tab2:
    st.header("Sentiment Escalation Engine – Day 2: Escalation Triggering")
    st.write("Below are the escalated products based on review clustering.")
    escalation_file = os.path.join("output", "escalations.json")
    if os.path.exists(escalation_file):
        with open(escalation_file, "r") as f:
            escalations = json.load(f)
        for esc in escalations:
            st.markdown(f"### Product: {esc['product_id']}")
            st.error(f"Escalation: {esc['reason']}")
            for review in esc["reviews"]:
                st.markdown(f"* **Review:** {review['text']}")
                st.markdown(f"  - **Sentiment:** `{review['sentiment']}`")
            st.markdown("---")
    else:
        st.write("No escalations yet. Check back later after processing reviews.")
