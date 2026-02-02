import sys
import cv2
import time

# --- Configuration de la caméra ---
if sys.platform.startswith("win"):
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
else:
    cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cap.isOpened():
    raise RuntimeError("Impossible d'ouvrir la webcam.")

# --- Chargement des Cascades ---
# Utilisation du chemin cv2.data.haarcascades pour plus de fiabilité
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")

if face_cascade.empty() or eye_cascade.empty():
    raise RuntimeError("Erreur lors du chargement des fichiers XML de Haar.")

# --- Variables de contrôle de somnolence ---
eye_closed_counter = 0
ALARM_THRESHOLD = 15  # Nombre de frames consécutives yeux fermés avant alerte

print("Système actif. Appuyez sur 'q' pour quitter.")

while True:
    ok, frame = cap.read()
    if not ok:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Amélioration du contraste pour une meilleure détection
    gray = cv2.equalizeHist(gray) 

    faces = face_cascade.detectMultiScale(gray, 1.2, 5, minSize=(100, 100))

    if len(faces) == 0:
        # Optionnel : On peut réinitialiser le compteur si aucun visage n'est vu
        eye_closed_counter = 0
    
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        roi_gray = gray[y:y+h, x:x+w]
        roi_color = frame[y:y+h, x:x+w]

        # Détection des yeux dans la zone du visage
        eyes = eye_cascade.detectMultiScale(roi_gray, 1.1, 10, minSize=(30, 30))

        # LOGIQUE DE SOMNOLENCE :
        if len(eyes) == 0:
            eye_closed_counter += 1
        else:
            eye_closed_counter = 0
            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (255, 0, 0), 2)

        # Si le compteur dépasse le seuil, on affiche une alerte
        if eye_closed_counter >= ALARM_THRESHOLD:
            cv2.putText(frame, "!!! ALERTE SOMNOLENCE !!!", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
            # Ici tu pourrais ajouter un son avec : print('\a') 

    cv2.imshow("Somnolence Detector", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()