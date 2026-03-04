from __future__ import annotations

import requests
import streamlit as st

BACKEND_URL = "http://127.0.0.1:8000/analyze-claim/"

st.set_page_config(page_title="ClaimSense AI", layout="centered")
st.title("ClaimSense AI")

uploaded_file = st.file_uploader("Upload claim document", type=None)

if uploaded_file is not None:
    with st.spinner("Analyzing claim..."):
        try:
            files = {
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    uploaded_file.type or "application/octet-stream",
                )
            }
            response = requests.post(BACKEND_URL, files=files, timeout=60)
            response.raise_for_status()
            payload = response.json()

            analysis = payload.get("analysis", {})

            st.subheader("Parsed Claim Data")
            st.json(analysis.get("parsed_data", {}))

            st.subheader("Denial Explanation")
            st.write(analysis.get("explanation", "No explanation returned."))

            st.subheader("Generated Appeal Letter")
            st.write(analysis.get("appeal_letter", "No appeal letter returned."))
        except requests.exceptions.RequestException as exc:
            st.error(f"Failed to reach backend: {exc}")
        except ValueError:
            st.error("Backend returned invalid JSON.")
        except Exception as exc:
            st.error(f"Unexpected error: {exc}")
