from pymba import Vimba
from typing import Optional
from PIL import Image
import numpy as np

class ImageProcessor:
    def __init__(self):
        self.system = Vimba()
        self.system.startup()
        camera_ids = self.system.camera_ids()
        if not camera_ids:
            raise ValueError("No cameras found.")
        self.camera = self.system.camera(camera_ids[0])
        self.camera.open()

    def capture_image(self, path: str) -> None:
        # Arm the camera for capturing a single frame
        self.camera.arm('SingleFrame')
        # Capture the frame
        frame = self.camera.acquire_frame()
        # Access the image data from the frame
        image_data = frame.buffer_data_numpy()
        # Convert numpy array to an image
        image = Image.fromarray(image_data)
        # Save the image
        image.save(path)

# Example usage
if __name__ == "__main__":
    processor = ImageProcessor()
    processor.capture_image('image.jpg')
                                   