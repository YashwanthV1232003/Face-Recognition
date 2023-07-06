import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://face-attendance-realtime-fec73-default-rtdb.firebaseio.com/"
})

#creating refrence

ref = db.reference('Students')

data = {
    #value within value
    "321654":
        {
            "name": "Yashwanth V",
            "major": "CS&SE",
            "starting_year": 2020,
            "total_attendance":6,
            "standing":"G",
            "year":4,
            "last_attendance_time":"2023-02-11 00:54:34"

        },
    "852741":
        {
            "name": "Emily Blunt",
            "major": "Economics",
            "starting_year": 2022,
            "total_attendance": 12,
            "standing": "B",
            "year": 1,
            "last_attendance_time": "2023-02-11 00:54:34"

        },
    "963852":
        {
            "name": "Elon Musk",
            "major": "Physics",
            "starting_year": 2021,
            "total_attendance": 7,
            "standing": "G",
            "year": 2,
            "last_attendance_time": "2023-02-11 00:54:34"

        }
}

#sending data

for key,value in data.items():
    # if sending the data to specific directory we use child
    ref.child(key).set(value)