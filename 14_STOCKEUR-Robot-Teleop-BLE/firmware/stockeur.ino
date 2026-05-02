#include "MeMegaPi.h"
#include "Wire.h"

// IHM MODE — 0 = PILOT  1 = MANU
int ihmMode = 0;

// ═══════════════════════════════════════════════════════════
// MOTORS & SENSORS
// ═══════════════════════════════════════════════════════════
MeMegaPiDCMotor    motorRight  (PORT1B);
MeMegaPiDCMotor    motorLeft   (PORT2B);
MeMegaPiDCMotor    grabberArm  (PORT3B);
MeMegaPiDCMotor    grabberClamp(PORT4B);
MeLineFollower     lineSensor  (PORT_6);
MeUltrasonicSensor sonar       (PORT_5);
MeColorSensor      colorSensor (PORT_8);

const int   BASE_SPEED        = 50;
const float OBSTACLE_CM       = 3;
const int   BASE_SPEED_NORMAL = 50;
const int   BASE_SPEED_SLOW   = 25;
const int   ARM_SPEED         = 100;
const int   CLAMP_SPEED       = 150;
bool slowMode = false;

// ═══════════════════════════════════════════════════════════
// ENCODERS
// ═══════════════════════════════════════════════════════════
const byte ENC1_INT = 18; const byte ENC1_DIR = 31;
const byte ENC2_INT = 19; const byte ENC2_DIR = 38;

volatile long pulses1 = 0;
volatile long pulses2 = 0;

void isr1() { if (digitalRead(ENC1_DIR) > 0) pulses1++; else pulses1--; }
void isr2() { if (digitalRead(ENC2_DIR) > 0) pulses2++; else pulses2--; }

float getRotation1() { return abs(pulses1) * (360.0 / 414.0); }
float getRotation2() { return abs(pulses2) * (360.0 / 414.0); }
void  resetEncoders() { pulses1 = 0; pulses2 = 0; }

// ═══════════════════════════════════════════════════════════
// SPEED
// ═══════════════════════════════════════════════════════════
const float MM_PER_PULSE = (2.0 * 3.14159 * 35.0) / 414.0;
long lastPulses1 = 0;
long lastPulses2 = 0;
unsigned long lastSpeedTime = 0;
float speedAvg = 0.0;

// ═══════════════════════════════════════════════════════════
// SENSOR CACHE
// ═══════════════════════════════════════════════════════════
int     g_line  = 3;
float   g_dist  = 0.0;
uint8_t g_color = 0;

// ═══════════════════════════════════════════════════════════
// PILOT STATE
// ═══════════════════════════════════════════════════════════
bool isFollowing  = false;
bool pilotStopped = true;
int  lastTurnDir  = 0;

String colorName(uint8_t c) {
  switch(c) {
    case BLACK:  return "BLACK";
    case WHITE:  return "WHITE";
    case RED:    return "RED";
    case YELLOW: return "YELLOW";
    case GREEN:  return "GREEN";
    case BLUE:   return "BLUE";
    default:     return "UNKNOWN";
  }
}

void readAllSensors() {
  int L = lineSensor.readSensor1();
  int R = lineSensor.readSensor2();
  if      (L == 0 && R == 0) g_line = 0;
  else if (L == 0 && R == 1) g_line = 1;
  else if (L == 1 && R == 0) g_line = 2;
  else                        g_line = 3;

  static unsigned long lastSonar = 0;
  unsigned long now = millis();
  if (now - lastSonar >= 100) {
    g_dist = sonar.distanceCm();
    lastSonar = now;
  }

  static unsigned long lastColor = 0;
  if (now - lastColor >= 5000) {
    g_color = colorSensor.ColorIdentify();
    lastColor = now;
  }
}

bool obstacleDetected() { return (g_dist > 2.0 && g_dist < OBSTACLE_CM); }

