import json
from PIL import Image
import numpy as np
from pymba import Vimba
from datetime import datetime
import logging 
from pathlib import Path
import cv2
import vimba

class ImageProcessor:
    
    def __init__(self):
        # Logger configuration for the camera module
        logging.basicConfig(filename='logs/camera.log', 
                            level=logging.INFO, 
                            format='%(asctime)s:%(levelname)s:%(message)s')

        # Read the camera IDs from the config.json file
        with open('camera/config.json', 'r') as config_file:
            config = json.load(config_file)
        camera_ids_config = config.get("cameras")

        if not camera_ids_config:
            logging.error("No camera IDs found in config.json.") # Log the error
            raise ValueError("No camera IDs found in config.json.") # Raise an exception

        # Initialize the Vimba system
        self.system = Vimba()
        self.system.startup()
        available_camera_ids = self.system.camera_ids() # Get the available camera IDs

        # Check if the camera IDs from the config file are available
        for camera_name, camera_id in camera_ids_config.items():
            if camera_id not in available_camera_ids:
                logging.error(f"Camera ID {camera_id} for '{camera_name}' not found among available cameras.") # Log the error
            else:
                logging.info(f"Camera ID {camera_id} for '{camera_name}' is available.") # Log the info

        # Dont open the camera if it is not available
        self.camera = None

    def capture_image(self, camera_name):
        try:
            # Cargar el archivo de configuración
            config_path = Path(__file__).resolve().parent.joinpath('config.json')
            with open(config_path, 'r') as config_file:
                config = json.load(config_file)
            
            # Buscar el ID de la cámara usando el nombre
            camera_id = config['cameras'].get(camera_name)
            if camera_id is None:
                logging.error(f"No se encontró la cámara con nombre: {camera_name}")
                return

            # Aquí asumimos que ya tienes una forma de obtener el objeto de cámara basado en el ID
            #self.camera = self.system.get_camera_by_id(camera_id)
            self.camera = self.system.camera(camera_id=camera_id)
            self.camera.open()

            # Arm the camera for capturing a single frame
            self.camera.arm('SingleFrame')
            # Capture the frame
            frame = self.camera.acquire_frame()
            # Access the image data from the frame
            image_data = frame.buffer_data_numpy()
            # Generate name for the image file based on the current timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # Define the directory where the image will be saved
            project_dir = Path(__file__).resolve().parents[1]
            image_dir = project_dir.joinpath(f"camera/images/{camera_name}/input")
            image_dir.mkdir(parents=True, exist_ok=True)
            filename = image_dir.joinpath(f"{timestamp}.png")
            # Save the image as a PNG file using OpenCV
            cv2.imwrite(str(filename), cv2.cvtColor(image_data, cv2.COLOR_RGB2BGR))
            logging.info(f"Image saved successfully as {filename}.")
        except Exception as e:
            logging.error(f"Failed to capture and save image: {e}")
        finally:
            #if self.camera and self.camera.is_open:
            if self.camera and self.camera._is_armed:
                self.camera.close()

    def status_camera(self):
        """Devuelve el estado actual de la cámara."""
        if self.camera.is_open:
            return "Camera is open and ready."
        else:
            return "Camera is not open."
        
    def close_camera(self):
        """Cierra la cámara y libera los recursos."""
        self.camera.close()
        logging.info(f"Camera {self.camera.id} closed successfully.")        

# Example usage
if __name__ == "__main__":
    processor = ImageProcessor()  # Create an instance of ImageProcessor
    processor.capture_image("pipes")  # Call capture_image on the instance
    
    