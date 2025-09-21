import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="AI Object Detection App", layout="wide")
st.title("AI Object Detection (YOLOv11)")

# Signup Section

with st.expander("Create New Account"):
    fullname = st.text_input("Full Name", key="su_fullname")
    new_user = st.text_input("Username", key="su_username")
    new_pass = st.text_input("Password", type="password", key="su_pass")
    confirm_pass = st.text_input("Confirm Password", type="password", key="su_confirm")

    if st.button("Signup"):
        if not fullname or not new_user or not new_pass:
            st.error("All fields required")
        elif new_pass != confirm_pass:
            st.error("Passwords do not match")
        else:
            try:
                r = requests.post(f"{API_URL}/signup", params={
                    "fullname": fullname,
                    "username": new_user,
                    "password": new_pass,
                    "confirm_password": confirm_pass
                })
                if r.status_code == 200:
                    st.success("Signup successful. Please login below.")
                else:
                    st.error(r.json().get("detail", "Signup failed"))
            except Exception as e:
                st.error(f"Error connecting to server: {e}")

# Login Section

if "token" not in st.session_state:
    with st.form("login_form"):
        username = st.text_input("Username", key="li_user")
        password = st.text_input("Password", type="password", key="li_pass")

        if st.form_submit_button("Login"):
            try:
                resp = requests.post(f"{API_URL}/login", params={
                    "username": username,
                    "password": password
                })
                if resp.status_code == 200:
                    data = resp.json()
                    st.session_state.token = data["access_token"]
                    st.session_state.fullname = data["fullname"]
                    st.success(f"Welcome {st.session_state.fullname}!")
                else:
                    st.error("Invalid credentials")
            except Exception as e:
                st.error(f"Error connecting to server: {e}")

# Main App Section

if "token" in st.session_state:
    st.markdown(f"**Logged in as:** {st.session_state.fullname}")

    # Logout button
    if st.button("🔒 Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("You have been logged out.")
        st.rerun()

    st.sidebar.header("Detection Settings")
    conf = st.sidebar.slider("Confidence threshold", min_value=0.1, max_value=0.9, value=0.5, step=0.05)
    st.sidebar.caption("Higher = stricter, fewer false positives")

    uploaded_file = st.file_uploader("Upload an image", type=["jpg","jpeg","png"])

    if uploaded_file and st.button("Detect Objects"):
        files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
        params = {"token": st.session_state.token, "conf": conf}

        try:
            resp = requests.post(f"{API_URL}/uploadimage", files=files, params=params)

            if resp.status_code == 200:
                try:
                    data = resp.json()
                    st.json(data["detections"])
                    st.image(f"{API_URL}/outputimage", caption="Detected Objects", width="stretch")
                except Exception as e:
                    st.error(f"Failed to parse response: {e}")
            else:
                try:
                    st.error(resp.json().get("detail", "Detection failed"))
                except:
                    st.error(f"Detection failed. Status code: {resp.status_code}")
        except Exception as e:
            st.error(f"Error connecting to server: {e}")

    # Upload History
    
    if st.button("Show My Upload History"):
        try:
            r = requests.get(f"{API_URL}/history", params={"token": st.session_state.token})
            if r.status_code == 200:
                history = r.json()
                if not history:
                    st.info("No uploads yet")
                else:
                    for rec in history:
                        st.write(f"**{rec['filename']}** — uploaded at {rec['uploaded_at']} — avg_confidence: {rec['avg_confidence']:.3f}")
                        st.json(rec["detections"])
                        try:
                            img = requests.get(f"{API_URL}/output/{rec['id']}")
                            if img.status_code == 200:
                                st.image(img.content, width=300)
                        except Exception:
                            pass
            else:
                st.error("Could not fetch history. Try login again.")
        except Exception as e:
            st.error(f"Error fetching history: {e}")