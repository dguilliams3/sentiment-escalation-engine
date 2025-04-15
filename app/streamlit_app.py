import streamlit as st
import json
import os

# Create two tabs: one for Day 1 and one for Day 2
tab1, tab2 = st.tabs(["Feature 1: Classified Reviews", "Feature 2: Escalation Triggering"])

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
                st.markdown("---")
            st.markdown("----")
    else:
        st.info("No escalations yet. Run the escalation grouping script after classification.")
