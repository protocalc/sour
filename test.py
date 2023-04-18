import sour.sony as cam
import time

camera = cam.SONYconn(name='Sony RX0')

camera.initialize_camera(ControlMode='RemoteControl')

