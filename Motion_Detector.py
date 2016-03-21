"""

        Author: Rowland DePree                                      Motion_Detector.py

        This is a program designed to alert a user to movements in the camera.  It will make a beep sound and send a text
        message off to the user if motion is detected.

"""

import argparse
import datetime
import smtplib
import time
import winsound

import cv2
import imutils


def send_message():
    """
    This ia method design to send a text message to the owner of the camera
    :return:
    """
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login('motion.sensor.from.laptop@gmail.com', 'testing@123')

    server.sendmail('Laptop', '7173501175@txt.att.net',
                    "Your camera has detected motion.\nDisregard this if it was you who entered.\nOtherwise, please return to the location of the camera immediately.")


def main():
    """
    This is the main program.  It is what detects the motion on the camera and alarms if motion is detected.  The original form of this was
    obtain from: http://www.pyimagesearch.com/2015/05/25/basic-motion-detection-and-tracking-with-python-and-opencv/
    :return:
    """
    alarm = False
    ap = argparse.ArgumentParser()
    ap.add_argument("--v", "--video", help="path to the video file")
    ap.add_argument("-a", "--min-area", type=int, default=250, help="minimum area size")
    args = vars(ap.parse_args())

    if args.get("video", None) is None:
        camera = cv2.VideoCapture(0)
        time.sleep(0.25)
    else:
        camera = cv2.VideoCapture(args["video"])

    firstFrame = None
    while True:
        (grabbed, frame) = camera.read()
        text = "NO MOTION DETECTED"

        if not grabbed:
            break

        frame = imutils.resize(frame, width=500)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if firstFrame is None:
            firstFrame = gray
            continue
        frameDelta = cv2.absdiff(firstFrame, gray)
        thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]

        thresh = cv2.dilate(thresh, None, iterations=2)
        (cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for c in cnts:
            if cv2.contourArea(c) < args["min_area"]:
                continue
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            text = "MOTION DETECTED"
            cv2.putText(frame, "Room Status: {}".format(text), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

        cv2.imshow("Security Feed", frame)
        if text == "MOTION DETECTED" and not alarm:
            send_message()
            winsound.Beep(2500, 1000)
            alarm = True
        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

    camera.release()
    cv2.destoryAllWindows()


"""
    Starts the main program
"""
if __name__ == '__main__':
    main()
