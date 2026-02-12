import cv2
import numpy as np
import msvcrt
import threading
from colorama import init, Fore
from colorama.ansi import clear_screen, Cursor
import sys
import socket
import time
import pyttsx3

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   #sets up connection to "server"
client.connect(("localhost", 9999))

#this only works in windows because terminals are hard
#also i haven't yet bothered to add an escape condition, just close your terminal window to finish

#Source:https://github.com/ejfox/ascii_webcam/blob/main/ascii_webcam.py
def webcam_to_ascii(frame, cols=120, rows=40):
    # Convert frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Resize the frame
    cell_width = frame.shape[1] // cols
    cell_height = frame.shape[0] // rows
    resized = cv2.resize(gray, (cols, rows))
    
    # Define ASCII characters
    ascii_chars = ' .:;><~+-?][}{|\/XYUJCLQ0Z*#MW&8%B@$'
    
    # Convert to ASCII
    ascii_frame = ''
    for row in resized:
        for pixel in row:
            # Ensure the index is within the range of ascii_chars
            index = min(int(pixel / 7), len(ascii_chars) - 1)
            ascii_frame += ascii_chars[index]
        ascii_frame += '\n'
    
    return ascii_frame

def eavesdropper():             #reads terminal input character by character
    while True:
        char = msvcrt.getch()
        if char == b'\x08':         #backspace for the unintiated (me)
            if str_stack:
                str_stack.pop()
        elif char == b'\r':        
            #when user hits enter, switch to broadcast mode
            #doing this here has the handy side effect of not displaying inputted characters till the server message has been read
            broadcast()
        else:
            try:
                decoded = char.decode('utf-8')       #utf-8 so no foreigners allowed sorry 
                str_stack.append(decoded)
            except UnicodeDecodeError:          
                pass


def broadcast():
    txt_input=""

    for char in str_stack:              #converts from stack to string
            txt_input += char

    for char in txt_input:              #text dissapearing anim
        time.sleep(1/len(txt_input))
        str_stack.pop(0)

    client.send(txt_input.encode('utf-8')) 
    reciever()


def reciever():
    msg = client.recv(2048).decode('utf-8')

    #starts a new thread so text printing doesnt hang waiting for voice over
    voice_thread = threading.Thread(target=voice, args=(msg,), daemon=True)  
    voice_thread.start()

    #prints message with an attempt to match speaking cadence
    for char in msg:
        str_stack.append(char)
        if char != " " and char != ".":
            time.sleep(0.08)
        elif char != ".":
            time.sleep(0.15)
        else:
            time.sleep(1.5)
        
    #text dissapearing anim
    time.sleep(1)
    for char in msg:
        time.sleep(1/len(msg))
        str_stack.pop(0)


def voice(msg):
    #tts reads message, if you mess with rate, remember to adjust reciever print speeds accordingly
    engine = pyttsx3.init()
    engine.setProperty('rate', 100)
    engine.say(msg)
    engine.runAndWait()


def main():
    init()
    print("\033[?25l", end="")  #hides cursor

    global str_stack #stores text to be animated, character by character
    str_stack = []

    #dynamic cam assignment check
    camindex = 0
    while True:
        cap = cv2.VideoCapture(camindex)
        if cap.isOpened() and cap.getBackendName()=="DSHOW":
            break
        else:
            camindex += 1
        if camindex == 9:
            print("Failed to find cam, exiting....")
            sys.exit()
    
    text_thread = threading.Thread(target=eavesdropper, daemon=True)   #on seperate thread so frames dont hang waiting on user input
    text_thread.start()

    while True:
        txt_input = ""

        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        ascii_frame = webcam_to_ascii(frame)
        # print("\033[H\033[J", end="")  # Clear console          #old drawing method kept incase something breaks
        # print(Fore.GREEN + ascii_frame)


        for char in str_stack:
            txt_input += char


        sys.stdout.write(Cursor.POS(2, 3))                  #smoother drawing, no stinky cursor
        sys.stdout.write(Fore.GREEN + ascii_frame)
        sys.stdout.write("\n")
        sys.stdout.write(Fore.GREEN + txt_input + "\033[K")
        sys.stdout.flush()

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()