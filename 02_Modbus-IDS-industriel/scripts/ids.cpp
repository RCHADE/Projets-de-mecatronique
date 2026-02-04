#include <iostream>
#include <vector>
#include <cstdint>

std::string nom_fonction(uint8_t code) {
    switch(code) {
        case 0x01: return "Lire Bobines";
        case 0x02: return "Lire Entrées Discrètes";
        case 0x03: return "Lire Registres";
        case 0x04: return "Lire Entrées Analogiques";
        case 0x05: return "Écrire Bobine";
        case 0x06: return "Écrire Registre";
        case 0x0F: return "Écrire Bobines Multiples";
        case 0x10: return "Écrire Registres Multiples";
        case 0x2B: return "Identification Appareil";
        default: return "Inconnue";
    }
}

bool fonction_valide(uint8_t code) {
    uint8_t codes_valides[] = {0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x0F, 0x10, 0x2B};
    for (auto c : codes_valides) {
        if (code == c) return true;
    }
    return false;
}

bool adresse_critique(uint16_t adresse) {
    return (adresse >= 0x1100 && adresse <= 0x11FF);
}

void analyser_modbus(const uint8_t* données, size_t taille) {
    if (taille < 8) return;
    
    uint16_t id_trans = (données[0] << 8) | données[1];
    uint8_t id_unite = données[6];
    uint8_t code_fonction = données[7];
    
    std::cout << "\nTransaction: " << id_trans;
    std::cout << ", Unité: " << (int)id_unite;
    std::cout << ", Fonction: 0x" << std::hex << (int)code_fonction << std::dec;
    std::cout << " (" << nom_fonction(code_fonction) << ")" << std::endl;
    
    bool alerte = false;
    std::string raison;
    
    if (!fonction_valide(code_fonction)) {
        alerte = true;
        raison = "Fonction inconnue";
    }
    
    if (code_fonction == 0x03 || code_fonction == 0x04) {
        if (taille >= 12) {
            uint16_t adresse = (données[8] << 8) | données[9];
            uint16_t quantité = (données[10] << 8) | données[11];
            
            std::cout << "Lecture: adresse 0x" << std::hex << adresse;
            std::cout << ", quantité " << std::dec << quantité << std::endl;
            
            if (quantité > 100) {
                alerte = true;
                raison = "Lecture excessive";
            }
        }
    }
    else if (code_fonction == 0x06) {
        if (taille >= 12) {
            uint16_t adresse = (données[8] << 8) | données[9];
            uint16_t valeur = (données[10] << 8) | données[11];
            
            std::cout << "Écriture: adresse 0x" << std::hex << adresse;
            std::cout << ", valeur " << std::dec << valeur << std::endl;
            
            if (adresse_critique(adresse)) {
                alerte = true;
                raison = "Adresse critique";
            }
            
            if (valeur > 10000) {
                alerte = true;
                raison = "Valeur dangereuse";
            }
        }
    }
    else if (code_fonction == 0x10) {
        if (taille >= 13) {
            uint16_t adresse = (données[8] << 8) | données[9];
            uint16_t quantité = (données[10] << 8) | données[11];
            uint8_t octets = données[12];
            
            std::cout << "Écriture multiple: adresse 0x" << std::hex << adresse;
            std::cout << ", quantité " << std::dec << quantité;
            std::cout << ", octets " << (int)octets << std::endl;
            
            if (quantité > 50) {
                alerte = true;
                raison = "Écriture massive";
            }
        }
    }
    else if (code_fonction == 0x2B) {
        alerte = true;
        raison = "Reconnaissance appareil";
    }
    
    if (alerte) {
        std::cout << "\033[1;31mALERTE: " << raison << "\033[0m" << std::endl;
    } else {
        std::cout << "\033[1;32mNormal\033[0m" << std::endl;
    }
}

std::vector<uint8_t> lire_fichier(const std::string& nom) {
    std::vector<uint8_t> données;
    FILE* fichier = fopen(nom.c_str(), "rb");
    
    if (fichier) {
        fseek(fichier, 0, SEEK_END);
        long taille = ftell(fichier);
        fseek(fichier, 0, SEEK_SET);
        
        données.resize(taille);
        fread(données.data(), 1, taille, fichier);
        fclose(fichier);
    }
    
    return données;
}

int main() {
    std::cout << "Système de Détection d'Intrusion Modbus" << std::endl;
    std::cout << "========================================" << std::endl;
    
    auto trafic_normal = lire_fichier("trafic_normal.bin");
    auto trafic_suspect = lire_fichier("trafic_suspect.bin");
    
    if (trafic_normal.empty() || trafic_suspect.empty()) {
        std::cout << "Exécutez d'abord générer_trafic.py" << std::endl;
        return 1;
    }
    
    std::cout << "\n=== Trafic Normal ===" << std::endl;
    for (size_t i = 0; i < trafic_normal.size(); i += 12) {
        if (i + 12 <= trafic_normal.size()) {
            analyser_modbus(&trafic_normal[i], 12);
        }
    }
    
    std::cout << "\n=== Trafic Suspect ===" << std::endl;
    for (size_t i = 0; i < trafic_suspect.size(); i += 12) {
        if (i + 12 <= trafic_suspect.size()) {
            analyser_modbus(&trafic_suspect[i], 12);
        }
    }
    
    return 0;
}