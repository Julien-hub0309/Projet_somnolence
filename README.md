# Cahier des charges

## Système de détection de somnolence au volant

### 1. **Contexte du projet**

Dans le cadre de la réglementation européenne imposant l’intégration de systèmes de surveillance du conducteur (Driver Monitoring System), l’entreprise **Forvia** souhaite développer une solution embarquée capable de détecter :

- La **somnolence** du conducteur
    
- La **distraction** (regard détourné de la route)
    

L’objectif est de proposer une **preuve de faisabilité** (prototype fonctionnel) démontrant que ces exigences peuvent être satisfaites sur un système embarqué.

### 2. **Objectif général**

Concevoir et réaliser un système embarqué capable :

1. D’analyser en temps réel l’état du conducteur via une caméra.
    
2. De détecter les signes de somnolence et de distraction.
    
3. D’émettre une alerte adaptée lorsque l’état du conducteur devient dangereux.
    

### 3. **Fonctions principales du système**

#### 3.1 Détection de la somnolence

- Détecter la fermeture prolongée des yeux.
    
- Mesurer le **temps de fermeture** des paupières.
    
- Déterminer deux niveaux :
    
    - **Micro-sieste** : fermeture > 3,5 s à vitesse > 50 km/h
        
    - **Somnolence importante** : fermeture > 5 s
        

#### 3.2 Détection de la distraction

- Détecter l’orientation du visage.
    
- Déterminer si le conducteur **ne regarde plus la route**.
    
- Mesurer le **temps d’inattention** (seuil à définir).
    

#### 3.3 Avertissement du conducteur

- Déclencher une alerte en cas de danger.
    
- Types d’alertes :
    
    - **Visuelle** (message sur IHM)
        
    - **Sonore** (signal variable selon gravité)
        
    - **Haptique** (vibration)
        
- Messages prévus :
    
    - Somnolence : _« Pause et arrêt fortement recommandés »_
        
    - Distraction : vibration simple
        

#### 3.4 Interface Homme-Machine (IHM)

- Afficher les alertes visuelles.
    
- Permettre d’activer/désactiver le système.
    
    - Le système doit être **actif par défaut**.
        

#### 3.5 Communication

- Le système doit pouvoir communiquer avec l’ordinateur de bord (simulation possible dans le prototype).
    

### 4. **Contraintes techniques**

#### 4.1 Matériel

- Caméra embarquée orientée vers le conducteur.
    
- Plateforme embarquée (Raspberry Pi, Jetson Nano, PC embarqué… selon choix de l’équipe).
    
- Capteurs de vibration / buzzer pour alertes haptiques et sonores.
    

#### 4.2 Logiciel

- Traitement d’image en temps réel.
    
- Détection des yeux et orientation du visage (OpenCV, IA, etc.).
    
- Mesure des durées (fermeture, inattention).
    
- Gestion des alertes.
    
- Interface utilisateur simple et lisible.
    

#### 4.3 Performances attendues

- Analyse vidéo en temps réel (≥ 10–15 FPS).
    
- Détection fiable dans des conditions normales d’éclairage.
    
- Temps de réaction du système < 1 seconde après détection.
    

### 5. **Contraintes réglementaires**

- Respect des exigences européennes concernant les systèmes DMS (Driver Monitoring System).
    
- Alerte obligatoire si somnolence détectée au-dessus des seuils réglementaires.
    
- Système désactivable mais actif par défaut.
    

### 6. **Plan de validation**

Le système devra être validé via :

#### 6.1 Tests unitaires

- Détection des yeux
    
- Détection de l’orientation du visage
    
- Mesure du temps de fermeture
    
- Déclenchement des alertes
    

#### 6.2 Tests d’intégration

- Fonctionnement global du pipeline vidéo → analyse → décision → alerte
    
- Interaction avec l’IHM
    

#### 6.3 Tests de performance

- Temps de traitement
    
- Robustesse en conditions variées (lunettes, faible luminosité…)
    

#### 6.4 Démonstration finale

- Présentation d’un prototype fonctionnel montrant :
    
    - Détection de somnolence
        
    - Détection de distraction
        
    - Déclenchement des alertes
        

### 7. **Livrables attendus**

- Cahier des charges (ce document)
    
- Architecture matérielle et logicielle
    
- Code source commenté
    
- Plan de validation + résultats des tests
    
- Prototype fonctionnel
    
- Présentation orale finale

---

# Première séance : 

## Connexion SSH à la Raspberry Pi : 

- sudo apt install ssh 
- sudo nano /etc/ssh/sshd_config
- ssh cielssh@172.30.103.91

## Création d’un dossier de travail dédié au groupe : 

- cd /home/user/Documents
- mkdir projet somnolence

## Lancement et test du script fourni : 
- python3 somnolence.py

---
## Code applicatif : 

### 1. Correction de la Logique : Détecter l'absence d'yeux

Le problème principal des Cascades de Haar est qu'elles détectent des yeux **ouverts**. Pour détecter la somnolence, nous devons compter le nombre de frames (images) où les yeux ne sont **pas** détectés alors que le visage l'est.

### 2. Ajout d'un compteur de "Frames de Sommeil"

Si les yeux ne sont pas détectés pendant, disons, 15 frames consécutives, on peut considérer que la personne s'endort.


```py
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
ALARM_THRESHOLD = 15  # Nombre de frames consécutives yeux fermés avant alerte
print("Système actif. Appuyez sur 'q' pour quitter.")

while True:
    ok, frame = cap.read()
    if not ok:
        break
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Amélioration du contraste pour une meilleure détection
    gray = cv2.equalizeHist(gray)
    faces = face_cascade.detectMultiScale(gray, 1.2, 5, minSize=(100, 100)
  

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
                        
    cv2.imshow("Somnolence Detector", frame)
    
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
cap.release()
cv2.destroyAllWindows()

```

---
