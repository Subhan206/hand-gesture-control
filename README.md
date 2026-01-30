# Multimodal Hand Gesture Control ✋🖱️

![Status](https://img.shields.io/badge/Status-Active-success)
![CV](https://img.shields.io/badge/Computer_Vision-MediaPipe-orange)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)

> **A contactless Human-Computer Interaction (HCI) interface that controls the mouse, scroll, and system volume using real-time hand landmark detection.**

![Demo](https://via.placeholder.com/800x400.png?text=Insert+Demo+GIF+Here)

## 📝 Overview
This project implements a **State-Machine based Controller** using a standard RGB webcam. It leverages **Google's MediaPipe** for hand tracking and maps 3D landmarks to 2D system controls. It features "Zero-Latency" optimization for real-time performance.

## ✨ Key Features

### 🎮 **Multimodal Interaction (State Machine)**
The system switches modes dynamically based on hand configuration:
- **Cursor Mode (Index Up):** Precision mouse tracking with coordinate interpolation.
- **Scroll Mode (Index + Middle Up):** Vertical scrolling based on hand height (Top=Up, Bottom=Down).
- **Volume Mode (Pinky Up):** Linear interpolation of thumb-index distance to control system audio.

### 🖱️ **Advanced Gestures**
- **Left Click:** Pinch Index + Thumb.
- **Right Click:** Pinch Middle + Thumb.
- **Turbo Mode:** Optimized with `pyautogui.PAUSE = 0` for real-time responsiveness.

## 🛠️ Tech Stack
- **Vision:** `MediaPipe Hands`, `OpenCV`
- **Control:** `PyAutoGUI` (Mouse/Scroll), `Pycaw` (Windows Audio API)
- **Math:** `NumPy` for vector mapping and smoothing.

## 🚀 Usage
1. Install dependencies: `pip install -r requirements.txt`
2. Run the controller: `python hand_track.py`
3. Raise your **Index Finger** to move the mouse, or **Pinky** to change volume!
