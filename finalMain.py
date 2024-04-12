from flask import Flask, render_template, Response
import cv2
import numpy as np
import face_recognition
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import numpy as np
from datetime import datetime
from pymongo import MongoClient
import pickle

app = Flask(__name__)

# MongoDB Configuration
client = MongoClient('mongodb://username:password@localhost:27017/')
db = client['attendance_system']
collection = db['attendance']

class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.video.set(3, 640)
        self.video.set(4, 480)
        self.encodeListKnown = []  
        self.studentIds = []      
        # Load the encoding file
        print("Loading Encode File ...")
        file = open('EncodeFile.p', 'rb')
        encodeListKnownWithIds = pickle.load(file)
        file.close()
        self.encodeListKnown, self.studentIds = encodeListKnownWithIds
        # print(studentIds)
        print("Encode File Loaded")


    def __del__(self):
        self.video.release()

    def get_frame(self):
        while True:
            success, img = self.video.read()
            if not success:
                return None

            imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

            faceCurFrame = face_recognition.face_locations(imgS)
            encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

            for faceLoc in faceCurFrame:
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

            if faceCurFrame:
                for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
                    matches = face_recognition.compare_faces(self.encodeListKnown, encodeFace)
                    faceDis = face_recognition.face_distance(self.encodeListKnown, encodeFace)
                    matchIndex = np.argmin(faceDis)
                    if matches[matchIndex]:
                        # Get the student ID
                        id = self.studentIds[matchIndex]
                        print("THE STUDENT WITH THE ID :" + id + " IS DETECTED")
                        # Update attendance in MongoDB
                        update_attendance(id)

            _, jpeg = cv2.imencode('.jpg', img)
            return jpeg.tobytes()


def update_attendance(student_id):
    # Get current date
    today = datetime.now().strftime("%Y-%m-%d")

    # Check if the student has already marked attendance for today
    existing_record = collection.find_one({"student_id": student_id, "date": today})

    if existing_record:
        print("Attendance already marked for today.")
    else:
        # Insert new attendance record
        record = {
            "student_id": student_id,
            "date": today
        }
        collection.insert_one(record)
        print("Attendance marked successfully.")

@app.route('/')
def index():
    return render_template('index.html')

def gen(camera):
    while True:
        frame = camera.get_frame()
        if frame is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)
