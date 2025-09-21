import serial
import re
import json

class DataReader:
    def __init__(self,port = "COM4",baudrate=115200,timeout=1):
        try:
            self.ser = serial.Serial(port = port, baudrate = baudrate,timeout =1)
        except Exception as s:
            print("Could not open serial port",s)
            #Marking as failed
            self.ser = None
    
    def read_line(self):
        if not self.ser:
            return None

        while True:
                try:
                    line = self.ser.readline().decode("utf-8").strip()
                    if line:
                        cleaned = line.replace(";",",")
                        if(cleaned[0]=="["):
                            final_data = json.loads(cleaned)
                            print(cleaned)

                except Exception as e:
                    print("Parse error:",line,e)
     

    def close(self):
        if self.ser:
            self.ser.close()

reader = DataReader()
reader.read_line();  



