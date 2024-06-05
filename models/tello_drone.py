import logging
import socket
import threading
import time
import cv2
import subprocess
import numpy as np
import signal
import os
import contextlib

from utils.singleton import Singleton

logger = logging.getLogger(__name__)

HOST_IP = '192.168.10.2'
DRONE_IP = '192.168.10.1'
SEND_COMMAND_PORT = 8889
VIDEO_PORT = 11111
DEFAULT_DRONE_MOVE_DISTANTE = 0.30
DEFAULT_DRONE_MOVE_SPEED = 15
FRAME_X = int(960/3)
FRAME_Y = int(720/3)
FRAME_AREA = FRAME_X * FRAME_Y
# 画像はRBGで3次元
FRAME_SIZE = FRAME_AREA * 3
FRAME_CENTER_X = FRAME_X / 2
FRAME_CENTER_Y = FRAME_Y / 2

FFMPEG_COMMAND = (f'ffmpeg -hwaccel auto -hwaccel_device opencl -i pipe:0 '
                  f'-pix_fmt bgr24 -s {FRAME_X}x{FRAME_Y} -f rawvideo pipe:1')


FACE_DETECT_XML_FILE = './tello_drone_app/models/detection/face/haarcascade_frontalface_default.xml'


class TelloDrone(metaclass=Singleton):
    def __init__(self, host_ip=HOST_IP, host_port=SEND_COMMAND_PORT, 
              drone_ip=DRONE_IP, drone_port=SEND_COMMAND_PORT, 
                 move_speed=DEFAULT_DRONE_MOVE_SPEED, video_port=VIDEO_PORT):
        
        self.host_ip = host_ip
        self.host_port = host_port                    
        
        self.drone_ip = drone_ip
        self.drone_port = drone_port
        self.drone_address = (self.drone_ip, self.drone_port)
        self.move_speed = move_speed
        self.video_port = video_port

        self.stop_flag = threading.Event()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.host_ip, self.host_port))
        self.response = None
        self._receive_thread = threading.Thread(target=self.receive_drone_response, args=(self.stop_flag, ))
        self._receive_thread.start()

        self.video_proc = subprocess.Popen(FFMPEG_COMMAND.split(' '), stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        self.video_proc_stdin = self.video_proc.stdin
        self.video_proc_stdout = self.video_proc.stdout
        self._receive_video_thread = threading.Thread(target=self.receive_drone_video, 
                                                      args=(self.stop_flag, self.video_proc_stdin,
                                                            self.host_ip, self.video_port))
        # self._receive_video_thread.start()

        if not os.path.exists(FACE_DETECT_XML_FILE):
            raise ErrorNotFoundFaceDetectXmlFile(f'{FACE_DETECT_XML_FILE} is not exists')
        self.face_cascade = cv2.CascadeClassifier(FACE_DETECT_XML_FILE)
        self._is_use_face_detect = False


        self._command_semaphore = threading.Semaphore(1)
        self._command_thread = None

        # コマンドの初期化
        self.socket.sendto(b'command', self.drone_address)
        self.socket.sendto(b'streamon', self.drone_address)

        self.set_speed(self.move_speed)

    def __del__(self):
        self.stop()

    def stop(self):
        self.stop_flag.set()
        self.socket.close()
        os.kill(self.video_proc.pid, signal.CTRL_C_EVENT)
        print('ffmpeg is killed!!!!!!!!!!!!')
        

    def receive_drone_response(self, stop_flag):
        while not stop_flag.is_set():
            try:
                # Telloのサンプルコードと同様に3000
                self.response, ip = self.socket.recvfrom(3000)
                logger.info(f'receive_thread: {self.response}')
            except socket.error as ex:
                logger.error(f'Caught exception socket.error: {ex} at receive_drone_response')
                break

    def receive_drone_video(self, stop_flag, pipe_in, host_ip,video_port):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as socket_video:
            socket_video.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            socket_video.settimeout(.5)
            socket_video.bind((host_ip, video_port))
            video_data = bytearray(2048)

            while not stop_flag.is_set():
                try:
                    data_size, address = socket_video.recvfrom_into(video_data)
                    # logger.info(f'receive_drone_video: {video_data}')
                except socket.timeout as ex:
                    logger.warning(f'Caught exception socket.timeout: {ex} at receive_drone_video')
                    time.sleep(0.5)
                    continue
                except socket.error as ex:
                    logger.error(f'Caught exception socket.error: {ex} at receive_drone_video')
                    break

                try:
                    pipe_in.write(video_data[:data_size])
                    pipe_in.flush()
                except Exception as ex:
                    logger.error(f'Caught exception: {ex} at receive_drone_video')
                    break


    def send_command(self, command, blocknig=True):
        self._command_thread = threading.Thread(
            target=self._send_command,
            args=(command, blocknig,))
        self._command_thread.start()
    
    def _send_command(self, command, blocknig=True):

        is_acquire = self._command_semaphore.acquire(blocking=blocknig)
        if is_acquire:
            with contextlib.ExitStack() as stack:
                stack.callback(self._command_semaphore.release)
                logger.info(f'send_command: {command}')
                self.socket.sendto(command.encode('utf-8'), self.drone_address)

                retry = 0
                while self.response is None:
                    time.sleep(0.3)
                    if retry > 3:
                        break
                    retry += 1

                if self.response is None:
                    response = None
                else:
                    response = self.response.decode('utf-8')

                self.response = None
                
                return response
        else:
            logger.warning(f'Not acquire')

    
    def set_speed(self, speed):
        return self.send_command(f'speed {speed}')

    def takeoff(self):
        return self.send_command('takeoff')

    def land(self):
        return self.send_command('land')
    
    def move(self, direction, distance):
        distance = float(distance)
        distance = int(round(distance * 100))
        return self.send_command(f'{direction} {distance}')
    
    def move_forward(self, distance=DEFAULT_DRONE_MOVE_DISTANTE):
        return self.move('forward', distance)
    
    def move_backward(self, distance=DEFAULT_DRONE_MOVE_DISTANTE):
        return self.move('back', distance)
    
    def move_up(self, distance=DEFAULT_DRONE_MOVE_DISTANTE):
        return self.move('up', distance)

    def move_down(self, distance=DEFAULT_DRONE_MOVE_DISTANTE):
        return self.move('down', distance)

    def move_right(self, distance=DEFAULT_DRONE_MOVE_DISTANTE):
        return self.move('right', distance)

    def move_left(self, distance=DEFAULT_DRONE_MOVE_DISTANTE):
        return self.move('left', distance)
    
    def rotate_clockwise(self, degrees=90):
        return self.send_command(f'cw {degrees}')

    def rotate_counter_clockwise(self, degrees=90):
        return self.send_command(f'ccw {degrees}')

    def flip(self, direction):
        return self.send_command(f'flip {direction}')
    
    def flip_forward(self):
        return self.flip('f')
    
    def flip_back(self):
        return self.flip('b')
    
    def flip_right(self):
        return self.flip('r')
    
    def flip_left(self):
        return self.flip('l')
    
    def video_binary_generator(self):
        while True:
            try:
                frame = self.video_proc_stdout.read(FRAME_SIZE)
            except Exception as ex:
                logger.error(f'Caught exception : {ex} at video_binary_generator')
                continue

            if not frame:
                continue
                
            frame = np.fromstring(frame, np.uint8).reshape(FRAME_Y, FRAME_X, 3) 
            yield frame

    def enable_face_detect(self):
        self._is_use_face_detect = True

    def disable_face_detect(self):
        self._is_use_face_detect = False
        
    def video_jpeg_generator(self):
        for frame in self.video_binary_generator():
            
            if self._is_use_face_detect:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x,y), (x+w, y+h), (255, 0, 0), 2)

                    face_cnter_x = x  + (w/2)
                    face_cnter_y = y  + (h/2)

                    diff_x = FRAME_CENTER_X - face_cnter_x
                    diff_y = FRAME_CENTER_Y - face_cnter_y
                    face_area = w * h
                    percent_face = face_area / FRAME_AREA

                    drone_x, drone_y, drone_z, speed = 0, 0, 0, self.move_speed
                    if diff_x < -30:
                        drone_y = -30
                    if diff_x > 30:
                        drone_y = 30
                    if diff_y < -15:
                        drone_z = -30
                    if diff_y > 15:
                        drone_z = 30
                    if percent_face < 0.02:
                        drone_x = 30
                    if percent_face > 0.30:
                        drone_x = -30
                    
                    self.send_command(f'go {drone_x} {drone_y} {drone_z} {speed}', blocknig=False)
 
                    break

            _, jpeg = cv2.imencode('.jpg', frame)
            jpeg_binary = jpeg.tobytes()
            yield jpeg_binary



class ErrorNotFoundFaceDetectXmlFile(Exception):
    """Eroror no face detect xml file"""