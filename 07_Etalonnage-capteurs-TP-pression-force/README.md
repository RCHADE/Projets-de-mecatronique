# Étalonnage de capteurs — Pression & Force

Étalonnage de capteurs à partir de données expérimentales réelles.
Modélisation de la relation tension/grandeur physique par régression linéaire,
validation statistique et filtrage du signal.

## Capteurs traités
- **Capteur de pression** — tension (mV) → pression (mmHg)
- **Capteur de force** — tension (V) → poids (g), deux gammes de gain (×1000, ×10000)

## Méthodes
- Régression linéaire (polyfit)
- Validation : R², MAE, RMSE
- Comparaison régression vs interpolation
- Filtrage passe-bas Butterworth (débruitage signal)

## Structure
- `data/` — données expérimentales CSV
- `Code_Python/` — script Python (NumPy, SciPy, sklearn, matplotlib)
- `Code_Matlab/` — script MATLAB équivalent
- `figures/` — graphiques générés
- `Document/` — rapport de TP

## Lancer

Python :
```bash
pip install numpy pandas matplotlib scipy scikit-learn
python Code_Python/etalonnage.py
```

MATLAB :
```
Run Code_Matlab/etalonnage.m
```

## Résultats
![Étalonnage capteurs](figures/etalonnage_capteurs.png)
![Filtrage signal](figures/filtrage_signaux.png)