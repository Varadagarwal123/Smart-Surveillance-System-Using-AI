# main.py

import streamlit as st
import numpy as np
import cv2
from keras.models import load_model
from collections import deque
from email_notification import send_email_notification

# Function to process the live camera feed for violence detection
def process_live_camera_feed(camera_index=0, consecutive_violent_frames=5):
    # Load the trained model
    model = load_model('modelnew.h5')
    Q = deque(maxlen=128)

    # Initialize counter for consecutive violent frames
    consecutive_violence_count = 0
    alert_sent = False

    # Capture video from the specified camera
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        st.error("Could not open the camera.")
        return

    st.info("Starting live camera feed...")

    # Set up Streamlit container for the live video feed
    video_container = st.empty()

    # Stream the camera feed in real-time
    while cap.isOpened():
        # Read a frame from the camera
        ret, frame = cap.read()
        if not ret:
            break

        output = frame.copy()

        # Preprocess frame for model input
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(frame_rgb, (128, 128)).astype("float32")
        frame_resized = frame_resized.reshape(128, 128, 3) / 255

        # Predict violence in the frame
        preds = model.predict(np.expand_dims(frame_resized, axis=0))[0]
        Q.append(preds)
        results = np.array(Q).mean(axis=0)
        label = (preds > 0.50)[0]

        # Increment counter if violence is detected, otherwise reset it
        if label:
            consecutive_violence_count += 1
            text = "Violence Detected"
            text_color = (0, 0, 255)  # Red color for alert
        else:
            consecutive_violence_count = 0
            text = "No Violence"
            text_color = (0, 255, 0)  # Green color for normal

        # Trigger an alert if the consecutive count reaches the threshold
        if consecutive_violence_count >= consecutive_violent_frames and not alert_sent:
            send_email_notification(
                subject="Violence Detected Alert",
                body="Warning: Violent activity detected in the live camera feed.",
            )
            st.warning("Alert: Violence detected and email notification sent!")
            alert_sent = True  # Ensure alert is only sent once

        # Overlay text on the frame
        FONT = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(output, text, (35, 50), FONT, 1.25, text_color, 3)

        # Update the Streamlit video container with the current frame
        video_container.image(output, channels="BGR")

    # Release the video capture after loop
    cap.release()

# Streamlit app interface
st.set_page_config(page_title="Live Violence Detection", layout="wide")
st.title("📹 Live Violence Detection with Camera Feed")

# Sidebar for setting consecutive violent frame threshold
st.sidebar.title("Settings")
consecutive_violent_frames = st.sidebar.slider("Consecutive Violent Frames to Trigger Alert", min_value=3, max_value=10, value=5, step=1)

# Camera input section
st.sidebar.title("Input Source")
camera_index = st.sidebar.number_input("Enter Camera Index (0 for default camera)", value=0, step=1)

# Start processing live feed
if st.sidebar.button("Start Camera Feed"):
    process_live_camera_feed(camera_index=camera_index, consecutive_violent_frames=consecutive_violent_frames)
