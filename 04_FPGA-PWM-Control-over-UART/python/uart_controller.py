import serial
import time
import sys

class FPGA_PWM_Controller:
    def __init__(self, port='COM3', baud=115200):
        try:
            self.ser = serial.Serial(port, baud, timeout=1)
            time.sleep(2)
            print(f"Connected to {port}")
        except:
            print(f"Error opening {port}")
            sys.exit(1)
    
    def set_duty(self, percent):
        if 0 <= percent <= 100:
            cmd = f"b{percent}\n"
            self.ser.write(cmd.encode())
            print(f"Set duty to {percent}%")
        else:
            print("Invalid percent")
    
    def reset(self):
        self.ser.write(b"r\n")
        print("Reset")
    
    def close(self):
        self.ser.close()
        print("Closed")

if __name__ == "__main__":
    fpga = FPGA_PWM_Controller('COM3')
    
    try:
        fpga.reset()
        time.sleep(1)
        
        for duty in [20, 50, 80, 100, 50]:
            fpga.set_duty(duty)
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("Stopped")
    finally:
        fpga.close()