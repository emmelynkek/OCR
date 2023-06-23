from picamera import PiCamera
import cv2
import pytesseract
import numpy as np
from pytesseract import Output
# from pybraille import convertText
import re
# from gtts import gTTS
import os
import requests

BACKUP = True

# TODO: uncomment this later
# from modules.motor import *
from modules.motor_backup import *

import RPi.GPIO as GPIO

GPIO.setwarnings(False)
# GPIO.setmode(GPIO.BOARD)

# Peripherals
PICTURE_PIN = 17
GPIO.setup(PICTURE_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

NEXT_PIN = 27
GPIO.setup(NEXT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

PREV_PIN = 22
GPIO.setup(PREV_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

camera = PiCamera()

code_table = {
    'a': '100000',
    'b': '110000',
    'c': '100100',
    'd': '100110',
    'e': '100010',
    'f': '110100',
    'g': '110110',
    'h': '110010',
    'i': '010100',
    'j': '010110',
    'k': '101000',
    'l': '111000',
    'm': '101100',
    'n': '101110',
    'o': '101010',
    'p': '111100',
    'q': '111110',
    'r': '111010',
    's': '011100',
    't': '011110',
    'u': '101001',
    'v': '111001',
    'w': '010111',
    'x': '101101',
    'y': '101111',
    'z': '101011',
    '1': '100000',
    '2': '110000',
    '3': '100100',
    '4': '100110',
    '5': '100010',
    '6': '110100',
    '7': '110110',
    '8': '110010',
    '9': '010100',
    '0': '010110',
    ',': '010000',
    ';': '011000',
    ':': '010010',
    '.': '010011',
    '!': '011010',
    '(': '011011',
    ')': '011011',
    '?': '011001',
    '"': '011001',
    '*': '001010',
    '#': '001111',
    'Capital': '000001',
    'Letter': '000011',
    ' ': '000000'
}

CONFIG_MAP = {
  '00': 0,
  '01': 1,
  '11': 2,
  '10': 3
}

output_braille = []
string_store = ""
prev_state = ['000000', '000000', '000000']
pointer = 3

# Audio
def audio(char):
    print(char)
    try:
        if char == "f":
            r = requests.get(url=f'http://172.20.10.2/ff')
        else:
            r = requests.get(url=f'http://172.20.10.2/{char}')
    except:
        pass

# removes all special characters and double spacing
def string_processing(string_input):
    pattern = r'[^A-Za-z0-9\\.\\*,;:!()"?\s]'
    string_input = re.sub(pattern, '', string_input)
    string_input = re.sub(" +", " ", string_input)
    return string_input

# converts string to a list of braille
def string_to_braille(string_input):
    letter_indicator = True
    braille_output = []
    string_store = ""
    for char in string_input:
        if (letter_indicator==True and char.isnumeric()):
            braille_output.append(code_table["Letter"])
            char += "^"
            letter_indicator = False
        elif (letter_indicator==False and char.isalpha()):
            braille_output.append(code_table["#"])
            letter_indicator = True
            char += "#"
        if (char.isupper()):
            braille_output.append(code_table['Capital'])
            string_store += "%"
            char = char.lower()
        braille_output.append(code_table[char])
        string_store += char
    return braille_output, string_store

def braille_to_motor(braille_input):
    motor_output = []
    for char in braille_input:
        if len(motor_output) == 0 or len(motor_output[-1]) == 6:
            motor_output.extend(["","",""])
        motor_output[-3] += char[:2]
        motor_output[-2] += char[2:4]
        motor_output[-1] += char[4:6]
    return motor_output

def capture_image_backup():
    global pointer, prev_state, output_braille, string_store
    print("Capturing Image...")

    camera.start_preview()
    camera.rotation = 180 # Depends how we eventually orientate the camera
    camera.capture("images/image.jpg")
    camera.stop_preview()

    # Read from camera
    img = cv2.imread("images/image.jpg")

    # Read from file
    # img = cv2.imread("images/1.jpg")

    d = pytesseract.image_to_data(img, output_type=Output.DICT)
    n_boxes = len(d['text'])

    output_string = ""
    for i in range(n_boxes):
        if int(d['conf'][i]) > 60:
            (text, x, y, w, h) = (d['text'][i], d['left'][i], d['top'][i], d['width'][i], d['height'][i])
            # don't show empty text

            if text and text.strip() != "":
                output_string += text + " "
                img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                img = cv2.putText(img, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
    print(f"String Output Bef: {output_string}")

    # String processing
    output_string = string_processing(output_string)
    print(f"String Output Aft: {output_string}")
    print(f"String Output: {output_string}")

    # Conversion to list of braille
    output_braille, string_store = string_to_braille(output_string)
    print(f"Braille Output: {output_braille}")

    # Conversion to braille image
    # print(convertText(output_string))

    # Conversion to motor instructions
    pointer = 1
    prev_state = [0, 0, 0]

    # while pointer <= len(output_braille):
    curr_state = braille_to_motor(output_braille[pointer-1:pointer])

    motor_steps = []
    differential_steps = []
    for i, instruction in enumerate(curr_state):
        motor_steps.append(CONFIG_MAP[instruction])
        differential_step = CONFIG_MAP[instruction] - prev_state[i]
        differential_step %= 4
        differential_steps.append(differential_step)
    prev_state = motor_steps

    print(f"Motor Output: {differential_steps} | Batch: {pointer}")
    # Save image
    # cv2.imwrite('images/image_ocr.jpg', img)

    turn_elevator_motor(direction=stepper.BACKWARD)
    turn_motors(differential_steps)
    turn_elevator_motor()
    audio(string_store[pointer-1])

def capture_image():
    global output_braille, pointer, prev_state, string_store

    print("Capturing Image...")

    camera.start_preview()
    camera.rotation = 180 # Depends how we eventually orientate the camera
    camera.capture("images/image.jpg")
    camera.stop_preview()

    # Read from camera
    img = cv2.imread("images/image.jpg")

    # Read from file
    # img = cv2.imread("images/1.jpg")

    d = pytesseract.image_to_data(img, output_type=Output.DICT)
    n_boxes = len(d['text'])

    output_string = ""
    for i in range(n_boxes):
        if int(d['conf'][i]) > 60:
            (text, x, y, w, h) = (d['text'][i], d['left'][i], d['top'][i], d['width'][i], d['height'][i])
            # don't show empty text

            if text and text.strip() != "":
                output_string += text + " "
                img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                img = cv2.putText(img, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
    print(f"String Output Bef: {output_string}")

    # String processing
    output_string = string_processing(output_string)
    print(f"String Output Aft: {output_string}")
    # print(f"String Output: {output_string}")

    # Conversion to list of braille
    output_braille = string_to_braille(output_string)
    print(f"Braille Output: {output_braille}")

    # Conversion to braille image
    # print(convertText(output_string))

    # Conversion to motor instructions
    pointer = 3
    prev_state = ['000000', '000000', '000000']
    # while pointer <= len(output_braille):
    curr_state = braille_to_motor(output_braille[pointer-3:pointer])

    output_motor = ["".join([str(int(a) ^ int(b)) for a, b in zip(x, y)]) for x, y in zip(curr_state, prev_state)]
    print(f"Motor Output: {output_motor} | Batch: {pointer // 3}")

    # send_motor_instructions(output_motor)
    prev_state = curr_state

    # Conversion to audio
    # language = 'en'
    # myobj = gTTS(text=output_string, lang=language, slow=False)
    # myobj.save("welcome.mp3")
    # os.system("mpg321 welcome.mp3")

    # Save image
    cv2.imwrite('images/image_ocr.jpg', img)

def next_chars():
    global pointer, output_braille, prev_state, string_store
    if pointer > len(output_braille):
        return
    elif pointer > len(output_braille) - 3:
        print("End of Output")
    pointer += 3
    curr_state = braille_to_motor(output_braille[pointer-3:pointer])
    output_motor = ["".join([str(int(a) ^ int(b)) for a, b in zip(x, y)]) for x, y in zip(curr_state, prev_state)]
    print(f"Motor Output: {output_motor} | Batch: {pointer // 3}")

    # send_motor_instructions(output_motor)
    prev_state = curr_state

def next_chars_backup():
    global output_braille, pointer, prev_state, string_store
    if pointer > len(output_braille):
        return
    elif pointer > len(output_braille) - 1:
        print("End of Output")
    pointer += 1
    curr_state = braille_to_motor(output_braille[pointer-1:pointer])

    motor_steps = []
    differential_steps = []
    for i, instruction in enumerate(curr_state):
        motor_steps.append(CONFIG_MAP[instruction])
        differential_step = CONFIG_MAP[instruction] - prev_state[i]
        differential_step %= 4
        differential_steps.append(differential_step)
    
    prev_state = motor_steps

    print(f"Motor Output: {differential_steps} | Batch: {pointer}")

    turn_elevator_motor(direction=stepper.BACKWARD)
    turn_motors(differential_steps)
    turn_elevator_motor()
    audio(string_store[pointer-1])

def prev_chars():
    global pointer, output_braille, prev_state, output_string
    if pointer <= 3:
        return

    pointer -= 3
    curr_state = braille_to_motor(output_braille[pointer-3:pointer])
    output_motor = ["".join([str(int(a) ^ int(b)) for a, b in zip(x, y)]) for x, y in zip(curr_state, prev_state)]
    print(f"Motor Output: {output_motor} | Batch: {pointer // 3}")

    prev_state = curr_state

def prev_chars_backup():
    global pointer, output_braille, prev_state, string_store
    if pointer <= 0:
        return

    pointer -= 1
    if pointer == 0:
        curr_state = ['00','00','00']
    else:
        curr_state = braille_to_motor(output_braille[pointer-1:pointer])

    motor_steps = []
    differential_steps = []
    for i, instruction in enumerate(curr_state):
        motor_steps.append(CONFIG_MAP[instruction])
        differential_step = CONFIG_MAP[instruction] - prev_state[i]
        differential_step %= 4
        differential_steps.append(differential_step)
    
    prev_state = motor_steps
    print(f"Motor Output: {differential_steps} | Batch: {pointer}")

    turn_elevator_motor(direction=stepper.BACKWARD)
    turn_motors(differential_steps)
    turn_elevator_motor()
    audio(string_store[pointer-1])

if __name__ == "__main__":
    print("Running program")
    
    # picture_button.when_pressed = capture_image_backup if BACKUP else capture_image
    # next_button.when_pressed = next_chars_backup if BACKUP else next_chars
    # prev_button.when_pressed = prev_chars_backup if BACKUP else prev_chars

    while True:
        if GPIO.input(PICTURE_PIN) == GPIO.LOW:
            capture_image_backup()
        if GPIO.input(NEXT_PIN) == GPIO.LOW:
            next_chars_backup()
        if GPIO.input(PREV_PIN) == GPIO.LOW:
            prev_chars_backup()
