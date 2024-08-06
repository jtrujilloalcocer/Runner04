import cv2
from datetime import datetime
from PIL import Image
import numpy as np
import json
import logging
import os
from pathlib import Path
from vimba import *
import json
import logging
from pathlib import Path
from vimba import Vimba, Camera, PersistType

#Class to process the images
class CameraModule:
    # Constructor
    def __init__(self):
        # Logger configuration for the camera module
        logging.basicConfig(filename='logs/camera.log', 
                            level=logging.INFO, 
                            format='%(asctime)s:%(levelname)s:%(message)s')
                   
        config_path = Path('camera/config.json') # Path to the configuration file
        if not config_path.exists(): # Check if the configuration file exists
            logging.error("config.json file not found.") # Log an error message
            raise FileNotFoundError("config.json file not found.") # Raise an exception

        with open(config_path, 'r') as config_file: # Open the configuration file
            self.config = json.load(config_file) # Load the configuration file
        self.vimba = Vimba.get_instance() # Get the Vimba instance
        self.cameras = self.config.get("cameras", {}) # Get the camera configurations 
        self.parameters = self.config.get("parameters", {}) # Get the camera parameters

        if not self.cameras: # Check if there are camera configurations
            logging.error("No camera configurations found in config.json.") # Log an error message
            raise ValueError("No camera configurations found in config.json.")# Raise an exception

        with Vimba.get_instance() as vimba: # Open the Vimba instance  
            self.vimba = Vimba.get_instance() # Get the Vimba instance
            self.available_cameras = self.vimba.get_all_cameras() # Get all the available cameras
            if not self.available_cameras: # Check if there are available cameras
                logging.error("No cameras found.") # Log an error message
                raise RuntimeError("No cameras found.") # Raise an exception
            
        self.available_camera_ids = [camera.get_id() for camera in self.available_cameras] # Get the IDs of the available cameras
        logging.info(f"Available cameras: {self.available_camera_ids}") # Log a message with the available cameras

    # Function to apply the camera settings
    def apply_settings(self):
        for name, camera_id in self.cameras.items(): # Iterate over the camera configurations
            if camera_id in self.available_camera_ids: # Check if the camera is available
                config_file = self.parameters.get(name) # Get the configuration file
                if config_file: # Check if the configuration file exists
                    self.load_settings(camera_id, config_file) # Load the camera settings
                else:
                    logging.warning(f"No settings file found for camera {name} with ID {camera_id}") # Log a warning message
            else:
                logging.warning(f"Camera {name} with ID {camera_id} is not available") # Log a warning message
                
    # Function to load the camera settings from a configuration file
    def load_settings(self, cam_id, path_config):
        base_path = Path(__file__).parent # Get the base path of the file
        config_file_path = base_path / path_config # Create the path to the configuration file
        if not config_file_path.exists(): # Check if the configuration file exists
            logging.error(f"Configuration file {path_config} not found.") # Log an error message 
            raise FileNotFoundError(f"Configuration file {path_config} not found.") # Raise an exception
        with Vimba.get_instance() as vimba: # Open the Vimba instance
            with vimba.get_camera_by_id(cam_id) as cam: # Get the camera by ID
                try:
                    cam.load_settings(str(config_file_path), PersistType.All) # Load the camera settings
                    logging.info(f"Settings loaded for camera {cam_id} from '{path_config}'") # Log a message
                except Exception as e: # Catch any exceptions
                    logging.error(f"Failed to load settings for camera {cam_id}: {e}") # Log an error message
                    
    # Function to capture an image from a camera
    def capture_image(self, camera_name):
        try:
            camera_id = self.config['cameras'].get(camera_name) # Get the camera ID
            if camera_id is None: # Check if the camera ID is not found
                logging.error(f"No se encontró la cámara con nombre: {camera_name}") # Log an error message
                return
            with self.vimba as vimba: # Open the Vimba instance
                current_dir = Path(os.path.dirname(os.path.abspath(__file__))) # Get the current directory
                save_dir = current_dir /'images'/'nuts_sv'/'input' # Create a directory to save the images
                save_dir.mkdir(parents=True, exist_ok=True) # Create the directory
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f") # Get the current timestamp
                save_path = save_dir / f"image_{timestamp}.png" # Create the path to save the image
                cam = vimba.get_camera_by_id(camera_id) # Get the camera by ID
                cam._open() # Open the camera
                frame = cam.get_frame(timeout_ms=1000) # Get a frame from the camera
                image = frame.as_opencv_image() # Convert the frame to an OpenCV image
                cv2.imwrite(str(save_path), image) # Save the image
                logging.info(f"Image captured and saved to '{save_path}' from camera {camera_name}") # Log a message
        except Exception as e: # Catch any exceptions
            logging.error(f"Failed to capture image from camera {camera_name}: {e}") # Log an error message 
        #finally:
            #cam._disconnected()      

if __name__ == "__main__":
    processor = CameraModule() # Create an instance of the ImageProcessor class
    processor.apply_settings() # Apply the camera settings
    processor.capture_image("nuts_sv") # Capture an image from the camera with the name "nuts_sv"
