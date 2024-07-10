import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

# Cargar los parámetros de calibración
try:
    with np.load('calibration_images/calibracion_puntos.npz') as X:
        mtx, dist, rvecs, tvecs = [X[i] for i in ('mtx', 'dist', 'rvecs', 'tvecs')]
except FileNotFoundError:
    print("Error: No se pudo encontrar el archivo de calibración 'calibracion_puntos.npz'.")
    exit()

# Crear un directorio para guardar las imágenes
output_dir = 'captured_images'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Inicializa la webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: No se pudo abrir la cámara.")
    exit()

# Captura de imágenes
images = []
print("Escaneando... Presiona 'q' para salir.")
plt.ion()  # Habilitar modo interactivo para matplotlib
fig, ax = plt.subplots()
image_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: No se pudo capturar la imagen.")
        break

    # Mostrar la imagen capturada utilizando matplotlib
    ax.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    ax.set_title("Escaneo 3D")
    ax.axis('off')
    plt.draw()
    plt.pause(0.001)  # Pausa breve para permitir la actualización de la ventana

    # Almacenar la imagen en memoria
    images.append(frame.copy())

    # Guardar la imagen en el disco
    image_path = os.path.join(output_dir, f'image_{image_count:04d}.png')
    cv2.imwrite(image_path, frame)
    image_count += 1

    # Presiona 'q' para salir
    if plt.waitforbuttonpress(0.1):  # Espera a que se presione una tecla
        if plt.get_fignums():  # Verifica si la figura sigue abierta
            break

# Libera los recursos
cap.release()
plt.close('all')

# Procesar imágenes y detectar el láser
laser_lines = []
for img in images:
    gray_frame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresholded = cv2.threshold(gray_frame, 150, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours:
        if cv2.contourArea(contour) > 100:
            x, y, w, h = cv2.boundingRect(contour)
            laser_lines.append((x + w // 2, y + h // 2))

# Convertir las coordenadas de píxeles a coordenadas del mundo real usando los parámetros de calibración
points_3d = []
for line in laser_lines:
    x, y = line
    z = 0  # Suponiendo que la superficie es plana en z=0
    undistorted_point = cv2.undistortPoints(np.array([[x, y]], dtype=np.float32), mtx, dist).flatten()
    points_3d.append([undistorted_point[0], undistorted_point[1], z])

# Convertir a numpy array
points_3d = np.array(points_3d)

# Mostrar los puntos 3D
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(points_3d[:, 0], points_3d[:, 1], points_3d[:, 2])
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
plt.show()

