import cv2
import numpy as np
import matplotlib.pyplot as plt

# Función para mostrar imágenes usando matplotlib
def mostrar_imagen(titulo, imagen):
    plt.imshow(imagen, cmap='gray')
    plt.title(titulo)
    plt.axis('off')  
    plt.show()

# Inicializa la webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: No se pudo abrir la cámara.")
    exit()

# Configura el láser y el patrón de calibración
laser_power = 500  
calibration_pattern = "calibration_pattern.jpg"  

# Carga el patrón de calibración
calibration_image = cv2.imread(calibration_pattern, cv2.IMREAD_GRAYSCALE)
if calibration_image is None:
    print("Error: No se pudo cargar el patrón de calibración.")
    exit()

# Mostrar el patrón de calibración usando matplotlib
mostrar_imagen("Patrón de Calibración", calibration_image)

# Captura y procesa imágenes
print("Escaneando... Presiona 'q' para salir.")
while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: No se pudo capturar la imagen.")
        break

    # Convierte la imagen a escala de grises
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Aplica umbralización para detectar el láser
    _, thresholded = cv2.threshold(gray_frame, 150, 255, cv2.THRESH_BINARY)

    # Encuentra los contornos del láser
    contours, _ = cv2.findContours(thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        if cv2.contourArea(contour) > 100:  
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Mostrar la imagen procesada usando matplotlib
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  
    mostrar_imagen("Escaneo 3D", frame_rgb)

    # Presiona 'q' para salir
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libera los recursos
cap.release()
cv2.destroyAllWindows()

print("Escaneo completado.")
