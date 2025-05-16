# This is a sample Python script.

# Press Maj+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
from pathlib import Path

# Configuration - Easy to modify categories
# Format: ("Display Name", "file_name_prefix")
# Maximum 10 categories (0-9 keys)
CATEGORIES = [
    ("Sens interdit", "sens_interdit"),
    ("Céder le passage", "ceder_le_passage"),
    ("Stop", "stop"),
    ("Giratoire", "giratoire")
]

# Validate categories
if len(CATEGORIES) > 10:
    raise ValueError("Maximum 10 categories allowed")

class ImageViewer:
    def __init__(self, root, base_folder):
        self.root = root
        self.root.title("Image Viewer")
        
        # Setup folder structure
        self.base_folder = Path(base_folder)
        self.to_process_folder = self.base_folder / "to_process"
        self.categorized_folder = self.base_folder / "categorized"
        
        # Create folders if they don't exist
        self.to_process_folder.mkdir(parents=True, exist_ok=True)
        self.categorized_folder.mkdir(parents=True, exist_ok=True)
        
        # Store the image folder path and get all image files
        self.image_files = [f for f in self.to_process_folder.glob("*") 
                          if f.suffix.lower() in ('.png', '.jpg', '.jpeg', '.gif', '.bmp')]
        self.current_index = 0
        
        # Category counters for file naming
        self.category_counters = {cat[1]: 0 for cat in CATEGORIES}
        
        # Create main container
        self.container = tk.Frame(root)
        self.container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create left frame for image
        self.left_frame = tk.Frame(self.container)
        self.left_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        # Create image label
        self.image_label = tk.Label(self.left_frame)
        self.image_label.pack(pady=10)
        
        # Create button frame
        self.button_frame = tk.Frame(self.left_frame)
        self.button_frame.pack(pady=10)
        
        # Create buttons
        self.keep_button = tk.Button(self.button_frame, text="Keep", command=self.keep_image)
        self.keep_button.pack(side=tk.LEFT, padx=5)
        
        self.delete_button = tk.Button(self.button_frame, text="Delete", command=self.delete_image)
        self.delete_button.pack(side=tk.LEFT, padx=5)
        
        # Create right frame for radio buttons
        self.right_frame = tk.Frame(self.container)
        self.right_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 0))
        
        # Create label for categories
        tk.Label(self.right_frame, text="Catégories:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 10))
        
        # Radio buttons setup
        self.selected_category = tk.StringVar()
        
        # Create radio buttons with number labels
        for i, (text, value) in enumerate(CATEGORIES):
            label_text = f"{i}: {text}"
            rb = tk.Radiobutton(
                self.right_frame,
                text=label_text,
                value=value,
                variable=self.selected_category
            )
            rb.pack(anchor=tk.W, pady=2)
        
        # Bind number keys to categories
        self.setup_key_bindings()
        
        # Load and display the first image
        self.load_current_image()
    
    def setup_key_bindings(self):
        """Setup keyboard shortcuts for categories and actions"""
        # Bind number keys to categories
        for i in range(len(CATEGORIES)):
            self.root.bind(str(i), self.create_key_handler(i))
        
        # Bind Enter to Keep and Delete to delete
        self.root.bind('<Return>', lambda e: self.keep_image())
        self.root.bind('<Delete>', lambda e: self.delete_image())
    
    def create_key_handler(self, index):
        """Create a handler for number key press"""
        def handler(event):
            if index < len(CATEGORIES):
                self.selected_category.set(CATEGORIES[index][1])
        return handler
        
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
        
        # Clear radio button selection
        self.selected_category.set("")
        
    def keep_image(self):
        if not self.selected_category.get():
            messagebox.showwarning("Warning", "Veuillez sélectionner une catégorie avant de continuer.")
            return
            
        current_image = self.image_files[self.current_index]
        category = self.selected_category.get()
        
        # Increment counter for the selected category
        self.category_counters[category] += 1
        
        # Create new filename with category and index
        new_filename = f"{category}_{self.category_counters[category]}{current_image.suffix}"
        new_path = self.categorized_folder / new_filename
        
        try:
            # Move the file to the categorized folder
            current_image.rename(new_path)
            # Update the list with the new path
            self.image_files[self.current_index] = new_path
            # Move to next image
            self.current_index += 1
            self.load_current_image()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to move image: {str(e)}")
        
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
    
    # Get the base folder path
    base_folder = "images"  # Default folder name
    
    # Create the image viewer
    app = ImageViewer(root, base_folder)
    
    # Start the application
    root.mainloop()

if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
