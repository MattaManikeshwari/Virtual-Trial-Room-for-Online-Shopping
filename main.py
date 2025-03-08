import os
import cv2
import cvzone
from flask import Flask, Response, render_template, send_from_directory, jsonify, request
from cvzone.PoseModule import PoseDetector
import threading

app = Flask(__name__)

# Global variables
cap = cv2.VideoCapture(0)
detector = PoseDetector()

# Constants
SHIRT_WIDTH_REFERENCE = 262
SHOULDER_WIDTH_REFERENCE = 190
PANT_WIDTH_REFERENCE=135
HIP_WIDTH_REFERENCE=72
SHIRT_HEIGHT = 581
SHIRT_WIDTH = 440
SCALE_X = 44
SCALE_Y = 48
PANT_HEIGHT=375
PANT_WIDTH=150
DRESS_WIDTH_REFERENCE=262
DRESS_HEIGHT=370
DRESS_WIDTH=200
WIDTH_OFFSET=0
HEIGHT_OFFSET=0
# Configurable parameters
config = {
    'width_offset': WIDTH_OFFSET,
    'height_offset': HEIGHT_OFFSET,
    'shirts_path': "",
    'pants_path': "",
    'dress_path': ""
}

feed_active = True
feed_lock = threading.Lock()

def reset_feed_state():
    global feed_active, cap
    with feed_lock:
        feed_active = True
        if cap is None or not cap.isOpened():
            cap = cv2.VideoCapture(0)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            print("Camera reset and feed state set to active.")
        else:
            print("Camera is already active and feed state is active.")
        print("Feed state reset")

def stop_camera():
    global feed_active, cap
    with feed_lock:
        feed_active = False
        if cap is not None and cap.isOpened():
            cap.release()
            print("Camera stopped and feed state set to inactive.")
        else:
            print("Camera is already stopped and feed state is inactive.")
        print("Camera stopped")

def overlay_clothing(lmList, img, clothing_path, points):
    global SHIRT_HEIGHT,SHIRT_WIDTH,SHIRT_WIDTH_REFERENCE,SHOULDER_WIDTH_REFERENCE,SCALE_X,SCALE_Y,config
    lm1, lm2 = lmList[points[0]][0:2], lmList[points[1]][0:2]
    if not clothing_path:
        print("No clothing path provided.")
        return img
    if clothing_path==config['shirts_path']:
        fixed_ratio = SHIRT_WIDTH_REFERENCE / SHOULDER_WIDTH_REFERENCE
        clothing_img = cv2.imread(clothing_path, cv2.IMREAD_UNCHANGED)
        SHIRT_HEIGHT=clothing_img.shape[0]
        SHIRT_WIDTH=clothing_img.shape[1]
        if SHIRT_HEIGHT==SHIRT_WIDTH:
            SHIRT_HEIGHT=SHIRT_HEIGHT*1.5
        ratio_height_width = SHIRT_HEIGHT / SHIRT_WIDTH 
        current_scale = (lm1[0] - lm2[0]) / SHOULDER_WIDTH_REFERENCE
        
    elif clothing_path==config['pants_path']:
         fixed_ratio=PANT_WIDTH_REFERENCE/HIP_WIDTH_REFERENCE
         clothing_img = cv2.imread(clothing_path, cv2.IMREAD_UNCHANGED)
         PANT_HEIGHT=clothing_img.shape[0]
         PANT_WIDTH=clothing_img.shape[1]
         if PANT_HEIGHT==PANT_WIDTH:
             PANT_HEIGHT=PANT_HEIGHT*2
         ratio_height_width=PANT_HEIGHT/PANT_WIDTH
         current_scale = (lm1[0] - lm2[0]) / HIP_WIDTH_REFERENCE
         SCALE_X=35
         SCALE_Y=18  
    elif clothing_path==config['dress_path']:
         fixed_ratio=DRESS_WIDTH_REFERENCE/SHOULDER_WIDTH_REFERENCE
         clothing_img = cv2.imread(clothing_path, cv2.IMREAD_UNCHANGED)
         DRESS_HEIGHT=clothing_img.shape[0]
         DRESS_WIDTH=clothing_img.shape[1]
         if (2 * DRESS_WIDTH * (1 - 50)) <= DRESS_HEIGHT <= (2 * DRESS_WIDTH * (1 + 50)):
             DRESS_HEIGHT=DRESS_HEIGHT*2
         ratio_height_width=DRESS_HEIGHT/DRESS_WIDTH
         current_scale = (lm1[0] - lm2[0]) / SHOULDER_WIDTH_REFERENCE
         SCALE_X=44
         SCALE_Y=48
    if clothing_img is None:
        print(f"Clothing image at {clothing_path} failed to load.")
        return img
        
    
    
    
    width = max(2, abs(int((lm1[0] - lm2[0]) * fixed_ratio)))+config["width_offset"]
    height = int(width * ratio_height_width)+config['height_offset']
    clothing_img = cv2.resize(clothing_img, 
                            (width, 
                             height))
    if WIDTH_OFFSET==config['width_offset']:
       offset = int(SCALE_X * current_scale), int(SCALE_Y * current_scale)
    else:
        offset=int((SCALE_X*current_scale)-config['width_offset']),int((SCALE_Y*current_scale)-config['height_offset'])
    try:
        img = cvzone.overlayPNG(img, clothing_img, 
                               (lm2[0] - offset[0], lm2[1] - offset[1]))
    except Exception as e:
        print(f"Error overlaying clothing: {e}")
        pass
        
    return img

