# Face Recognition Attendance System

This project implements a Face Recognition Attendance System using OpenCV (Open Source Computer Vision Library) and CNN (Convolutional Neural Network). The system identifies individuals from images or video streams and maintains an attendance record based on their presence.

## Features

- **Face Detection**: Utilizes OpenCV's Haar Cascade Classifier for detecting faces in images or video streams.
- **Face Recognition**: Employs a Convolutional Neural Network (CNN) model for recognizing faces.
- **Attendance Tracking**: Records attendance based on recognized faces and timestamps.
- **User Interface (UI)**: Provides a simple and intuitive interface for users to interact with the system.

![Video Demo](https://github.com/Deepak484sakthi2004/FaceRecognitionAttendanceSystem/raw/main/raw/videos/mini_project.mp4)

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/your_username/face-recognition-attendance.git
    ```

2. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. Train the CNN model after updating the Database to create encodings

    ```bash
    python encodeGenerator.py
    ```

2. Run the Face Recognition Attendance System:

    ```bash
    python Database.py
    python main.py
    ```

3. Follow on-screen instructions to navigate the system and manage attendance.

## Credits

This project was developed by Deepaksakthi V K.

## License

This project is licensed under the MIT License.
