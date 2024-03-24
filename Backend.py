from flask import Flask, request, jsonify, render_template, redirect, session
from firebase_admin import credentials, initialize_app, db , auth
import pyrebase
from auth import create_user


app = Flask(__name__)

firebaseConfig = {

  };
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

app.secret_key  = 'secret'


# Initialize Firebase app with database URL and authentication
cred = credentials.Certificate("serviceAccountKey.json")
firebase_app = initialize_app(cred, {
    'databaseURL': 'https://database-83124-default-rtdb.firebaseio.com/'
})
firebase_db = db.reference()

# Define routes
@app.route('/', methods=['GET'])
def home():
        return render_template('home.html')

@app.route('/Teacherlogin', methods=['POST','GET'])
def login():
    if('user' in session):
        return render_template('dashboard.html',user_name=session['user'])
    
    if request.method =='POST':
    # Get teacher credentials from request
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            user = auth.sign_in_with_email_and_password(email, password)
            session['user'] =  email
            return redirect('/dashboard')

        except:
            return render_template('error.html')
    else:
        return render_template('login.html')

@app.route('/dashboard', methods=['GET'])
def dashboard():
    # Check if user is logged in
    if 'user_email' not in session:
        return redirect('/login')

    # Get logged-in user's email from session
    user_email = session['user_email']

    # Retrieve student data for the logged-in teacher
    teacher_email = user_email.replace('.', '_')
    teacher_email = teacher_email.replace('@', '_')
    teacher_ref = firebase_db.child('Teachers').child(teacher_email)
    students = teacher_ref.child('Students').get()

    # Convert Firebase data to a Python dictionary
    students_data = {}
    if students:
        students_data = {student.key(): student.val() for student in students}

    # Print the list of students in the terminal
    print("List of students:")
    for student_id, student_data in students_data.items():
        print(f"ID: {student_id}, Name: {student_data.get('name')}")

    # Render dashboard template with student data
    return render_template('dashboard.html', user_email=user_email, students=students_data)

@app.route('/add_student', methods=['POST','GET'])
def add_student():
    if request.method == 'POST':
        teacher_email = request.form.get('teacher_email')
        student_name = request.form.get('student_name')
        student_id = request.form.get('student_id')

        try:
            teacher_ref = firebase_db.child('Teachers').child(teacher_email.replace('.','_'))
            teacher_ref.child('Students').child(student_id).set({
                'name': student_name,
                'id': student_id
            })
            return 'Student added successfully'
        except Exception as e:
            return f'Failed to add student: {str(e)}'
    
    return render_template('add_student.html')


        # # Authenticate user with Firebase
        # user = auth.get_user_by_email(email)            
        #     if user:
        #         return jsonify({'error': 'User already exists'}), 400
        #     else:
        #         new_user = auth.create_user_with_email_and_password(email, password)
        #         return jsonify({'message': 'User created successfully'}), 200
        # except Exception as e:
        #     return jsonify({'error': str(e)}), 400
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user')
    return redirect('/')           

@app.route('/add_teacher', methods=['POST','GET'])
def add_user():
    if request.method =='POST':
        # Get user credentials from request
        name = request.form.get('name')    
        email = request.form.get('email')
        password = request.form.get('password')

        # Create user with Firebase Authentication
        user_id = create_user(
            name=name,
            email=email,
            password=password
        )
        email_user = email.replace('.', '_')
        print("the user id is: ",user_id)
        if user_id:
            # Create a new database for the teacher
            teacher_ref = firebase_db.child('Teachers').child(email_user)
            teacher_ref.set({
                'email': email,
                'name': name
            })
            # Redirect to home page after successful creation
            return redirect('/')
        else:
            # Handle user creation failure
            return "Failed to register user", 500
    else:
        # Render the registration form
        return render_template('register.html')



################################################################################
# @app.route('/add_teacher', methods=['POST','GET'])
# def add_user():

#     if request.method =='POST':
#     # Get user credentials from request
#         name = request.form.get('name')    
#         email = request.form.get('email')
#         password = request.form.get('password')

#         # Create user with Firebase Authentication
#         user = create_user(
#                 name = name,
#                 email=email,
#                 password=password
#             )
        
#         # Create a new database for the teacher
#         teacher_ref = firebase_db.child('Teachers').child(email)
#         teacher_ref.set({
#             'email': email,
#             'name': name
#         })
#     redirect('/')
#     return render_template('register.html')
#   #  return jsonify({'message': 'Teacher registered successfully'}), 200

#     try:
#         # Extract user details from request
#         email = request.json.get('email')
#         password = request.json.get('password')
#         is_admin = request.json.get('is_admin', False)

        

#         # Add user details to Firebase Realtime Database
#         user_ref = firebase_db.child('users').child(user.uid)
#         user_ref.set({
#             'email': email,
#             'is_admin': is_admin
#         })

#         return jsonify({'message': 'User added successfully'}), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 400
    

# @app.route('/modify_user/<user_id>', methods=['PUT'])
# def modify_user(user_id):
#     try:
#         # Check if the user making the request is an admin
#         # You need to implement your own logic for admin verification
#         # This could involve checking the user's Firebase UID against a list of admin UIDs
#         is_admin = True  # Placeholder for admin check logic

#         if not is_admin:
#             return jsonify({'error': 'Unauthorized access'}), 401

#         # Extract updated user details from request
#         email = request.json.get('email')
#         is_admin = request.json.get('is_admin', False)

#         # Update user details in Firebase Authentication
#         auth.update_user(
#             user_id,
#             email=email,
#             custom_claims={'admin': is_admin}
#         )

#         # Update user details in Firebase Realtime Database
#         user_ref = firebase_db.child('users').child(user_id)
#         user_ref.update({
#             'email': email,
#             'is_admin': is_admin
#         })

#         return jsonify({'message': 'User modified successfully'}), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 400



@app.route('/modify_database/<user_id>', methods=['PUT'])
def modify_database(user_id):
    # Logic for modifying user's database (admin privilege required)
    pass

@app.route('/update_attendance/<user_id>', methods=['PUT'])
def update_attendance(user_id):

    try:
        # Extract attendance data from request JSON
        attendance_data = request.json.get('attendance')

        # Get user's database from Firebase Realtime Database
        user_database_ref = firebase_db.child('users').child(user_id).child('database')
        user_database = user_database_ref.get()

        if user_database is None:
            return jsonify({'error': 'User database not found'}), 404

        # Update attendance for each student in the user's database
        for student_id, student_info in user_database.items():
            if 'attendance' not in student_info:
                student_info['attendance'] = {}

            # Update attendance time and count for the student
            student_info['attendance']['time'] = attendance_data.get('time')
            student_info['attendance']['count'] = attendance_data.get('count')

            # Save updated student info back to the database
            user_database_ref.child(student_id).update(student_info)

        return jsonify({'message': 'Attendance updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    

    
if __name__ == '__main__':
    app.run(debug=True)
