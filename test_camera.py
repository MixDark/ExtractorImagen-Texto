import cv2
import time

print("Probando cámara...")
print(f"OpenCV versión: {cv2.__version__}")

# Intentar con CAP_DSHOW (Windows)
print("\nIntentando con CAP_DSHOW...")
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("❌ No se pudo abrir con CAP_DSHOW, intentando con VideoCapture(0)...")
    cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ No se pudo abrir la cámara")
    exit(1)

print("✓ Cámara abierta exitosamente")

# Configurar
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)

print("Calentando cámara...")
for i in range(10):
    ret, frame = cap.read()
    if ret:
        print(f"  Frame {i+1}: OK - Shape: {frame.shape}")
    else:
        print(f"  Frame {i+1}: FALLO")
    time.sleep(0.1)

print("\nLeyendo 5 frames...")
for i in range(5):
    ret, frame = cap.read()
    if ret:
        print(f"✓ Frame {i+1}: {frame.shape}")
    else:
        print(f"❌ Frame {i+1}: No se pudo leer")

cap.release()
print("\n✓ Prueba completada")
