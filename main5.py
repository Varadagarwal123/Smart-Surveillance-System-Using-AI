import streamlit as st
import yt_dlp 
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities.hasher import Hasher
from auth_utils import get_users_from_db, format_credentials, register_user
from violence_detection_utils import process_video, process_live_camera_feed,get_youtube_video_url
from pytube import YouTube

# ========== Streamlit UI ==========

st.set_page_config(page_title="Violence Detection in Videos", layout="wide")
# st.title("🔐 Login Required to Access the Violence Detection System")

users = get_users_from_db()
credentials = format_credentials(users)
authenticator = stauth.Authenticate(credentials, "auth_cookie", "auth_key", cookie_expiry_days=1)

# Login


if st.session_state.get("authentication_status") is None or st.session_state.get("authentication_status") is False:
    st.title("🔐 Login Required to Access the Violence Detection System")

    auth_mode = st.sidebar.radio("Choose Action", ["Login", "Sign Up"])
    if auth_mode == "Login":
        authenticator.login()
    if auth_mode == "Sign Up":
        st.subheader("Create an Account")
        name = st.text_input("Full Name")
        new_username = st.text_input("Username")
        new_password = st.text_input("Password", type="password")
        if st.button("Sign Up"):
            if register_user(name, new_username, new_password):
                st.success("Registration successful! Please log in.")
            else:
                st.error("Username may already exist or something went wrong.")
    elif st.session_state["authentication_status"] is False:
        st.error("Invalid credentials")
    elif st.session_state["authentication_status"] is None:
        st.warning("Please enter your credentials")

elif st.session_state["authentication_status"]:  # If logged in
    # Place Logout button in Sidebar
        with st.sidebar:
            st.success(f"Welcome 👋 {st.session_state['name']}")
            authenticator.logout("Logout", "sidebar")

        # ================= Main App Interface =================
        st.title("🎥 Violence Detection in Videos")
        st.sidebar.title("Settings")
        threshold = st.sidebar.slider("Violence Detection Threshold (%)", 10, 50, 20, step=5) / 100
        consecutive_violent_frames = st.sidebar.slider("Consecutive Violent Frames to Trigger Alert (Live Feed Only)", 3, 10, 5)

        input_type = st.sidebar.selectbox("Select Input Source", ["Upload Video", "YouTube URL", "Live Camera Feed"])

        if input_type == "Upload Video":
            uploaded_file = st.file_uploader("Choose a video...", type=["mp4", "avi"])

            if uploaded_file is not None:
                st.video(uploaded_file)
                st.info("Processing your video. This may take a while depending on the video length...")

                if 'processed_video_path' not in st.session_state:
                    processed_video_path, result_message, result_type = process_video(uploaded_file, threshold)
                    st.session_state.processed_video_path = processed_video_path
                    st.session_state.result_message = result_message
                    st.session_state.result_type = result_type

                # Display detection message for local video
                if st.session_state.result_type == 'success':
                    st.success(st.session_state.result_message)
                else:
                    st.warning(st.session_state.result_message)

        elif input_type == "YouTube URL":
            st.subheader("📺 Analyze a YouTube Video")
            video_url = st.text_input("Enter the YouTube video URL")

            if video_url:
                try:
                    # Show YouTube video info using yt-dlp (not pytube)
                    with yt_dlp.YoutubeDL() as ydl:
                        info_dict = ydl.extract_info(video_url, download=False)
                        thumbnail_url = info_dict.get('thumbnail', None)

                    if thumbnail_url:
                        st.image(thumbnail_url, caption="YouTube Video Preview", use_container_width=True)

                    if st.button("🚀 Start Processing Video"):
                        with st.spinner("Processing YouTube video. This may take a while..."):
                            # ✅ DOWNLOAD the video first using yt-dlp
                            downloaded_video_path = get_youtube_video_url(video_url)
                            print("hi",downloaded_video_path)
                            # ✅ Now process the downloaded file
                            processed_video_path, result_message, result_type = process_video(downloaded_video_path, threshold)

                            # ✅ Show result message
                            st.success(result_message) if result_type == 'success' else st.warning(result_message)
                            st.video(processed_video_path)

                except Exception as e:
                    st.error(f"❌ Failed to process YouTube video: {e}")



        else:
            process_live_camera_feed(consecutive_violent_frames=consecutive_violent_frames)