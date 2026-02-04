#include "DHT20.h"

int buzzer = D12;
int frequency = 2700; 
int cycle = 1000000/frequency;
int LED = D11;
int statu = 0;
const int BUTTON_PIN = A7;
int mode = 0;


bool silencer_alarme = false;
DHT20 DHT;
unsigned long lastButtonPress = 0; 
unsigned long dernieure_lecture = 0;

const int intervalle_entre_deux_lectur = 1000;

void setup() {
  
  Serial.begin(9600);
  pinMode(buzzer,OUTPUT);
  pinMode(LED, OUTPUT);
  pinMode(BUTTON_PIN, INPUT);
  Wire.begin();
  DHT.begin();



}

void loop() {


  if (millis() - dernieure_lecture >= intervalle_entre_deux_lectur) {
    dernieure_lecture = millis();

  int etat = DHT.read();
  float temperature = DHT.getTemperature();
  float Himidity  = DHT.getHumidity();
  int buttonState = digitalRead(BUTTON_PIN);

  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
  command.trim();
  
  if (command == "SILENCE") {
    silencer_alarme = true;
    Serial.println("mode=SILENCED,T=0,H=0,alarm=0");
  } else if (command == "RESUME") {
    silencer_alarme = false;
    Serial.println("mode=RESUMED,T=0,H=0,alarm=0");
  } else if (command == "START") {
    Serial.println("mode=STARTED,T=0,H=0,alarm=0");
  }
}
  
  Serial.print("mode=");
  if (mode == 0) {
    Serial.print("IDLE");
  }else if (mode == 1) {
    Serial.print("MONITERING");
  } else if ( mode == 2) {
    Serial.print("ALARM");
  }
  Serial.print(",");
  Serial.print("T = ");
  Serial.print(temperature, 3);
  Serial.print(",");
  Serial.print(" H= ");
  Serial.print(Himidity, 3);
  Serial.print(", alarm =");
  Serial.print(statu);
  Serial.print('\n');



  

  if (buttonState == LOW) {  
  if (millis() - lastButtonPress > 100) {
    lastButtonPress = millis();
    silencer_alarme = !silencer_alarme;
    
  }
}


if (temperature > 27) {
    if (silencer_alarme) {
        statu = 0; 
        mode = 2;
    } else {
        statu = 1;
        mode = 2;
    }
} else {
    silencer_alarme = false; 
    statu = 0;
    mode = 1;
}
  
  }
  if (statu == 1) {
  static unsigned long lastChange = 0;
  static int alarmStep = 0;
  
  if (millis() - lastChange > 500) {
    lastChange = millis();
    
    switch (alarmStep) {
      case 0:
        digitalWrite(LED, HIGH);
        tone(buzzer, 1500);
        break;
      case 1:
        digitalWrite(LED, HIGH);
        tone(buzzer, 800);
        break;
      case 2:
        digitalWrite(LED, LOW);
        noTone(buzzer);
        break;
      case 3:
        digitalWrite(LED, HIGH);
        tone(buzzer, 1500);
        break;
      case 4:
        digitalWrite(LED, LOW);
        noTone(buzzer);
        break;
      case 5:
        digitalWrite(LED, LOW);
        noTone(buzzer);
        break;
    }
    alarmStep++;
    if (alarmStep > 5) alarmStep = 0;
    
  }
} else {
  digitalWrite(LED, LOW);
  noTone(buzzer);
}

  
}
