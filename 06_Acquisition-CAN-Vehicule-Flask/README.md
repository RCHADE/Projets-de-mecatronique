# 06_Acquisition-CAN-Vehicule-Flask

## Description
- Lecture des données CAN véhicule via Arduino + MCP2515
- Transmission série vers PC
- Dashboard Flask pour visualisation temps réel

## Données affichées
- Régime moteur
- Vitesse
- Température
- Niveau carburant
- Accélération
- Charge moteur

## Structure
- `arduino_code/can_reader.ino` : code Arduino
- `acquisition_du_donnee.py` : lecture série
- `app.py` : serveur Flask
- `templates/index.html` : dashboard

## Utilisation
1. Uploader le code Arduino
2. Lancer acquisition_du_donnee.py
3. Lancer app.py
4. Ouvrir http://127.0.0.1:5000