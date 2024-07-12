import cv2
import numpy as np
import matplotlib.pyplot as plt

# Ruta al video
video_path = 'videos/video4.mp4'

cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("Error al abrir el archivo de video")

ret, frame = cap.read()

cap.release()


if ret:

    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    plt.title('Imagen Original')
    plt.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    plt.subplot(1, 2, 2)
    plt.title('Imagen en HSV')
    plt.imshow(hsv_frame)
    
    plt.show()

    x, y, w, h = 66, 75, 221, 20  # <- se ingresan las coordenadas

    roi = hsv_frame[y:y+h, x:x+w]

    hsv_min = np.min(roi, axis=(0, 1))
    hsv_max = np.max(roi, axis=(0, 1))

    print(f'hsvMin = {hsv_min}')
    print(f'hsvMax = {hsv_max}')
else:
    print("Error al leer el primer cuadro del video")
