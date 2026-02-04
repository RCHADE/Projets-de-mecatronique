#include <iostream>


struct CarMessage {
    int message_id;
    unsigned char data[8];
    int data_length;
};

class SimpleCarGuard {
public:
    // Verifie si le message est du diagnostique ou pas et son type de service ..ect
    void checkMessage(CarMessage msg) {
        
       
        if (msg.message_id != 0x7DF) {
            return; 
        }
        
        if (msg.data_length < 2) {
            return;
        }
        
        unsigned char service_type = msg.data[1];
        
        
        std::cout << "\na trouver des cmd diagnostique: ";
        
        
        if (service_type == 0x2E) {
            // Quelqu'un essaie d'écrire dans la mémoire de la voiture.
            std::cout << "    DANGER : Ceci pourrait reprogrammer la voiture " << std::endl;
            std::cout << "   Ce cmd a ete blocke " << std::endl;
        }
        else if (service_type == 0x2F) {
            // Quelqu'un essaie de contrôler les freins ou la direction
            std::cout << " DANGER : Ceci pourrait contrôler les freins ou la direction " << std::endl;
            std::cout << "  Ce cmd a ete blocke" << std::endl;
        }
        else if (service_type == 0x31) {
            // Quelqu'un essaie de contrôler le moteur
            std::cout << "    AVERTISSEMENT : Ceci pourrait démarrer ou arrêter le moteur " << std::endl;
            std::cout << "   Ce cmd a ete blocke " << std::endl;
        }
        else if (service_type == 0x01) {
            std::cout << "Lire le data du sensor" << std::endl;
            std::cout << " sûr " << std::endl;
        }
        else if (service_type == 0x03) {
            std::cout << "READ ERROR CODES" << std::endl;
            std::cout << " sûr " << std::endl;
        }
        else {
            // cmd inconus
            std::cout << "cmd inconus (service 0x" << std::hex << (int)service_type << ")" << std::dec << std::endl;
        }
    }
    
    
};

int main() {

    SimpleCarGuard car_security;

    return 0;
}