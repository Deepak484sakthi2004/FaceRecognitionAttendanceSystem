from flask import Flask, jsonify,render_template, request, session,redirect, Response
import requests
import pyrebase
from auth import create_user
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import face_recognition
from datetime import datetime
import cvzone
import cv2
import numpy as np
app = Flask(__name__, template_folder='templates')

# Load environment variables from .env file
load_dotenv()

MONGO_USER = os.getenv('MONGO_USER')
MONGO_PASSWORD = os.getenv('MONGO_PASSWORD')
MONGO_CLUSTER = os.getenv('MONGO_CLUSTER')
MONGO_DATABASE = os.getenv('MONGO_DATABASE')

# MongoDB configuration
mongo_url = f"mongodb+srv://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_CLUSTER}/{MONGO_DATABASE})"
database_name = MONGO_DATABASE
collection_name = os.getenv('MONGO_COLLECTION', 'movies')  # Use 'movies' as default collection name if not provided

client = MongoClient(mongo_url)
db = client[database_name]
collection = db[collection_name]

# 'auth' collection in your MongoDB database
auth_collection = db['auth'] 

app.secret_key = os.getenv('SECRET_KEY')  # Set secret key for session management


# Route to get all documents from MongoDB
@app.route('/api/data', methods=['GET'])
def get_data():
    data = list(collection.find({}, {'_id': 0}))
    return jsonify(data)


@app.route('/Teacherlogin', methods=['POST','GET'])
def login():
    if request.method =='POST':
        # Get teacher credentials from request
        email = request.form.get('email')
        password = request.form.get('password')
        
        try:
            user = auth_collection.find_one({'username': email, 'password': password})
            
            if user:
                print("User logged in:", user)
                session['email'] = email  # Store email in session
                print(session)

                print("Session data after login:", session)  # Debug print
                return redirect('/dashboard')
            else :
                return render_template('error.html')  

        except Exception as e:
            print("Exception:", e)
            return render_template('error.html')
        
    else:
        return render_template('login.html')
    
# @app.route('/dashboard', methods=['GET'])
# def dashboard():
#     print("Welcome to Dashboard")
#     print("Session data in dashboard:", session)  # Debug print
#     if 'email' in session:  # Check if email is stored in session
#         email = session['email']  # Retrieve email from session
#         print("Email retrieved from session:", email)  # Debug print
#         response = requests.get(f'http://localhost:5000/teacher/data?emailId={email}')  # Pass email as query parameter
#         if response.status_code == 200:
#             data = response.json()
#             #return jsonify(data)
#         else:
#             return render_template('error.html', error=response.json()), response.status_code
#     # else:
#     #     return redirect('/Teacherlogin')  # Redirect to login if email is not stored in session
    
#     return render_template('dashboard.html')


@app.route('/dashboard', methods=['GET'])
def dashboard():
    print("Welcome to Dashboard")
    print("Session data in dashboard:", session)  # Debug print
    if 'email' in session:  # Check if email is stored in session
        email = session['email']  # Retrieve email from session
        print("Email retrieved from session:", email)  # Debug print
        response = requests.get(f'http://localhost:5000/teacher/data?emailId={email}')  # Pass email as query parameter
        if response.status_code == 200:
            data = response.json()
            
            return render_template('dashboard.html', studentDetails=data,user_email=email) 
        else:
            return render_template('error.html', error=response.json()), response.status_code
    else:
        return redirect('/Teacherlogin')  # Redirect to login if email is not stored in session
    


# @app.route('/dashboard', methods=['GET'])
# def dashboard():
#     print("Welcome to Dashboard")
#     response = requests.get('http://localhost:5000/teacher/data')
#     if 'email' in session:  # Check if email is stored in session
#         email = session['email']  # Retrieve email from session
#         print("Email retrieved from session:", email)  # Debug print
#         response = requests.get(f'http://localhost:5000/teacher/data?emailId={email}')  # Pass email as query parameter
#         if response.status_code == 200:
#             data = response.json()
#             return jsonify(data)
#         else:
#             return render_template('error.html', error=response.json()), response.status_code
#     else:
#         return redirect('/Teacherlogin')
    