def generate_frames():
    global config
    while True:
        with feed_lock:
            if not feed_active or not cap.isOpened():
                print("Feed is not active or camera is not opened.")
                break
                
            success, img = cap.read()
            if not success:
                print("Failed to read frame from camera.")
                break
                
            img = detector.findPose(img)
            lmList, _ = detector.findPosition(img, bboxWithHands=False, draw=False)
            
            if lmList:
                if config['shirts_path']:
                    img = overlay_clothing(lmList, img, config['shirts_path'], [11, 12])
                elif config['pants_path']:
                    img = overlay_clothing(lmList, img, config['pants_path'], [23, 24])
                elif config['dress_path']:
                    img = overlay_clothing(lmList, img, config['dress_path'], [11, 12])
                    
            _, buffer = cv2.imencode('.jpg', img)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                  b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    print("Index route accessed")
    return render_template('index.html')

@app.route('/tryon', methods=["POST"])
def tryon():
    print("Tryon route accessed")
    reset_feed_state()
    data=request.form  # Parse JSON into a dictionary

    # Default reset
    config['dress_path'] = ""
    config['pants_path'] = ""
    config['shirts_path'] = ""
    print("data:",data)
    if data:
        clothing_type = data.get('cloth_type')
        item_id = data.get('cloth_id')
        if clothing_type and item_id:
            if clothing_type == "shirts":
                config['shirts_path'] = f"static/{clothing_type}/{item_id}.png"
            elif clothing_type == "pants":
                config['pants_path'] = f"static/{clothing_type}/{item_id}.png"
            elif clothing_type == "dresses":
                config['dress_path'] = f"static/{clothing_type}/{item_id}.png"
    return render_template('tryon.html')


@app.route('/static/shirts/<path:filename>')
def serve_shirt(filename):
    return send_from_directory('static/shirts', filename)
@app.route('/static/pantss/<path:filename>')
def serve_pant(filename):
    return send_from_directory('static/pantss', filename)
@app.route('/static/dresses/<path:filename>')
def serve_dress(filename):
    
    return send_from_directory('static/dresses', filename)

@app.route("/update_fit", methods=["POST"])
def update_fit():
    global SCALE_X,SCALE_Y,config
    print("Update fit route accessed")
    data = request.json
    config['width_offset'] = int(data.get("width", config['width_offset']))
    config['height_offset'] = int(data.get("height", config['height_offset']))
    
    print(f"Updated width offset to {config['width_offset']}, height offset to {config['height_offset']}")
    return jsonify({
        "shirtwidth": config['width_offset'],
        "shirtheight": config['height_offset'],
        "scalex": SCALE_X,
        "scaley": SCALE_Y,
    })

@app.route('/stop_feed', methods=['POST'])
def stop_feed():
    stop_camera()
    print("Stop feed route accessed")
    

    print("Feed stopped and shirt path reset.")
    return jsonify({"status": "success"})


@app.route('/video_feed')
def video_feed():
    print("Video feed route accessed")
    return Response(generate_frames(), 
                   mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    print("App running")
    app.run(debug=True)