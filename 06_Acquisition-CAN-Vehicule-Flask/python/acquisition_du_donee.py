import serial
import time
import json

ser = serial.Serial('COM3', 115200)
time.sleep(2)

vehicle_data = {
    "REGIME": 0,
    "VITESSE": 0,
    "TEMP": 0,
    "CARBURANT": 0,
    "ACCELERATION": 0,
    "CHARGE": 0
}

def read_serial():
    while True:
        if ser.in_waiting:
            line = ser.readline().decode().strip()
            if line and ':' in line:
                line = line.replace(';', '')
                label, value = line.split(':')
                if label in vehicle_data:
                    vehicle_data[label] = int(value)
                    print(f"{label}: {value}")
        time.sleep(0.01)

if __name__ == "__main__":
    read_serial()