@app.route('/', methods=['GET'])
def home():
        return render_template('home.html')

@app.route('/teacher/data', methods=['GET'])
def get_data_by_teacher():
    email = request.args.get('emailId')
    if not email:
        return jsonify({'error': 'EmailId is required'}), 400
    students_data = list(collection.find({}, {'_id': 0}))
    for teacher in students_data:
        if teacher['emailId'] == email:
            return jsonify(teacher['students'])
    
    return jsonify({'error': 'No students found for the provided emailId'}), 404
def mark_attendance(student_id):
    # Placeholder implementation
    student_info = {
        'id': student_id,
        'name': 'John Doe',
        'total_attendance': 10,
        'major': 'Computer Science',
        'CGPA': 3.8,
        'year': 'Senior',
        'starting_year': 2018,
        'last_attendance_time': '2024-04-06 10:00:00'
    }
    return student_info

def attendance_generator():
    global encodeListKnown, studentIds, imgModeList, imgBackground, cap

    modeType = 0
    counter = 0
    id = -1
    imgStudent = []

    while True:
        success, img = cap.read()

        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        faceCurFrame = face_recognition.face_locations(imgS)
        encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

        imgBackground[162:162 + 480, 55:55 + 640] = img
        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

        if faceCurFrame:
            for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
                matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
                faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
                matchIndex = np.argmin(faceDis)

                if matches[matchIndex]:
                    y1, x2, y2, x1 = faceLoc
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                    imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                    id = studentIds[matchIndex]
                    if counter == 0:
                        cvzone.putTextRect(imgBackground, "Loading", (275, 400))
                        ret, jpeg = cv2.imencode('.jpg', imgBackground)
                        frame = jpeg.tobytes()
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
                        counter = 1
                        modeType = 1

            if counter != 0:
                if counter == 1:
                    studentInfo, imgStudent = mark_attendance(id)

                    datetimeObject = datetime.strptime(studentInfo['last_attendance_time'], "%Y-%m-%d %H:%M:%S")
                    secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
                    if secondsElapsed > 30:
                        modeType = 3
                    else:
                        modeType = 0

                if modeType != 3:
                    if 10 < counter < 20:
                        modeType = 2

                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

                    if counter <= 10:
                        cv2.putText(imgBackground, str(studentInfo['total_attendance']), (861, 125),
                                    cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                        cv2.putText(imgBackground, str(studentInfo['major']), (1006, 550),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                        cv2.putText(imgBackground, str(id), (1006, 493),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                        cv2.putText(imgBackground, str(studentInfo['CGPA']), (910, 625),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                        cv2.putText(imgBackground, str(studentInfo['year']), (1025, 625),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                        cv2.putText(imgBackground, str(studentInfo['starting_year']), (1125, 625),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                        (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                        offset = (414 - w) // 2
                        cv2.putText(imgBackground, str(studentInfo['name']), (808 + offset, 445),
                                    cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

                        resized_imgStudent = cv2.resize(imgStudent, (371, 545))
                        imgBackground[175:175 + resized_imgStudent.shape[0], 909:909 + resized_imgStudent.shape[1]] = resized_imgStudent

                counter += 1

                if counter >= 20:
                    counter = 0
                    modeType = 0
                    studentInfo = []
                    imgStudent = []
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
        else:
            modeType = 0
            counter = 0

        ret, jpeg = cv2.imencode('.jpg', imgBackground)
        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/attendance')
def attendance():
    return Response(attendance_generator(), mimetype='multipart/x-mixed-replace; boundary=frame')



@app.route('/logout')
def logout():
    session.pop('user')
    return redirect('/') 

if __name__ == '__main__':
    app.run(debug=True)

