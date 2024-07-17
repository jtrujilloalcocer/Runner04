import json
import snap7
from snap7.util import *
from snap7.type import *
import logging

# Configurar el nivel de logging
logging.basicConfig(level=logging.DEBUG)

class PLCConnection:
    def __init__(self, config_path='plc_control/config.json'):
        # Initialize the class with the path to the configuration file
        self.config_path = config_path
        self.load_config()
        self.client = snap7.client.Client()

    def load_config(self):
        # Load the configuration from a JSON file
        try:
            with open(self.config_path) as f:
                self.config = json.load(f)
                self.ip = self.config['plc']['ip']
                self.rack = self.config['plc']['rack']
                self.slot = self.config['plc']['slot']
                logging.debug(f"Loaded configuration: {self.config}")
        except Exception as e:
            logging.error(f"Error loading configuration: {e}")
            raise

    def connect(self):
        # Connect to the PLC
        try:
            self.client.connect(self.ip, self.rack, self.slot)
            if not self.client.get_connected():
                raise snap7.snap7exceptions.Snap7Exception('Connection failed')
            logging.debug("Connected to PLC")
        except Exception as e:
            logging.error(f"Error connecting to PLC: {e}")
            raise

    def disconnect(self):
        # Disconnect from the PLC
        try:
            self.client.disconnect()
            if self.client.get_connected():
                raise snap7.snap7exceptions.Snap7Exception('Disconnection failed')
            logging.debug("Disconnected from PLC")
        except Exception as e:
            logging.error(f"Error disconnecting from PLC: {e}")
            raise

    def get_status(self):
        # Get the status of the PLC
        try:
            status = self.client.get_cpu_state()
            logging.debug(f"PLC status: {status}")
            return status
        except Exception as e:
            logging.error(f"Error getting PLC status: {e}")
            return 'S7CpuStatusUnknown'  
    
if __name__ == "__main__":
    try:
        plc = PLCConnection()
        plc.connect()
        status = plc.get_status()
        print(status)
        plc.disconnect()
    except Exception as e:
        logging.error(f"An error occurred: {e}")