// ═══════════════════════════════════════════════════════════
// MOVEMENT
// ═══════════════════════════════════════════════════════════
void goForward() {
  int spd = slowMode ? BASE_SPEED_SLOW : BASE_SPEED_NORMAL;
  motorRight.run(-spd); motorLeft.run(spd);
}
void goBackward() {
  int spd = slowMode ? BASE_SPEED_SLOW : BASE_SPEED_NORMAL;
  motorRight.run(spd); motorLeft.run(-spd);
}
void turnLeft()   { motorRight.run(-60); motorLeft.run(-60); }
void turnRight()  { motorRight.run( 60); motorLeft.run( 60); }
void stopMotors() { motorRight.stop();   motorLeft.stop(); }

void armUp()      { grabberArm.run(-ARM_SPEED); }
void armDown()    { grabberArm.run( ARM_SPEED); }
void armStop()    { grabberArm.stop(); }
void clampOpen()  { grabberClamp.run(-CLAMP_SPEED); }
void clampClose() { grabberClamp.run( CLAMP_SPEED); }
void clampStop()  { grabberClamp.stop(); }

// ═══════════════════════════════════════════════════════════
// DATA STREAMING
// ═══════════════════════════════════════════════════════════
unsigned long lastDataSend = 0;

void streamData() {
  unsigned long now = millis();
  if (now - lastDataSend < 200) return;

  unsigned long dt = now - lastSpeedTime;
  if (dt > 0) {
    long delta1 = abs(pulses1) - lastPulses1;
    long delta2 = abs(pulses2) - lastPulses2;
    speedAvg      = ((delta1 + delta2) / 2.0 * MM_PER_PULSE) / (dt / 1000.0);
    lastPulses1   = abs(pulses1);
    lastPulses2   = abs(pulses2);
    lastSpeedTime = now;
  }
  lastDataSend = now;

  String msg = "DATA:";
  msg += "line="  + String(g_line);
  msg += ",color=" + colorName(g_color);
  msg += ",dist="  + String(g_dist, 1);
  msg += ",deg1="  + String(getRotation1(), 1);
  msg += ",deg2="  + String(getRotation2(), 1);
  msg += ",obs="   + String(obstacleDetected() ? "1" : "0");
  msg += ",mode="  + String(ihmMode);
  msg += ",spd="   + String(speedAvg, 1);

  Serial.println(msg);
  Serial3.println(msg);
}

// ═══════════════════════════════════════════════════════════
// COMMAND PROCESSING
// ═══════════════════════════════════════════════════════════
void processCommand(String input) {
  if (input == "P") {
    ihmMode = 0; isFollowing = false; pilotStopped = false;
    stopMotors(); armStop(); clampStop();
    Serial.println("LOG:Mode PILOT actif");
    Serial3.println("LOG:Mode PILOT actif");
  }
  else if (input == "N") {
    ihmMode = 1; isFollowing = false; pilotStopped = false;
    stopMotors(); armStop(); clampStop();
    Serial.println("LOG:Mode MANU actif");
    Serial3.println("LOG:Mode MANU actif");
  }
  else if (input == "Z") {
    resetEncoders();
    Serial.println("LOG:Encodeurs remis à zéro");
    Serial3.println("LOG:Encodeurs remis à zéro");
  }
  else if (input == "W") {
    slowMode = true;
    Serial.println("LOG:Mode lent");
    Serial3.println("LOG:Mode lent");
  }
  else if (input == "K") {
    slowMode = false;
    Serial.println("LOG:Mode normal");
    Serial3.println("LOG:Mode normal");
  }
  else if (ihmMode == 0) {
    if (input == "G") {
      pilotStopped = false;
      Serial.println("LOG:GO");
      Serial3.println("LOG:GO");
    }
    else if (input == "S") {
      pilotStopped = true; isFollowing = false;
      stopMotors();
      Serial.println("LOG:STOP");
      Serial3.println("LOG:STOP");
    }
  }
  else if (ihmMode == 1) {
    if      (input == "F") { goForward();  Serial.println("LOG:AVANT");        Serial3.println("LOG:AVANT");        }
    else if (input == "B") { goBackward(); Serial.println("LOG:ARRIÈRE");      Serial3.println("LOG:ARRIÈRE");      }
    else if (input == "L") { turnLeft();   Serial.println("LOG:GAUCHE");       Serial3.println("LOG:GAUCHE");       }
    else if (input == "R") { turnRight();  Serial.println("LOG:DROITE");       Serial3.println("LOG:DROITE");       }
    else if (input == "S") { stopMotors(); Serial.println("LOG:STOP roues");   Serial3.println("LOG:STOP roues");   }
    else if (input == "U") { armDown();    Serial.println("LOG:BRAS bas");     Serial3.println("LOG:BRAS bas");     }
    else if (input == "D") { armUp();      Serial.println("LOG:BRAS haut");    Serial3.println("LOG:BRAS haut");    }
    else if (input == "X") { armStop();    Serial.println("LOG:BRAS stop");    Serial3.println("LOG:BRAS stop");    }
    else if (input == "O") { clampOpen();  Serial.println("LOG:PINCE ouvre");  Serial3.println("LOG:PINCE ouvre");  }
    else if (input == "C") { clampClose(); Serial.println("LOG:PINCE ferme");  Serial3.println("LOG:PINCE ferme");  }
    else if (input == "V") { clampStop();  Serial.println("LOG:PINCE stop");   Serial3.println("LOG:PINCE stop");   }
  }
}

