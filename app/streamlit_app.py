import streamlit as st
import json
import os

st.title("Sentiment Escalation Engine (Day 1 MVP)")
st.write("This display shows classified product reviews.")

# Load classified reviews from the output file
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
