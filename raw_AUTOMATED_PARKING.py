import cv2
import easyocr
import matplotlib.pyplot as plt
import datetime
import time
import mysql.connector as my
import pyttsx3
engine = pyttsx3.init()
engine.setProperty('volume', 1) 
engine.setProperty('rate', 150) 
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[2].id) 
unique_id=1
image_not_detect=0
text_not_detect_while_scan=0

def payment(details):
    print(details)
    time.sleep(7)
    capture_vehicle()

    

def databaseuser(gadi_number):
    mycon=my.connect(host="localhost",user="root",passwd="21696579",database="parkingsystem")   #connector
    if mycon.is_connected():
        cursor=mycon.cursor()                                                                      #cursor
        cursor2=mycon.cursor()
        cursor.execute(f"select * from userdata")                                                  #query
        data=cursor.fetchall()  
        for i in data:
            if i[1]==gadi_number:
                currtime=time.strftime("%y-%m-%d %H:%M:%S")
                cursor2.execute(f"update userdata set exittime='{currtime}' where number_plate='{gadi_number}'")
                mycon.commit()                                                                    #current time updated to SQL

                cursor.execute("select * from userdata")
                for i in data:
                    if i[1]==gadi_number:
                        mycon.close()
                        engine.say("YOUR ENTRIES ARE VALID PROCEED FOR PAYMENT !")
                        engine.runAndWait()
                        payment(i)

        else:
            currtime=time.strftime("%y-%m-%d %H:%M:%S")
            unique_id=len((data))
            query=f"insert into userdata values('{unique_id}','{gadi_number}','{currtime}',NULL)"
            cursor.execute(query)
            mycon.commit()
            mycon.close()
            engine.say("YOUR ENTRIES ARE REGISTERED !")
            engine.runAndWait()
            capture_vehicle()

                    
def information(gadi_number):
    global image_not_detect
    count_space=gadi_number.count(" ")
    listt=list(gadi_number)
    for i in range (count_space):
        listt.remove(" ")
    gadi_number=''.join(listt)                                       #if there is any space space will be removed
    if image_not_detect<5:
        if gadi_number.isalnum()==True and len(gadi_number)==10:    # if number plate have any other symbol or length is more than 5 it will rescan the image 20 times      
            image_not_detect=0
            print("NUMBER PLATE SCANNED")
            engine.say(" VEHICLE CONFIRMED ! NUMBER PLATE SCANNED")
            engine.runAndWait()
            databaseuser(gadi_number)
        else:
            image_not_detect+=1
            engine.say("PLACE YOUR VEHICLE AT PROPER POSITION !")
            engine.runAndWait()
            #print(image_not_detect)
            capture_numberplate()

    else:
        engine.say("NUMBER PLATE IS NOT VALID ")
        engine.runAndWait()
        print("NUMBER PLATE IS NOT VALID ")                         # After 7 times if number plate does not contain proper charaters it will declare that number plate is invalid
        image_not_detect=0

#def rescan_numberplate():



def identify_GADInumber():
    global text_not_detect_while_scan
    image_path = r"D:\OneDrive\Desktop\GC\C PROJECT\New folder\PYTHON PROJECT\numberplate_frame_gray.png"
    img = cv2.imread(image_path)

    reader = easyocr.Reader(['en'])

    text_ = reader.readtext(img)
    if text_==[]:
        if text_not_detect_while_scan<5:
        #time.sleep(4)    #it will read 5 times if motion is detected but if no text is extracted then it will back go to motion vehicle_detector function
            text_not_detect_while_scan+=1
            engine.say("PLACE YOUR VEHICLE AT PROPER POSITION !")
            engine.runAndWait()
            capture_numberplate()
        else :
            text_not_detect_while_scan=0
            capture_vehicle()        
    else:
        if type(text_[0][1])==str:
            image_not_detect=0
            print(text_[0][1])
            gadi_number=text_[0][1]               # this is the NUMBERPLATE text in string format
            text_not_detect_while_scan=0
            information(gadi_number)
        


def capture_numberplate():
    time.sleep(3)
    cap=cv2.VideoCapture(0) ;
    #print(cap.isOpened())
    fourcc=cv2.VideoWriter_fourcc(*"XVID")
    outt=cv2.VideoWriter("output.avi",fourcc,60,(1920,1080))  
    ret,numberplate_frame=cap.read()
    numberplate_frame_gray=cv2.cvtColor(numberplate_frame,cv2.COLOR_BGR2GRAY)                   
    cv2.imwrite("numberplate_frame_gray.png",numberplate_frame_gray)
    img=cv2.imread(r"D:\OneDrive\Desktop\GC\C PROJECT\New folder\PYTHON PROJECT\numberplate_frame_gray.png",1)
    cv2.imshow("image",img)
    cv2.waitKey(4000)
    cap.release()
    cv2.destroyAllWindows()
    identify_GADInumber()
    


def capture_vehicle():
    global image_not_detect
      
    cap=cv2.VideoCapture(0) ;
    print(cap.isOpened())
    fourcc=cv2.VideoWriter_fourcc(*"XVID")
    outt=cv2.VideoWriter("output.avi",fourcc,60,(1920,1080))  

    if image_not_detect ==0:             
        ret,initial_frame=cap.read()
        initial_gray=cv2.cvtColor(initial_frame,cv2.COLOR_BGR2GRAY)                     #this is the initial frame 
        cv2.imwrite("initial_image.png",initial_gray)
    else:
        initial_gray=cv2.imread(r"D:\OneDrive\Desktop\GC\C PROJECT\New folder\PYTHON PROJECT\initial_image.png",0)
         
    while cap.isOpened():
        ret, frame=cap.read()
        if ret==True:
                gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)                 #current frame in B/W
                cv2.imshow("framee",gray)
                outt.write(gray)

                diff = cv2.absdiff(initial_gray, gray)                              #diff = cv2.absdiff(prev_frame_gray, curr_frame_gray)   diff-->nested array
                #threshold - a binary image which give black and wite intensity
                _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)

                # Display the difference
                #cv2.imshow("Frame Difference", thresh)

                #print(diff)
                hist1 = cv2.calcHist([initial_gray], [0], None, [256], [0, 256])
                hist2 = cv2.calcHist([gray], [0], None, [256], [0, 256])
                similarity = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
                if similarity < .2:                                             # Adjust threshold as needed
                        print("MOTION DETECTED !")
                        engine.say("MOTION DETECTED !")
                        engine.runAndWait()
                        #cv2.imwrite("vehicle_image.png",gray)
                        #identify_GADInumber()
                        cap.release()
                        cv2.destroyAllWindows()
                        capture_numberplate()
                                                            
                if cv2.waitKey(1) & 0xFF ==ord("q"):
                    break
        else:
            break
    cap.release()
    cv2.destroyAllWindows()


capture_vehicle()

            
