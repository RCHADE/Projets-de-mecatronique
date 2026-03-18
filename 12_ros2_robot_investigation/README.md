# Robot Investigation — ROS2

Simulation d'un robot d'investigation avec 4 nœuds ROS2 communiquant via topics.
Inspiré des architectures robotiques pour environnements contraints (CEA Marcoule).

## Architecture
```
┌─────────────────┐
│   sensor_node   │
│  (génère data)  │
└────────┬────────┘
         │ /sensor_data (Float32)
         ├──────────────────────────┐──────────────────────┐
         │                          │                       │
┌────────▼────────┐        ┌────────▼────────┐    ┌────────▼────────┐
│  teleop_node    │        │  logger_node    │    │   visu_node     │
│ (décide action) │        │ (CSV + alarmes) │    │ (plot temps réel│
└────────┬────────┘        └─────────────────┘    └─────────────────┘
         │ /cmd_vel (Twist)
         ▼
    Robot mobile (simulé)
```

## Nœuds

- **sensor_node** — publie une distance simulée (sinus + bruit gaussien) sur `/sensor_data` toutes les 500ms
- **teleop_node** — souscrit à `/sensor_data`, publie sur `/cmd_vel` : avance si distance > 0.5m, stop et tourne sinon
- **logger_node** — souscrit aux deux topics, enregistre dans un CSV horodaté, lève une alarme si distance < 0.3m
- **visu_node** — trace la distance en temps réel (ligne bleue = OK, rouge = obstacle)

## Lancer
```bash
# Terminal 1 — tous les nœuds sauf visu
ros2 launch investigation_robot robot.launch.py

# Terminal 2 — visualisation temps réel
ros2 run investigation_robot visu_node
```

## Outils
| Outil | Rôle |
|-------|------|
| ROS2 Jazzy | Communication entre nœuds |
| rclpy | API Python ROS2 |
| geometry_msgs/Twist | Commandes vitesse robot |
| matplotlib | Visualisation temps réel |
| colcon | Build du workspace |