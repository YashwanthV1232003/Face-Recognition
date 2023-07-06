import os
import numpy as np
import cv2
import pickle
import cvzone
import face_recognition
import numpy as np
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {

    'databaseURL':"https://face-attendance-realtime-fec73-default-rtdb.firebaseio.com/",
    'storageBucket': "face-attendance-realtime-fec73.appspot.com"
})
bucket = storage.bucket()

# updating data base real time


cap = cv2.VideoCapture(0)
cap.set(3,640)
cap.set(4,480)

imgBackground = cv2.imread('Resources/background.png')

#Importing mode images into a list

folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath,path)))

#print(len(imgModeList))

#import/load the encoding file
print("loading encode file . . .")
file = open('EncodeFile.p','rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeListKnownWithIds
#print(studentIds)
print("encode file loaded")

modeType = 0
# once face is detected we only need to download info in first frame as downloading again and again is inefficient
counter = 0
id = -1
imgStudent = []


while True:
    success, img = cap.read()

    imgS = cv2.resize(img ,(0,0),None,0.25,0.25)   #giving scale values not pixels
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    #finding encodings of the new imags
    encodeCurFrame = face_recognition.face_encodings(imgS,faceCurFrame)




    imgBackground[162:162+480,55:55+640] = img
    # starting n ending of height - 162:162+480
    # starting n ending of height - 55:55+640
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType] #changed from 0 to modetype
    # imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[1]
    # imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[2]
    # imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[3]

    #comparing generated encoding with actual with loop
    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurFrame,faceCurFrame): #we cant unzip using for loop or else we hve to have 2 diff loops
            matches = face_recognition.compare_faces(encodeListKnown,encodeFace)
            faceDis =  face_recognition.face_distance(encodeListKnown,encodeFace) #smaller distances = better the match
            # print("matches", matches)
            # print("faceDis", faceDis)


            #getting index of least value distance

            matchIndex = np.argmin(faceDis)
            #print("match index",matchIndex)

            if matches[matchIndex]:
                # print("known face detected")
                # print(studentIds[matchIndex])
                #getting bounding box ie bbox values
                y1,x2,y2,x1 = faceLoc
                #multiply by 4 as we reduced it
                y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
                # x y and width and height
                bbox = 55+x1,162+y1, x2-x1, y2-y1
                imgBackground = cvzone.cornerRect(imgBackground,bbox,rt=0)
                id = studentIds[matchIndex]

                # once we dtect after the ounter

                if counter == 0:
                    cvzone.putTextRect(imgBackground,"Loading",(275, 400)) # 275 400 is position
                    #update the img
                    cv2.imshow("Face Attendance",imgBackground)
                    cv2.waitKey(1)
                    counter =1
                    modeType = 1

        if counter != 0:

            if counter ==1:
                # getting the data
                studentInfo = db.reference(f'Students/{id}').get() # to download
                print(studentInfo)
                # get the Image from storage
                blob = bucket.get_blob(f'Images/{id}.png')
                array = np.frombuffer(blob.download_as_string(),np.uint8)
                imgStudent = cv2.imdecode(array,cv2.COLOR_BGRA2BGR)
                #update attendance
                #if the image is greater 30 secs then tke attendance


                datetimeObject = datetime.strptime(studentInfo['last_attendance_time'],"%Y-%m-%d %H:%M:%S")

                secondsElapsed = (datetime.now()-datetimeObject).total_seconds()
                print(secondsElapsed)

                if secondsElapsed > 30:


                    ref = db.reference(f'Students/{id}')
                    studentInfo['total_attendance'] +=1
                    #updating in db
                    ref.child('total_attendance').set(studentInfo['total_attendance'])
                    ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

                else:
                    modeType = 3
                    counter = 0
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

            if modeType != 3:

                if 10<counter<20:
                    modeType = 2

                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

                if counter <= 10:


                    cv2.putText(imgBackground,str(studentInfo['total_attendance']),(861,125), #size for that particular text
                                cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),1) # 1 is size here before color
                    cv2.putText(imgBackground, str(studentInfo['major']), (1006, 550),  # size for that particular text
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)  # 0.5 is size here before color
                    cv2.putText(imgBackground, str(id), (1006, 493),  # size for that particular text
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)  # 0.5 is size here before color
                    cv2.putText(imgBackground, str(studentInfo['standing']), (910, 625),  # size for that particular text
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)  # 0.6 is size here before color
                    cv2.putText(imgBackground, str(studentInfo['year']), (1025, 625),  # size for that particular text
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)  # 0.6 is size here before color
                    cv2.putText(imgBackground, str(studentInfo['starting_year']), (1125, 625),  # size for that particular text
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)  # 0.6 is size here before color

                    (w, h), _ = cv2.getTextSize(studentInfo['name'],cv2.FONT_HERSHEY_COMPLEX,1,1) #1 is scale and thickness
                    # (w, h), _ :this gives width and height and other value we dont need
                    # if width of text is 50px  so take total width minus 50 px and divide by 2 and start from there so it centers
                    offset = (414-w)//2 #this 414 is width of the image


                    cv2.putText(imgBackground, str(studentInfo['name']), (808+offset, 445),  # size for that particular text
                                cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)  # 1 is size here before color


                    imgBackground[175:175+216,909:909+216] = imgStudent #216 is size of img and 909 is off set of img

                counter+=1

                if counter>=20:
                    counter = 0
                    modeType= 0
                    studentInfo=[]
                    imgStudent=[]
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    else:
        modeType = 0
        counter = 0

    #cv2.imshow("Webcam",img)
    cv2.imshow("Face Attendance",imgBackground)
    cv2.waitKey(1)