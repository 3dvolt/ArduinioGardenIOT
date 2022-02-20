import numpy as np
import cv2
import threading
import requests

#funzione per l'invio dal bot della persona rilevata dalla CV
def send_image(botToken, imageFile, chat_id):
    url = "https://api.telegram.org/bot"+botToken+"/sendPhoto"
    payload = {'chat_id': str(chat_id)}
    files = [
        ('photo', ('output.jpg',imageFile, 'image/jpg'))
    ]
    headers = {}
    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    print(response)
    return

def startVideo(input,irrigationTime,br,config):
    hog = cv2.HOGDescriptor()
    hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

    cv2.startWindowThread()

    # secondi di irrigazione corrente
    timeDuration = 0

    #status corrente irrigazione
    status = "OFF"
    # open webcam video stream
    cap = cv2.VideoCapture(input)
    # the output will be written to output.avi

    findSomeone = 0

    #in sec
    findSomeoneDelay = 10

    nextsec=0

    # verifica se non è presente nessuno
    while (True):
        # Capture frame-by-frame
        ret, frame = cap.read()

        # resizing for faster detection
        frame = cv2.resize(frame, (640, 480))
        # using a greyscale picture, also for faster detection
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

        second = (cap.get(cv2.CAP_PROP_POS_MSEC)/1000)%60

        if(findSomeone == 1):
            print("find someone")
            print("delays", nextsec)
            if nextsec <= second:
                findSomeone=0
                nextsec=0
            if nextsec == 0:
                nextsec = second
                nextsec = nextsec+findSomeoneDelay


        # se non c'è nessuno e timeDuration non oltre il tempo di irrigazione
        if(timeDuration >= irrigationTime and findSomeone == 0):
            if status != "ON":
                # start water
                br.sender(b's')
                #timeDuration = second
                status = "ON"

        #primi 15 secondi per stabilizzare lo stream, se non trova nessuno
        if(second >= 15 and findSomeone == 0 and status != "ON"):
            print("15 sec analize stop")
            # start water
            br.sender(b's')
            status = "ON"

        #se il tempo di irrigazione è corrispondente alla durata effettiva spegni
        if(irrigationTime <= timeDuration):
            br.sender(b'e')
            break

        # if detect people in the image
        # returns the bounding boxes for the detected objects
        boxes, weights = hog.detectMultiScale(frame, winStride=(8, 8))

        boxes = np.array([[x, y, x + w, y + h] for (x, y, w, h) in boxes])

        for (xA, yA, xB, yB) in boxes:
            # display the detected boxes in the colour picture
            cv2.rectangle(frame, (xA, yA), (xB, yB),(0, 255, 0), 2)
            # altrimenti stoppa irrigazione
            findSomeone = 1
            # stop water
            if status == "ON":
                br.sender(b'e')
                cv2.imwrite('output.jpg', frame)
                send_image(config['bot'], open('output.jpg', 'rb'), config['uesr_code'])
                status = "OFF"

        # Display the resulting frame
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    cap.release()
    # finally, close the window
    cv2.destroyAllWindows()
    cv2.waitKey(1)