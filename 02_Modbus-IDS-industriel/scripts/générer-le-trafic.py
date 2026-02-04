#!/usr/bin/env python3

import struct

def créer_paquet_modbus(id_transaction=1, id_unite=1, code_fonction=3, adresse=0x1000, quantité=1):
    entête = struct.pack(">HHHB", id_transaction, 0x0000, 0x0006, id_unite)
    pdu = struct.pack(">BHH", code_fonction, adresse, quantité)
    return entête + pdu

def main():
    print("Génération de trafic Modbus...")
    
    paquets_normaux = []
    paquets_suspects = []
    
    for i in range(5):
        lecture = créer_paquet_modbus(id_transaction=i+1, code_fonction=0x03, adresse=0x1000)
        paquets_normaux.append(lecture)
        
        écriture = créer_paquet_modbus(id_transaction=i+10, code_fonction=0x06, adresse=0x2000)
        paquets_normaux.append(écriture)
    
    fonction_inconnue = créer_paquet_modbus(id_transaction=100, code_fonction=0x99, adresse=0x1000)
    paquets_suspects.append(fonction_inconnue)
    
    adresse_critique = créer_paquet_modbus(id_transaction=101, code_fonction=0x06, adresse=0x1100)
    paquets_suspects.append(adresse_critique)
    
    écriture_masse = créer_paquet_modbus(id_transaction=102, code_fonction=0x10, adresse=0x1000, quantité=200)
    paquets_suspects.append(écriture_masse)
    
    reconnaissance = créer_paquet_modbus(id_transaction=103, code_fonction=0x2B, adresse=0x0000)
    paquets_suspects.append(reconnaissance)
    
    with open("trafic_normal.bin", "wb") as f:
        for p in paquets_normaux:
            f.write(p)
    
    with open("trafic_suspect.bin", "wb") as f:
        for p in paquets_suspects:
            f.write(p)
    
    print(f"Paquets normaux: {len(paquets_normaux)}")
    print(f"Paquets suspects: {len(paquets_suspects)}")
    print("Fichiers créés: trafic_normal.bin, trafic_suspect.bin")

if __name__ == "__main__":
    main()