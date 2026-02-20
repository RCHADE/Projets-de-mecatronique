#include <mcp_can.h>
#include <SPI.h>

MCP_CAN CAN(10);

void setup() {
  Serial.begin(115200);
  
  if(CAN.begin(CAN_500KBPS) == CAN_OK) {
    Serial.println("CAN Connexion réussie");
  } else {
    Serial.println("CAN Échec de la connexion");
  }
}

void loop() {
  unsigned char len = 0;
  unsigned char buf[8];
  
  if(CAN_MSGAVAIL == CAN.checkReceive()) {
    CAN.readMsgBuf(&len, buf);
    unsigned long canId = CAN.getCanId();
    
    if(canId == 0x360) {
      int rpm = (buf[0] << 8) | buf[1];
      Serial.print("REGIME:");
      Serial.print(rpm);
      Serial.println(";");
    }
    
    else if(canId == 0x1A0) {
      int vitesse = buf[0];
      Serial.print("VITESSE:");
      Serial.print(vitesse);
      Serial.println(";");
    }
    
    else if(canId == 0x420) {
      int temp = buf[0];
      Serial.print("TEMP:");
      Serial.print(temp);
      Serial.println(";");
    }
    
    else if(canId == 0x430) {
      int carburant = buf[0];
      Serial.print("CARBURANT:");
      Serial.print(carburant);
      Serial.println(";");
    }
    
    else if(canId == 0x370) {
      int acceleration = buf[0];
      Serial.print("ACCELERATION:");
      Serial.print(acceleration);
      Serial.println(";");
    }
    
    else if(canId == 0x440) {
      int charge = buf[0];
      Serial.print("CHARGE:");
      Serial.print(charge);
      Serial.println(";");
    }
  }
}