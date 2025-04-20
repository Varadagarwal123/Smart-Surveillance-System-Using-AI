import numpy as np
import streamlit as st
import cv2
from keras.models import load_model
from collections import deque
import tempfile
import os
import yt_dlp
from email_notification import send_email_notification
from pytube import YouTube

# ========== Violence Detection Functions ==========

from pytube import YouTube
import tempfile

def get_youtube_video_url(video_url):
    # Download YouTube video using yt-dlp and get the best mp4 stream URL
    try:
        # Using yt-dlp to download the video
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',  # Download best video+audio combination
            'outtmpl': tempfile.mktemp(suffix='.mp4')  # Save it to a temporary file
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            video_path = ydl.prepare_filename(info_dict)  # Get the path of the downloaded video
        return video_path
    except Exception as e:
        raise Exception(f"Error in downloading video: {str(e)}")





def process_video(video_source, threshold=0.2):
    temp_video = tempfile.NamedTemporaryFile(delete=False, suffix='.avi')
    
    if isinstance(video_source, str) and video_source.startswith("http"):
    # If URL passed, download it
        video_path = get_youtube_video_url(video_source)
        cap = cv2.VideoCapture(video_path)
        
    else:
        # Local file
        temp_video.write(video_source.read())
        temp_video.close()
        cap = cv2.VideoCapture(temp_video.name)

    try:
        model = load_model('modelnew.h5')
        Q = deque(maxlen=128)
        writer = None
        (W, H) = (None, None)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
        violent_frames = 0
        frame_counter = 0
        snapshots = []
        max_snapshots = 25

        progress_bar = st.progress(0)
        progress_text = st.empty()
        output_file = tempfile.NamedTemporaryFile(delete=False, suffix='.avi')

        while True:
            (grabbed, frame) = cap.read()
            if not grabbed:
                break
            frame_counter += 1
            if W is None or H is None:
                (H, W) = frame.shape[:2]

            output = frame.copy()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (128, 128)).astype("float32")
            frame = frame.reshape(128, 128, 3) / 255
            preds = model.predict(np.expand_dims(frame, axis=0))[0]
            Q.append(preds)
            results = np.array(Q).mean(axis=0)
            label = (preds > 0.50)[0]

            if label:
                violent_frames += 1
                if len(snapshots) < max_snapshots:
                    snapshot_path = f"violent_frame_{frame_counter}.jpg"
                    cv2.imwrite(snapshot_path, output)
                    snapshots.append(snapshot_path)

            text_color = (0, 255, 0) if not label else (0, 0, 255)
            cv2.putText(output, f"Violence: {label}", (35, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.25, text_color, 3)

            if writer is None:
                fourcc = cv2.VideoWriter_fourcc(*"MJPG")
                writer = cv2.VideoWriter(output_file.name, fourcc, 30, (W, H), True)

            writer.write(output)
            progress = frame_counter / total_frames
            progress_bar.progress(progress)
            progress_text.markdown(f"⏳ Processing... {progress*100:.2f}%")


        writer.release()
        cap.release()
        progress_bar.empty()
        progress_text.empty()

        violent_percentage = violent_frames / total_frames

        if violent_percentage >= threshold:
            result_message = f"This video contains violence. ({violent_percentage:.2%})"
            result_type = 'warning'
            send_email_notification(
                subject="Violence Detected Alert",
                body=f"Violence detected: {violent_percentage:.2%} of frames.",
                attachments=snapshots
            )
        else:
            result_message = f"This video does not contain violence. ({violent_percentage:.2%})"
            result_type = 'success'

    finally:
            if not isinstance(video_source, str):
                os.remove(temp_video.name)
            for snapshot in snapshots:
                os.remove(snapshot)

    return output_file.name, result_message, result_type

def process_live_camera_feed(camera_index=0, consecutive_violent_frames=5):
    model = load_model('modelnew.h5')
    Q = deque(maxlen=128)
    consecutive_violence_count = 0
    alert_sent = False
    cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        st.error("Could not open the camera.")
        return

    st.info("Starting live camera feed...")
    video_container = st.empty()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        output = frame.copy()
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(frame_rgb, (128, 128)).astype("float32") / 255
        preds = model.predict(np.expand_dims(frame_resized, axis=0))[0]
        Q.append(preds)
        label = (preds > 0.50)[0]

        if label:
            consecutive_violence_count += 1
            text = "Violence Detected"
            text_color = (0, 0, 255)
        else:
            consecutive_violence_count = 0
            text = "No Violence"
            text_color = (0, 255, 0)

        if consecutive_violence_count >= consecutive_violent_frames and not alert_sent:
            send_email_notification(
                subject="Violence Detected Alert",
                body="Violent activity detected in live camera feed."
            )
            st.warning("Alert: Violence detected and email sent!")
            alert_sent = True

        cv2.putText(output, text, (35, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.25, text_color, 3)
        video_container.image(output, channels="BGR")

    cap.release()
