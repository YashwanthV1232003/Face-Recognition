import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {

    'databaseURL':"https://face-attendance-realtime-fec73-default-rtdb.firebaseio.com/",
    'storageBucket': "face-attendance-realtime-fec73.appspot.com"
})

#Importing student images

folderPath = 'Images'
pathList = os.listdir(folderPath)
print(pathList)
imgList = []
#extracting id
studentIds=[]
for path in pathList:
    imgList.append(cv2.imread(os.path.join(folderPath,path)))
    #removing png , 0 for the first element
    #print(os.path.splitext(path)[0])
    studentIds.append(os.path.splitext(path)[0])
    #sending images

    fileName = f'{folderPath}/{path}'
    # creating bucket
    bucket = storage.bucket()
    #creating a blob to send it
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)

print(studentIds)

def findEncodings(imagesList):
    encodeList = []

    for img in imagesList:
        #open cv uses bgr nd face rec uses rgb
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        # find encoding
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)

    return encodeList
print("Encoding Started")
encodeListKnown = findEncodings(imgList)
#stating which id belongs to which id
encodeListKnownWithIds = [encodeListKnown,studentIds]
#print(encodeListKnown)
print("Encoding Complete")

file = open("EncodeFile.p",'wb')
#dump list in this file
pickle.dump(encodeListKnownWithIds,file)
file.close()
print("File saved")