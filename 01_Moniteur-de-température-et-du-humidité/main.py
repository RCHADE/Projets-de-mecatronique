import time
import serial
from collections import deque
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import uvicorn
import json
import threading
from fastapi.responses import FileResponse

app = FastAPI()


dernieur_100_lectur = deque(maxlen = 100)
dernieur_lecture = { 'T':0.0, 'H':0.0, 'alarm': 0}
serial_conection = None




def to_data(linge):
    
    morceaux = linge.split(',')
    parti_temperature = morceaux[1]  
    T = parti_temperature.split('=')[1].strip()  
    
    
    parti_humidite = morceaux[2] 
    H = parti_humidite.split('=')[1].strip()  

    parti_alarm = morceaux[3]  
    alarm = parti_alarm.split('=')[1].strip()
    
    return [T, H, alarm]

def read_serial( port = "COM6", baudrate = 9600):

    global dernieur_lecture, serial_conection, dernieur_100_lectur
    try:
        ser = serial.Serial(port, baudrate=baudrate, timeout=1)
        serial_conection = ser
    except serial.SerialException as e:
        print(f"Error opening serial port {port}: {e}")
        return
    
    while True:
        
        line_bytes = ser.readline()
        if not line_bytes:
            
            continue
        try:
            line = line_bytes.decode("utf-8", errors="ignore").strip()
            
            L = to_data(line)
            dernieur_lecture['T'] = float(L[0])
            dernieur_lecture['H'] = float(L[1])
            dernieur_lecture['alarm'] = int(L[2])

            dernieur_100_lectur.append({
                "timestamp": time.time(),
                "temperature": float(L[0]),
                "humidity": float(L[1]),
                "alarm": int(L[2])
                })
        except UnicodeDecodeError:
            
            continue


def comand_arduino(message):
    global serial_conection
    
    if serial_conection and serial_conection.is_open:
        try:
            serial_conection.write((message + '\n').encode())
            print(f"Sent to Arduino: {message}")
            return True
        except Exception as e:
            print(f"Error sending to Arduino: {e}")
            return False
    else:
        print("No serial connection available")
        return False
    

@app.get("/", response_class=HTMLResponse)
async def home_page():
    """Serve the HTML page"""
    return FileResponse("index.html")

@app.get("/data")
def get_data():
    return dernieur_lecture

@app.get("/current")
def get_current():
    """Get current temperature, humidity, and alarm status"""
    return dernieur_lecture

@app.post("/silence")
def silence_alarm():
    """Send SILENCE command to Arduino"""
    success = comand_arduino("SILENCE")
    return {"success": success}

if __name__ == "__main__":
    thread = threading.Thread(target=read_serial)
    thread.start()

    uvicorn.run(app, host="127.0.0.1", port=8000)