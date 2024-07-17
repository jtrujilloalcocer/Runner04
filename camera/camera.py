import json
from PIL import Image
import numpy as np
from pymba import Vimba
from datetime import datetime
import logging 

class ImageProcessor:
    def __init__(self):
        # Configuration of the logger
        logging.basicConfig(filename='logs/camera.log', # Name of the log file
                            level=logging.INFO, #Level of the log
                            format='%(asctime)s:%(levelname)s:%(message)s')# Format of the log

        # Read ID of the camera from config.json
        with open('camera/config.json', 'r') as config_file:
            config = json.load(config_file)
        camera_id = config.get("cameras")["nuts"]
        if not camera_id:
            logging.error("Camera ID not found in config.json.") #Add log record 
            raise ValueError("Camera ID not found in config.json.") #Add log record

        self.system = Vimba() #Create a Vimba object
        self.system.startup() #Start the Vimba API
        camera_ids = self.system.camera_ids() #Get the IDs of the available cameras
        if camera_id not in camera_ids:
            logging.error(f"Camera ID {camera_id} not found among available cameras.") #Add log record
            raise ValueError(f"Camera ID {camera_id} not found among available cameras.") #Add log record

        self.camera = self.system.camera(camera_id) #Create a camera object
        self.camera.open() #Open the camera
        logging.info(f"Camera {camera_id} opened successfully.")  #Add log record

# Example usage
if __name__ == "__main__":
    processor = ImageProcessor()