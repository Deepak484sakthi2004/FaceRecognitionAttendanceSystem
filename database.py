

from firebase_admin import db
import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,
                              {
                                  'databaseURL': ''
                              })

ref = db.reference('Students')

data = {
    "420":
        {
            "name": "Modi",
            "major": "Economics and Political Science",
            "starting_year": 2020,
            "total_attendance": 12,
            "CGPA": "7.5",
            "year": 4,
            "last_attendance_time": "2024-1-11 00:54:34"
        },
    "123":
        {
            "name": "Deepaksakthi",
            "major": "IT",
            "starting_year": 2021,
            "total_attendance": 7,
            "CGPA": "8.2",
            "year": 3,
            "last_attendance_time": "2024-3-22 00:54:34"
        },
    "456":
        {
            "name": "RadhaKrishnan",
            "major": "IT",
            "starting_year": 2021,
            "total_attendance": 10,
            "CGPA": "8.2",
            "year": 3,
            "last_attendance_time": "2024-3-22 00:54:34"
        }
}
 
for key, value in data.items():
    ref.child(key).set(value)
