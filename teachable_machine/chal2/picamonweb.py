from tflite_runtime.interpreter import Interpreter 
import numpy as np
from picamera2 import Picamera2
import cv2
import time
from flask import Flask, Response

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

data_folder = "/home/pi/Desktop/teachable_machine/chal2/"

model_path = data_folder + "model.tflite"
label_path = data_folder + "labels.txt"

interpreter = Interpreter(model_path)

interpreter.allocate_tensors()
_, height, width, _ = interpreter.get_input_details()[0]['shape']

picam2 = Picamera2()
config = picam2.create_preview_configuration({"format":'XRGB8888',"size":(224,224)})
picam2.configure(config)
picam2.start(show_preview=True)

app = Flask(__name__)

@app.route('/')
def index():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def generate_frames():
    while True:
        image = picam2.capture_array("main")[:,:,:3]
        image = cv2.flip(image, 1)
        _, jpeg = cv2.imencode('.jpg', image)
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
    

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)

    while True:
    if ser.readline.decode('utf-8').strip() == "gonow":

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
            print("nothing")
            with open("output2.txt", "a") as output_file:
                    try:
                        output_file.write("Nothing Detected" + "\n")
                    except UnicodeDecodeError as e:
                        print(f"Error decoding line: {e}")
                    time.sleep(1)
        elif label_id==1:
            print("Human")
            with open("output2.txt", "a") as output_file:
                    try:
                        output_file.write("Human detected" + "\n")
                    except UnicodeDecodeError as e:
                        print(f"Error decoding line: {e}")
                    time.sleep(1)
        else:
            print("dino")
            with open("output2.txt", "a") as output_file:
                    try:
                        output_file.write("Dinosaur Detected" + "\n")
                    except UnicodeDecodeError as e:
                        print(f"Error decoding line: {e}")
                    time.sleep(1)

    else:
        with open("output2.txt", "a") as output_file:
            try:
                output_file.write("Moving" + "\n")
            except UnicodeDecodeError as e:
                print(f"Error decoding line: {e}")
