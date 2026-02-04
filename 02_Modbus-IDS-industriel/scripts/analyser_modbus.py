#!/usr/bin/env python3

import struct

def analyser_paquet(données):
    if len(données) < 8:
        print("Paquet trop court")
        return
    
    id_trans, id_proto, longueur, id_unite = struct.unpack(">HHHB", données[0:7])
    code_fonction = données[7]
    
    print(f"Transaction: {id_trans}, Unité: {id_unite}")
    print(f"Fonction: 0x{code_fonction:02x}")
    
    noms_fonctions = {
        0x01: "Lire Bobines",
        0x02: "Lire Entrées Discrètes",
        0x03: "Lire Registres",
        0x04: "Lire Entrées Analogiques",
        0x05: "Écrire Bobine",
        0x06: "Écrire Registre",
        0x0F: "Écrire Bobines Multiples",
        0x10: "Écrire Registres Multiples",
        0x2B: "Identification Appareil"
    }
    
    nom = noms_fonctions.get(code_fonction, "Inconnue")
    print(f"Opération: {nom}")
    
    if code_fonction in [0x01, 0x02, 0x03, 0x04]:
        if len(données) >= 12:
            adresse, quantité = struct.unpack(">HH", données[8:12])
            print(f"Adresse: 0x{adresse:04x}, Quantité: {quantité}")
            
            if quantité > 100:
                print("ALERTE: Lecture excessive!")
    
    elif code_fonction in [0x05, 0x06]:
        if len(données) >= 12:
            adresse, valeur = struct.unpack(">HH", données[8:12])
            print(f"Adresse: 0x{adresse:04x}, Valeur: {valeur}")
            
            if adresse >= 0x1100 and adresse <= 0x11FF:
                print("ALERTE: Adresse critique!")
    
    elif code_fonction == 0x10:
        if len(données) >= 13:
            adresse, quantité = struct.unpack(">HH", données[8:12])
            octets = données[12]
            print(f"Adresse: 0x{adresse:04x}, Quantité: {quantité}, Octets: {octets}")
            
            if quantité > 50:
                print("ALERTE: Écriture massive!")
    
    print("-" * 30)

def lire_fichier(nom_fichier):
    with open(nom_fichier, "rb") as f:
        contenu = f.read()
    
    index = 0
    numéro = 1
    
    while index < len(contenu):
        if index + 12 <= len(contenu):
            paquet = contenu[index:index+12]
            print(f"\nPaquet {numéro}:")
            analyser_paquet(paquet)
            numéro += 1
            index += 12
        else:
            break

def main():
    print("Analyseur Modbus")
    print("-" * 40)
    
    try:
        lire_fichier("trafic_normal.bin")
        lire_fichier("trafic_suspect.bin")
    except FileNotFoundError:
        print("Exécutez d'abord générer_trafic.py")

if __name__ == "__main__":
    main()