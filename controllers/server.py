import logging

import settings

from models.tello_drone import TelloDrone

from flask import render_template
from flask import request
from flask import jsonify
from flask import Response

logger = logging.getLogger(__name__)

app = settings.app

def get_tello_drone():
    return TelloDrone()

def video_generator():
    drone = get_tello_drone()
    for jpeg in drone.video_jpeg_generator():
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' +
               jpeg +
               b'\r\n\r\n')


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/tello/video/stremeing')
def streame_video():
    return Response(video_generator(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/tello/command/', methods=['POST'])
def send_command():
    command = request.form.get('command')
    logger.info(f'command : {command} command is called')
    
    drone = get_tello_drone()

    if command =='speed':
        speed = request.form.get('speed')
        if speed:
            drone.set_speed(int(speed))

    if command == 'takeOff':
        drone.takeoff()

    if command == 'land':
        drone.land()
    
    if command == 'forward':
        drone.move_forward()

    if command == 'back':
        drone.move_backward()

    if command == 'up':
        drone.move_up()

    if command == 'down':
        drone.move_down()

    if command == 'right':
        drone.right()

    if command == 'left':
        drone.left()

    if command == 'clockwise':
        drone.rotate_clockwise()

    if command == 'counterClockwise':
        drone.rotate_counter_clockwise()

    if command == 'flipFront':
        drone.flip_forward()

    if command == 'flipBack':
        drone.flip_back()

    if command == 'flipRight':
        drone.flip_right()

    if command == 'flipLeft':
        drone.flip_left()

    if command == 'pose':
        logger.info('pose recognition mode start!!')

    if command == 'faceDetectAndTrack':
        drone.enable_face_detect()
    if command == 'stopFaceDetectAndTrack':
        drone.disable_face_detect()

    return jsonify(status='Success!!!'), 200

def run():
    app.run(host=settings.SERVER_ADDRESS, port=settings.SERVER_PORT, threaded=True)

