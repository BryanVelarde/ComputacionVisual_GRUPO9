import cv2
import numpy as np
import os
import matplotlib.pyplot as plt

# Configuración del patrón de puntos
rows = 4  # Número de filas de puntos
cols = 11  # Número de columnas de puntos
point_spacing = 50  # Espaciado entre puntos en píxeles

# Crear una imagen en blanco
img_height = (rows + 1) * point_spacing
img_width = (cols + 1) * point_spacing
pattern_image = np.ones((img_height, img_width), dtype=np.uint8) * 255

# Dibujar los puntos
for i in range(1, rows + 1):
    for j in range(1, cols + 1):
        cv2.circle(pattern_image, 
                   (j * point_spacing, i * point_spacing), 
                   5,  # Radio del punto
                   (0, 0, 0), 
                   -1)

# Crear la carpeta de imágenes de calibración si no existe
output_folder = 'calibration_images'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Guardar la imagen del patrón de puntos
output_path = os.path.join(output_folder, 'dot_pattern.jpg')
cv2.imwrite(output_path, pattern_image)

print(f"Patrón de puntos guardado en: {output_path}")

# Mostrar la imagen del patrón de puntos usando matplotlib
plt.imshow(pattern_image, cmap='gray')
plt.title('Patrón de Puntos')
plt.axis('off')
plt.show()
