from tflite_runtime.interpreter import Interpreter 
import numpy as np
from picamera2 import Picamera2
import cv2
import serial
import time

from PIL import Image, ImageDraw, ImageFont

def load_labels(path): # Read the labels from the text file as a Python list.
    with open(path, 'r') as f:
        return [line.strip() for i, line in enumerate(f.readlines())]

def set_input_tensor(interpreter, image):
    tensor_index = interpreter.get_input_details()[0]['index']
    input_tensor = interpreter.tensor(tensor_index)()[0]
    input_tensor[:, :] = image

def classify_image(interpreter, image, top_k=1):
    set_input_tensor(interpreter, image)

    interpreter.invoke()
    output_details = interpreter.get_output_details()[0]
    output = np.squeeze(interpreter.get_tensor(output_details['index']))

    scale, zero_point = output_details['quantization']
    output = scale * (output - zero_point)

    ordered = np.argpartition(-output, 1)
    return [(i, output[i]) for i in ordered[:top_k]][0]

data_folder = "/home/pi/Desktop/teachable_machine/chal3/"

model_path = data_folder + "model.tflite"
label_path = data_folder + "labels.txt"

interpreter = Interpreter(model_path)

interpreter.allocate_tensors()
_, height, width, _ = interpreter.get_input_details()[0]['shape']

picam2 = Picamera2()
config = picam2.create_preview_configuration({"format":'XRGB8888',"size":(224,224)})
picam2.configure(config)
picam2.start(show_preview=True)
# Initialize Serial
ser = serial.Serial('/dev/ttyUSB1', 9600, timeout=1)
ser.reset_input_buffer()
while True:
    image = picam2.capture_array("main")[:,:,:3]
    image = cv2.flip(image, 1)
  
    label_id, prob = classify_image(interpreter, image)
    labels = load_labels(label_path)
    classification_label = labels[label_id]
    
    result_text = "{} ({})".format(classification_label, np.round(prob*100, 2))
    overlay = np.zeros((500,500,4),dtype=np.uint8)
    overlay[:80,:250] = (0,0,255,54) #blue background
    text_color = (255, 0, 0, 255) #red text
    cv2.putText(overlay, result_text, (0,50), cv2.FONT_HERSHEY_SIMPLEX,
                  1, text_color, 3)
    
    picam2.set_overlay(overlay)
    
    print("Result: ", label_id, ", Accuracy: ", np.round(prob*100, 2))
    if label_id==0:
        print("thermomnetre")
        with open("output3.txt", "a") as output_file:
                ser.write(b"Take Temperature\n")
                try:
                    line = ser.readline().decode('utf-8').rstrip()
                    print(line)
                    output_file.write(line + "\n")
                except UnicodeDecodeError as e:
                    print(f"Error decoding line: {e}")
                time.sleep(1)
        
    elif label_id==1:
        print("fire")
        with open("output3.txt", "a") as output_file:
                ser.write(b"Fan to start running\n")
                try:
                    line = ser.readline().decode('utf-8').rstrip()
                    print(line)
                    output_file.write(line + "\n")
                except UnicodeDecodeError as e:
                    print(f"Error decoding line: {e}")
                time.sleep(1)
    else:
        print("nothing")
        with open("output3.txt", "a") as output_file:
                ser.write(b"Nothing\n")
                try:
                    line = ser.readline().decode('utf-8').rstrip()
                    print(line)
                except UnicodeDecodeError as e:
                    print(f"Error decoding line: {e}")
                time.sleep(1)

