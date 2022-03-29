import json
import socket
from websocket import create_connection, WebSocket
import threading

ws = None

active_keys = set([])
connected_positions = set([])


class WebSocketReceiver(WebSocket):
    def recv_frame(self):
        global active_keys
        global connected_positions
        frame = super().recv_frame()
        try:
            frame_obj = json.loads(frame.data)
            active = frame_obj['ActiveKeys']

            # if len(active) > 0:
            #     print (active)
            active_keys = set(active)
            connected_positions = set(frame_obj['ConnectedPositions'])
        except:
            # active_keys = set([])
            # connected_positions = set([])
            #print('')
            pass

        return frame


def thread_function(name):
    while True:
        if ws is not None:
            ws.recv_frame()


def initialize():
    global ws
    try:
        ws = create_connection("ws://localhost:15881/v2/feedbacks",
                               sockopt=((socket.IPPROTO_TCP, socket.TCP_NODELAY, 1),),
                               class_=WebSocketReceiver)

        x = threading.Thread(target=thread_function, args=(1,))
        x.start()
    except:
        #print("Couldn't connect")
        return


def destroy():
    if ws is not None:
        ws.close()


def is_playing():
    return len(active_keys) > 0


def is_playing_key(key):
    return key in active_keys


# position Vest Head ForeamrL ForearmR HandL HandR FootL FootR
def is_device_connected(position):
    return position in connected_positions


def register(key, file_directory):
    json_data = open(file_directory).read()

    #print(json_data)

    data = json.loads(json_data)
    project = data["project"]

    layout = project["layout"]
    tracks = project["tracks"]

    request = {
        "Register": [{
            "Key": key,
            "Project": {
                "Tracks": tracks,
                "Layout": layout
            }
        }]
    }

    json_str = json.dumps(request)
    __submit(json_str)


def submit_registered(key):
    request = {
        "Submit": [{
            "Type": "key",
            "Key": key,
        }]
    }

    json_str = json.dumps(request)

    __submit(json_str)


def submit_registered_with_option(
        key, alt_key,
        scale_option,
        rotation_option):
    # scaleOption: {"intensity": 1, "duration": 1}
    # rotationOption: {"offsetAngleX": 90, "offsetY": 0}
    request = {
        "Submit": [{
            "Type": "key",
            "Key": key,
            "Parameters": {
                "altKey": alt_key,
                "rotationOption": rotation_option,
                "scaleOption": scale_option,
            }
        }]
    }

    json_str = json.dumps(request);

    __submit(json_str)


def submit(key, frame):
    request = {
        "Submit": [{
            "Type": "frame",
            "Key": key,
            "Frame": frame
        }]
    }

    json_str = json.dumps(request);

    __submit(json_str)


def submit_dot(key, position, dot_points, duration_millis):
    front_frame = {
        "position": position,
        "dotPoints": dot_points,
        "durationMillis": duration_millis
    }
    submit(key, front_frame)


def __submit(json_str):
    if ws is not None:
        ws.send(json_str)
