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

class ImageProcessor:
    def __init__(self):
        # Logger configuration for the camera module
        logging.basicConfig(filename='logs/camera.log', 
                            level=logging.INFO, 
                            format='%(asctime)s:%(levelname)s:%(message)s')
        
        # Leer la configuración de cameras y parámetros desde config.json
        config_path = Path('camera/config.json')
        if not config_path.exists():
            logging.error("config.json file not found.")
            raise FileNotFoundError("config.json file not found.")

        with open(config_path, 'r') as config_file:
            self.config = json.load(config_file)
        
        self.cameras = self.config.get("cameras", {})
        self.parameters = self.config.get("parameters", {})

        if not self.cameras:
            logging.error("No camera configurations found in config.json.")
            raise ValueError("No camera configurations found in config.json.")

        with Vimba.get_instance() as vimba:
            self.vimba = vimba
            self.available_cameras = self.vimba.get_all_cameras()
            if not self.available_cameras:
                logging.error("No cameras found.")
                raise RuntimeError("No cameras found.")
            
        self.available_camera_ids = [camera.get_id() for camera in self.available_cameras]
        logging.info(f"Available cameras: {self.available_camera_ids}")

    def apply_settings(self):
        for name, camera_id in self.cameras.items():
            if camera_id in self.available_camera_ids:
                config_file = self.parameters.get(name)
                if config_file:
                    self.load_settings(camera_id, config_file)
                else:
                    logging.warning(f"No settings file found for camera {name} with ID {camera_id}")
            else:
                logging.warning(f"Camera {name} with ID {camera_id} is not available")

    def load_settings(self, cam_id, path_config):
            config_file_path = Path(path_config)
            if not config_file_path.exists():
                logging.error(f"Configuration file {path_config} not found.")
                raise FileNotFoundError(f"Configuration file {path_config} not found.")
            with Vimba.get_instance() as vimba:   
                with vimba.get_camera_by_id(cam_id) as cam:
                    try:
                        cam.load_settings(str(config_file_path), PersistType.All)
                        logging.info(f"Settings loaded for camera {cam_id} from '{path_config}'")
                    except Exception as e:
                        logging.error(f"Failed to load settings for camera {cam_id}: {e}")
                        
                        
    def capture_image(self, cam_id):
        if cam_id not in self.available_camera_ids:
            logging.error(f"Camera {cam_id} is not available")
            raise ValueError(f"Camera {cam_id} is not available")

        save_dir = Path('images/nuts/input')
        save_dir.mkdir(parents=True, exist_ok=True)

        # Generate a unique filename based on the current timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")
        save_path = save_dir / f"image_{timestamp}.png"
        
        with Vimba.get_instance() as vimba:   
            with vimba.get_camera_by_id(cam_id) as cam:
                try:
                    cam.open()
                    frame = cam.get_frame()
                    frame.convert_pixel_format(PixelFormat.Mono8)  # Convert to a standard format if necessary
                    frame.save(str(save_path))
                    logging.info(f"Image captured and saved to '{save_path}' from camera {cam_id}")
                except Exception as e:
                    logging.error(f"Failed to capture image from camera {cam_id}: {e}")
                finally:
                    cam._close()
                    
    #def __del__(self):
        #self.vimba._shutdown()                    

if __name__ == "__main__":
    processor = ImageProcessor()
    processor.apply_settings()
    processor.capture_image("DEV_000F315D5D33")


"""     def capture_image(self, camera_name):
        try:
            # Buscar el ID de la cámara usando el nombre
            camera_id = self.config['cameras'].get(camera_name)
            if camera_id is None:
                logging.error(f"No se encontró la cámara con nombre: {camera_name}")
                return
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
            if self.camera and self.camera._is_armed:
                self.camera.close() """    
    