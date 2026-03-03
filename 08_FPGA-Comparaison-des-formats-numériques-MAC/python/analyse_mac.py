#!/usr/bin/env python3
"""
Comparaison des formats numériques pour MAC sur FPGA
Analyse les résultats des implémentations INT8, Fixed16 et Float16
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import os

Path("../resultats/graphiques").mkdir(parents=True, exist_ok=True)

def analyse_int8(fichier_csv):
    """Analyse des résultats INT8"""
    try:
        df = pd.read_csv(fichier_csv)
        print("\n" + "="*50)
        print("Analyse INT8")
        print("="*50)
        print(f"Total tests: {len(df)}")
        
        if 'error' in df.columns:
            erreurs = df[df['error'] == 1]
            print(f"Erreurs: {len(erreurs)} ({len(erreurs)/len(df)*100:.2f}%)")
            
            if 'expected' in df.columns and 'actual' in df.columns:
                mse = np.mean((df['expected'] - df['actual'])**2)
                print(f"MSE: {mse:.4f}")
        
        return df
    except Exception as e:
        print(f"Erreur lecture {fichier_csv}: {e}")
        return None

def analyse_fixed16(fichier_csv):
    """Analyse des résultats Fixed16"""
    try:
        df = pd.read_csv(fichier_csv)
        print("\n" + "="*50)
        print("Analyse Fixed16")
        print("="*50)
        print(f"Total tests: {len(df)}")
        
        if 'error_percent' in df.columns:
            df['error_percent'] = pd.to_numeric(df['error_percent'], errors='coerce')
            erreur_moyenne = df['error_percent'].mean()
            erreur_max = df['error_percent'].max()
            print(f"Erreur moyenne: {erreur_moyenne:.4f}%")
            print(f"Erreur max: {erreur_max:.4f}%")
            
            plt.figure(figsize=(10, 6))
            plt.hist(df['error_percent'].dropna(), bins=30, edgecolor='black')
            plt.title('Distribution des erreurs - Fixed16')
            plt.xlabel('Erreur (%)')
            plt.ylabel('Fréquence')
            plt.grid(True, alpha=0.3)
            plt.savefig('../resultats/graphiques/fixed16_distribution_erreurs.png', dpi=100)
            plt.close()
        
        return df
    except Exception as e:
        print(f"Erreur lecture {fichier_csv}: {e}")
        return None

def analyse_float16(fichier_csv):
    """Analyse des résultats Float16"""
    try:
        df = pd.read_csv(fichier_csv)
        print("\n" + "="*50)
        print("Analyse Float16")
        print("="*50)
        print(f"Total tests: {len(df)}")
        return df
    except Exception as e:
        print(f"Erreur lecture {fichier_csv}: {e}")
        return None

def genere_vecteurs_test():
    """Génération des vecteurs de test"""
    print("\nGénération des vecteurs de test...")
    
    int8_tests = []
    for i in range(50):
        a = np.random.randint(-128, 127)
        b = np.random.randint(-128, 127)
        c = np.random.randint(-128, 127)
        expected = a * b + c
        int8_tests.append([a, b, c, expected])
    
    int8_df = pd.DataFrame(int8_tests, columns=['a', 'b', 'c', 'expected'])
    int8_df.to_csv('../resultats/int8_vecteurs_test.csv', index=False)
    print(f"Généré {len(int8_tests)} vecteurs INT8")
    
    fixed16_tests = []
    for i in range(50):
        a = np.random.uniform(-10, 10)
        b = np.random.uniform(-10, 10)
        c = np.random.uniform(-10, 10)
        expected = a * b + c
        fixed16_tests.append([a, b, c, expected])
    
    fixed16_df = pd.DataFrame(fixed16_tests, columns=['a', 'b', 'c', 'expected'])
    fixed16_df.to_csv('../resultats/fixed16_vecteurs_test.csv', index=False)
    print(f"Généré {len(fixed16_tests)} vecteurs Fixed16")

def genere_rapport_comparaison():
    """Génération du rapport de comparaison"""
    print("\n" + "="*50)
    print("RAPPORT DE COMPARAISON")
    print("="*50)
    
    donnees = {
        'Format': ['INT8', 'Fixed16 (Q8.8)', 'Float16'],
        'Bits': [8, 16, 16],
        'Plage': ['-128 à 127', '-128 à 128', '~65k'],
        'Précision': ['1.0', '0.0039', 'Variable'],
        'DSPs': ['0-1', '1-2', '3+'],
        'LUTs': ['Très faible', 'Faible', 'Élevée'],
        'Latence': ['3 cycles', '3 cycles', '4-6 cycles'],
        'Usage idéal': ['Grands nombres,\nhaut débit', 'Équilibre\nprécision/efficacité', 'Grande dynamique,\ncalculs scientifiques']
    }
    
    df = pd.DataFrame(donnees)
    print("\n", df.to_string(index=False))
    
    df.to_csv('../resultats/comparaison_formats.csv', index=False)
    print("\nComparaison sauvegardée dans ../resultats/comparaison_formats.csv")
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    formats = ['INT8', 'Fixed16', 'Float16']
    luts = [50, 200, 800]
    dsps = [0, 1, 3]
    
    ax1.bar(formats, luts, color='skyblue', edgecolor='black')
    ax1.set_title('Utilisation des ressources (LUTs)')
    ax1.set_ylabel('Estimation LUTs')
    ax1.grid(True, alpha=0.3)
    
    ax2.bar(formats, dsps, color='lightcoral', edgecolor='black')
    ax2.set_title('Utilisation des ressources (DSPs)')
    ax2.set_ylabel('Estimation DSPs')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('../resultats/graphiques/comparaison_ressources.png', dpi=100)
    plt.close()
    
    print("Graphique sauvegardé")

def main():
    print("Analyse des formats numériques pour MAC sur FPGA")
    print("="*50)
    
    genere_vecteurs_test()
    
    dossier_resultats = Path("../resultats")
    
    int8_file = dossier_resultats / "int8_resultats.csv"
    if int8_file.exists():
        analyse_int8(int8_file)
    
    fixed16_file = dossier_resultats / "fixed16_resultats.csv"
    if fixed16_file.exists():
        analyse_fixed16(fixed16_file)
    
    float16_file = dossier_resultats / "float16_resultats.csv"
    if float16_file.exists():
        analyse_float16(float16_file)
    
    genere_rapport_comparaison()
    
    print("\n✅ Analyse terminée!")
    print("Vérifiez les fichiers dans ../resultats/ et ../resultats/graphiques/")

if __name__ == "__main__":
    main()