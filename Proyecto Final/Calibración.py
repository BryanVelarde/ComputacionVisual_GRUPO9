import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

# Configuración del patrón de puntos
pattern_size = (11, 4)  # Número de puntos en el patrón (ancho, alto)

# Criterios de terminación
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# Lista de nombres de archivos de imagen
images = [
    'calibration_images/dot_pattern.jpg',
    'calibration_images/1.jpg',
    'calibration_images/2.jpg',
    'calibration_images/3.jpg'
]

# Función para verificar si el archivo existe
def verificar_archivo(filepath):
    if not os.path.exists(filepath):
        print(f"Advertencia: No se pudo encontrar el archivo {filepath}")
        return False
    return True

# Arreglos para almacenar los puntos de objetos y los puntos de imagen de todas las imágenes.
objpoints = []  # Puntos 3D en el mundo real
imgpoints = []  # Puntos 2D en el plano de la imagen.

# Puntos de objeto 3D
objp = np.zeros((pattern_size[0] * pattern_size[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:pattern_size[0], 0:pattern_size[1]].T.reshape(-1, 2)

# Variable para almacenar el tamaño de la imagen
img_shape = None

results_final = []

for filepath in images:
    if not verificar_archivo(filepath):
        continue

    img = cv2.imread(filepath)
    if img is None:
        results_final.append(f"Error: No se pudo cargar la imagen {filepath}")
        continue
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)  # Mejorar el contraste
    gray = cv2.GaussianBlur(gray, (5, 5), 0)  # Aplicar filtro de desenfoque
    
    # Buscar los círculos del patrón de puntos
    ret, centers = cv2.findCirclesGrid(gray, pattern_size, cv2.CALIB_CB_SYMMETRIC_GRID)

    if ret:
        results_final.append(f'Puntos encontrados en {os.path.basename(filepath)}')
        imgpoints.append(centers)
        objpoints.append(objp)

        img = cv2.drawChessboardCorners(img, pattern_size, centers, ret)
        
        # Mostrar los puntos detectados
        plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        plt.title(f'Puntos del Patrón de Puntos Detectados: {os.path.basename(filepath)}')
        plt.axis('off')
        plt.show()
    else:
        results_final.append(f'No se encontraron puntos en {os.path.basename(filepath)}')

# Verificar que se han encontrado puntos en al menos una imagen
if imgpoints:
    # Calibrar la cámara
    img_shape = gray.shape[::-1]
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, img_shape, None, None)

    # Guardar los resultados de la calibración
    np.savez('calibration_images/calibracion_puntos.npz', mtx=mtx, dist=dist, rvecs=rvecs, tvecs=tvecs)

    results_final.append("Calibración completada y guardada.")
else:
    results_final.append("No se encontraron puntos en las imágenes de calibración.")

results_final