// ═══════════════════════════════════════════════════════════
// PILOT LOGIC
// ═══════════════════════════════════════════════════════════
void runPilot() {
  if (pilotStopped) return;

  if (obstacleDetected()) {
    stopMotors();
    isFollowing  = false;
    pilotStopped = true;
    lastTurnDir  = 0;
    Serial.println("LOG:Obstacle — GO pour reprendre");
    Serial3.println("LOG:Obstacle — GO pour reprendre");
    return;
  }

  int line = g_line;

  if (!isFollowing && line != 3) {
    isFollowing = true;
    Serial.println("LOG:Ligne détectée");
    Serial3.println("LOG:Ligne détectée");
  }

  if (!isFollowing) return;

  switch (line) {
    case 0:
      goForward();
      break;
    case 1:
      turnLeft();
      lastTurnDir = 1;
      break;
    case 2:
      turnRight();
      lastTurnDir = 2;
      break;
    case 3:
      if (g_color == RED || g_color == GREEN || g_color == YELLOW) {
        stopMotors();
        isFollowing  = false;
        pilotStopped = true;
        lastTurnDir  = 0;
        Serial.println("LOG:Zone colorée — arrêt");
        Serial3.println("LOG:Zone colorée — arrêt");
      } else {
        if (lastTurnDir == 1) {
          turnLeft();
        } else if (lastTurnDir == 2) {
          turnRight();
        } else {
          stopMotors();
          isFollowing  = false;
          pilotStopped = true;
          Serial.println("LOG:Ligne perdue — arrêt");
          Serial3.println("LOG:Ligne perdue — arrêt");
        }
      }
      break;
  }
}

// ═══════════════════════════════════════════════════════════
// SETUP & LOOP
// ═══════════════════════════════════════════════════════════
void setup() {
  Serial.begin(115200);
  Serial3.begin(115200);

  pinMode(ENC1_INT, INPUT_PULLUP); pinMode(ENC1_DIR, INPUT);
  pinMode(ENC2_INT, INPUT_PULLUP); pinMode(ENC2_DIR, INPUT);
  attachInterrupt(digitalPinToInterrupt(ENC1_INT), isr1, RISING);
  attachInterrupt(digitalPinToInterrupt(ENC2_INT), isr2, RISING);

  colorSensor.SensorInit();
  stopMotors(); armStop(); clampStop();

  Serial.println("LOG:Système initialisé");
  Serial3.println("LOG:Système initialisé");
}

void loop() {
  readAllSensors();
  streamData();

  static String usbBuffer = "";
  while (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '\n') {
      usbBuffer.trim();
      processCommand(usbBuffer);
      usbBuffer = "";
    } else {
      usbBuffer += c;
    }
  }

  static String bleBuffer = "";
  while (Serial3.available() > 0) {
    char c = Serial3.read();
    if (c == '\n') {
      bleBuffer.trim();
      processCommand(bleBuffer);
      bleBuffer = "";
    } else {
      bleBuffer += c;
    }
  }

  if (ihmMode == 0) runPilot();
}
