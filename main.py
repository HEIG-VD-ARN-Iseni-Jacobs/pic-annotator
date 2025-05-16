# This is a sample Python script.

# Press Maj+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
from pathlib import Path

class ImageViewer:
    def __init__(self, root, image_folder):
        self.root = root
        self.root.title("Image Viewer")
        
        # Store the image folder path and get all image files
        self.image_folder = Path(image_folder)
        self.image_files = [f for f in self.image_folder.glob("*") 
                          if f.suffix.lower() in ('.png', '.jpg', '.jpeg', '.gif', '.bmp')]
        self.current_index = 0
        
        # Create main frame
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(padx=10, pady=10)
        
        # Create image label
        self.image_label = tk.Label(self.main_frame)
        self.image_label.pack(pady=10)
        
        # Create button frame
        self.button_frame = tk.Frame(self.main_frame)
        self.button_frame.pack(pady=10)
        
        # Create buttons
        self.keep_button = tk.Button(self.button_frame, text="Keep", command=self.keep_image)
        self.keep_button.pack(side=tk.LEFT, padx=5)
        
        self.delete_button = tk.Button(self.button_frame, text="Delete", command=self.delete_image)
        self.delete_button.pack(side=tk.LEFT, padx=5)
        
        # Load and display the first image
        self.load_current_image()
        
    def load_current_image(self):
        if not self.image_files:
            messagebox.showinfo("Complete", "No more images to process!")
            self.root.quit()
            return
            
        if self.current_index >= len(self.image_files):
            messagebox.showinfo("Complete", "All images have been processed!")
            self.root.quit()
            return
            
        # Get current image path
        image_path = self.image_files[self.current_index]
        
        # Open and resize image to fit window
        image = Image.open(image_path)
        
        # Calculate new size while maintaining aspect ratio
        max_size = (800, 600)
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(image)
        
        # Update image label
        self.image_label.configure(image=photo)
        self.image_label.image = photo  # Keep a reference!
        
        # Update window title with current image name
        self.root.title(f"Image Viewer - {image_path.name}")
        
    def keep_image(self):
        self.current_index += 1
        self.load_current_image()
        
    def delete_image(self):
        if not self.image_files:
            return
            
        current_image = self.image_files[self.current_index]
        try:
            os.remove(current_image)
            self.image_files.pop(self.current_index)
            self.load_current_image()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete image: {str(e)}")

def main():
    # Create the root window
    root = tk.Tk()
    
    # Get the image folder path (you can modify this to your desired folder)
    image_folder = "images"  # Default folder name
    
    # Create the image viewer
    app = ImageViewer(root, image_folder)
    
    # Start the application
    root.mainloop()

if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
