"""
PROJET D'ÉTALONNAGE DE CAPTEURS
Lecture des données depuis des fichiers CSV
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import interpolate
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import os

# ============================================================
# 1. CHARGEMENT DES DONNÉES DEPUIS CSV
# ============================================================

# Obtenir le chemin absolu du répertoire du script
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)  # Remonter d'un niveau
data_dir = os.path.join(project_root, 'data')

# Chargement capteur pression
pression_file = os.path.join(data_dir, 'capteur_pression.csv')
df_pression = pd.read_csv(pression_file)
pression_mmHg = df_pression['pression_mmHg'].values
tension_mV = df_pression['tension_mV'].values
tension_V = tension_mV / 1000.0

print("✅ Données de pression chargées:")
print(f"   {len(pression_mmHg)} points de mesure")
print(f"   Plage: {min(pression_mmHg)}-{max(pression_mmHg)} mmHg")

# Chargement capteur force
force_file = os.path.join(data_dir, 'capteur_force.csv')
df_force = pd.read_csv(force_file)

# Séparation par gain
df_gain10000 = df_force[df_force['gain'] == 10000]
df_gain1000 = df_force[df_force['gain'] == 1000]

poids1 = df_gain10000['poids_g'].values
tension1 = df_gain10000['tension_V'].values

poids2 = df_gain1000['poids_g'].values
tension2 = df_gain1000['tension_V'].values

print("\n✅ Données de force chargées:")
print(f"   Gain 10000: {len(poids1)} points (poids {min(poids1)}-{max(poids1)} g)")
print(f"   Gain 1000: {len(poids2)} points (poids {min(poids2)}-{max(poids2)} g)")

# ============================================================
# 2. ANALYSE CAPTEUR PRESSION
# ============================================================

print("\n" + "="*60)
print("ANALYSE CAPTEUR DE PRESSION")
print("="*60)

# Régression linéaire
coeffs = np.polyfit(tension_V, pression_mmHg, 1)
a, b = coeffs[0], coeffs[1]
print(f"\n📈 Modèle: Pression (mmHg) = {a:.2f} × Tension (V) + {b:.2f}")

# Prédictions et métriques
pression_pred = a * tension_V + b
r2 = r2_score(pression_mmHg, pression_pred)
mae = mean_absolute_error(pression_mmHg, pression_pred)
rmse = np.sqrt(mean_squared_error(pression_mmHg, pression_pred))

print(f"\n📊 Qualité du modèle:")
print(f"   R² = {r2:.6f}")
print(f"   Erreur moyenne = {mae:.2f} mmHg")
print(f"   RMSE = {rmse:.2f} mmHg")
print(f"   Sensibilité = {a:.2f} mmHg/V ({a/1000:.4f} mmHg/mV)")

# ============================================================
# 3. ANALYSE CAPTEUR FORCE
# ============================================================

print("\n" + "="*60)
print("ANALYSE CAPTEUR DE FORCE")
print("="*60)

# Gamme 1 (Gain 10000)
coeffs1 = np.polyfit(tension1, poids1, 1)
a1, b1 = coeffs1[0], coeffs1[1]
print(f"\n📈 Gamme 1 (Gain=10000): Poids (g) = {a1:.1f} × Tension (V) + {b1:.2f}")

# Gamme 2 (Gain 1000)
coeffs2 = np.polyfit(tension2, poids2, 1)
a2, b2 = coeffs2[0], coeffs2[1]
print(f"📈 Gamme 2 (Gain=1000): Poids (g) = {a2:.1f} × Tension (V) + {b2:.2f}")

# ============================================================
# 4. FONCTIONS D'ÉTALONNAGE
# ============================================================

def pression_from_tension(V):
    """Convertit tension (V) en pression (mmHg)"""
    return a * V + b

def poids_from_tension(V, gain):
    """Convertit tension (V) en poids (g) selon le gain"""
    if gain == 10000:
        return a1 * V + b1
    elif gain == 1000:
        return a2 * V + b2
    else:
        raise ValueError(f"Gain {gain} non supporté")

# Test des fonctions
print("\n" + "="*60)
print("TEST DES FONCTIONS D'ÉTALONNAGE")
print("="*60)

test_V_pression = 0.200
p_calc = pression_from_tension(test_V_pression)
print(f"\n🔹 Tension = {test_V_pression*1000:.0f} mV → Pression = {p_calc:.1f} mmHg")

test_V_force1 = 0.3
poids_calc1 = poids_from_tension(test_V_force1, 10000)
print(f"🔹 Tension = {test_V_force1} V (Gain=10000) → Poids = {poids_calc1:.1f} g")

test_V_force2 = 3.4
poids_calc2 = poids_from_tension(test_V_force2, 1000)
print(f"🔹 Tension = {test_V_force2} V (Gain=1000) → Poids = {poids_calc2:.1f} g")

# ============================================================
# 5. VISUALISATION
# ============================================================

print("\n📊 Génération des graphiques...")

plt.figure(figsize=(15, 10))

# Capteur pression
plt.subplot(2, 2, 1)
plt.scatter(tension_mV, pression_mmHg, color='red', s=50, label='Mesures')
tension_fine = np.linspace(min(tension_V), max(tension_V), 100)
plt.plot(tension_fine * 1000, a * tension_fine + b, 'b-', label='Régression', linewidth=2)
plt.xlabel('Tension (mV)')
plt.ylabel('Pression (mmHg)')
plt.title('Capteur de pression - Étalonnage')
plt.grid(True, alpha=0.3)
plt.legend()

# Résidus pression
plt.subplot(2, 2, 2)
residus = pression_mmHg - pression_pred
plt.stem(tension_mV, residus, linefmt='r-', markerfmt='ro', basefmt='k-')
plt.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
plt.xlabel('Tension (mV)')
plt.ylabel('Erreur (mmHg)')
plt.title(f'Résidus - Capteur pression (MAE = {mae:.2f} mmHg)')
plt.grid(True, alpha=0.3)

# Capteur force
plt.subplot(2, 2, 3)
plt.scatter(tension1, poids1, color='blue', s=50, label='Gain=10000')
plt.scatter(tension2, poids2, color='green', s=50, label='Gain=1000')
plt.plot(tension_fine[:50], a1 * tension_fine[:50] + b1, 'b--', alpha=0.7, linewidth=2)
plt.plot(tension_fine[50:], a2 * tension_fine[50:] + b2, 'g--', alpha=0.7, linewidth=2)
plt.xlabel('Tension (V)')
plt.ylabel('Poids (g)')
plt.title('Capteur de force - Deux gammes')
plt.grid(True, alpha=0.3)
plt.legend()

# Comparaison régression vs interpolation
plt.subplot(2, 2, 4)
plt.scatter(tension_mV, pression_mmHg, color='red', s=50, label='Mesures')
plt.plot(tension_fine * 1000, a * tension_fine + b, 'b-', label='Régression', linewidth=2)
f_interp = interpolate.interp1d(tension_V, pression_mmHg, kind='linear')
plt.plot(tension_fine * 1000, f_interp(tension_fine), 'g--', label='Interpolation', linewidth=2)
plt.xlabel('Tension (mV)')
plt.ylabel('Pression (mmHg)')
plt.title('Régression vs Interpolation')
plt.grid(True, alpha=0.3)
plt.legend()

plt.tight_layout()

# Sauvegarde
figures_dir = os.path.join(project_root, 'figures')
os.makedirs(figures_dir, exist_ok=True)
plt.savefig(os.path.join(figures_dir, 'etalonnage_capteurs.png'), dpi=150)
print(f"✅ Graphiques sauvegardés dans {figures_dir}/")

plt.show()

print("\n" + "="*60)
print("✅ ANALYSE TERMINÉE AVEC SUCCÈS")
print("="*60)