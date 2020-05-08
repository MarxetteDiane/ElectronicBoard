import numpy as np
import cv2
import os
from collections import deque

blueLower = np.array([100, 60, 60])
blueUpper = np.array([140, 255, 255])

kernel = np.ones((5, 5), np.uint8)

black_points = [deque(maxlen=512)]
blue_points = [deque(maxlen=512)]
green_points = [deque(maxlen=512)]
red_points = [deque(maxlen=512)]
yellow_points = [deque(maxlen=512)]

black_index = 0
blue_index = 0
green_index = 0
red_index = 0
yellow_index = 0

colors = [(0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 255, 255)]
colored_index = 0

# Color Box Sizes
drawWindow = np.zeros((471,636,3)) + 255
drawWindow = cv2.circle(drawWindow, (40, 30), 25, (0,0,0), 2)
drawWindow = cv2.circle(drawWindow, (100, 30), 25, colors[0], -1)
drawWindow = cv2.circle(drawWindow, (160, 30), 25, colors[1], -1)
drawWindow = cv2.circle(drawWindow, (220, 30), 25, colors[2], -1)
drawWindow = cv2.circle(drawWindow, (280, 30), 25, colors[3], -1)
drawWindow = cv2.circle(drawWindow, (340, 30), 25, colors[4], -1)

cv2.namedWindow('Paint', cv2.WINDOW_AUTOSIZE)

filename = 'video.avi'
frames_per_second = 24.0
res = '720p'

cv2.namedWindow('Paint', cv2.WINDOW_AUTOSIZE)

def change_res(camera, width, height):
    camera.set(3, width)
    camera.set(4, height)

# Standard Video Dimensions Sizes
STD_DIMENSIONS = {
    "480p": (640, 480),
    "720p": (1280, 720),
    "1080p": (1920, 1080),
    "4k": (3840, 2160),
}

# grab resolution dimensions and set video capture to it.
def get_dims(camera, res='1080p'):
    width, height = STD_DIMENSIONS["480p"]
    if res in STD_DIMENSIONS:
        width, height = STD_DIMENSIONS[res]
    ## change the current caputre device
    ## to the resulting resolution
    change_res(camera, width, height)
    return width, height

VIDEO_TYPE = {
    'avi': cv2.VideoWriter_fourcc(*'XVID'),
    # 'mp4': cv2.VideoWriter_fourcc(*'H264'),
    'mp4': cv2.VideoWriter_fourcc(*'XVID'),
}

def get_video_type(filename):
    filename, ext = os.path.splitext(filename)
    if ext in VIDEO_TYPE:
        return VIDEO_TYPE[ext]
    return VIDEO_TYPE['avi']

camera = cv2.VideoCapture(0)
out = cv2.VideoWriter(filename, get_video_type(filename), 25, get_dims(camera, res))

while True:
    (grabbed, frame) = camera.read()
    frame = cv2.flip(frame, 1)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Color Circles
    frame = cv2.circle(frame, (40, 30), 25, (122, 122, 122), -1)
    frame = cv2.circle(frame, (100, 30), 25, colors[0], -1)
    frame = cv2.circle(frame, (160, 30), 25, colors[1], -1)
    frame = cv2.circle(frame, (220, 30), 25, colors[2], -1)
    frame = cv2.circle(frame, (280, 30), 25, colors[3], -1)
    frame = cv2.circle(frame, (340, 30), 25, colors[4], -1)

    if not grabbed:
        break

    blueMask = cv2.inRange(hsv, blueLower, blueUpper)
    blueMask = cv2.erode(blueMask, kernel, iterations=2)
    blueMask = cv2.morphologyEx(blueMask, cv2.MORPH_OPEN, kernel)
    blueMask = cv2.dilate(blueMask, kernel, iterations=1)

    (cnts, _) = cv2.findContours(blueMask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    center = None

    if len(cnts) > 0:
        cnt = sorted(cnts, key=cv2.contourArea, reverse=True)[0]
        ((x, y), radius) = cv2.minEnclosingCircle(cnt)
        M = cv2.moments(cnt)
        center = (int(M['m10'] / M['m00']), int(M['m01'] / M['m00']))

        if center[1] <= 50:
            if 15 <= center[0] <= 65:  # Clear All
                black_points = [deque(maxlen=512)]
                blue_points = [deque(maxlen=512)]
                green_points = [deque(maxlen=512)]
                red_points = [deque(maxlen=512)]
                yellow_points = [deque(maxlen=512)]

                black_index = 0
                blue_index = 0
                green_index = 0
                red_index = 0
                yellow_index = 0

                drawWindow[67:, :, :] = 255
            elif 75 <= center[0] <= 125:
                colored_index = 0  # Black
            elif 135 <= center[0] <= 185:
                colored_index = 1  # Blue
            elif 195 <= center[0] <= 245:
                colored_index = 2  # Green
            elif 255 <= center[0] <= 305:
                colored_index = 3  # Red
            elif 315 <= center[0] <= 365:
                colored_index = 4  # Yellow
        else:
            if colored_index == 0:
                black_points[black_index].appendleft(center)
            elif colored_index == 1:
                blue_points[blue_index].appendleft(center)
            elif colored_index == 2:
                green_points[green_index].appendleft(center)
            elif colored_index == 3:
                red_points[red_index].appendleft(center)
            elif colored_index == 4:
                yellow_points[yellow_index].appendleft(center)

    else:
        black_points.append(deque(maxlen=512))
        black_index += 1
        blue_points.append(deque(maxlen=512))
        blue_index += 1
        green_points.append(deque(maxlen=512))
        green_index += 1
        red_points.append(deque(maxlen=512))
        red_index += 1
        yellow_points.append(deque(maxlen=512))
        yellow_index += 1

    points = [black_points, blue_points, green_points, red_points, yellow_points]
    for i in range(len(points)):
        for j in range(len(points[i])):
            for k in range(1, len(points[i][j])):
                if points[i][j][k - 1] is None or points[i][j][k] is None:
                    continue
                cv2.line(frame, points[i][j][k - 1], points[i][j][k], colors[i], 5)
                cv2.line(drawWindow, points[i][j][k - 1], points[i][j][k], colors[i], 10)

    cv2.imshow("Tracking", frame)
    # cv2.imshow("Paint", drawWindow)
    out.write(frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
out.release()
cv2.destroyAllWindows()