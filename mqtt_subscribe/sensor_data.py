"""
Class for sensor data
"""

class SensorDATA:

    def __init__(self):
        self.mqtt_msg = ''
        self.parsed_msg = ''
        self.temp = ''
        self.pressure = ''
        self.light = ''
    
    def parse_msg(self, data):
        self.mqtt_msg = data
        self.parsed_msg = data.split(' ')
        
        self.temp  = self.parsed_msg[0]
        self.light = self.parsed_msg[2]
    
    def get_temp(self):
        return self.temp
    
    def get_pressure(self):
        return self.pressure
    
    def get_light(self):
        return self.light
        
        
        

