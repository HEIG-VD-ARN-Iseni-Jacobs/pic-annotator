# This is a sample Python script.

# Press Maj+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
from pathlib import Path
import random
from pillow_heif import register_heif_opener
import yaml

# Register HEIF opener with PIL
register_heif_opener()

def load_config():
    """Load configuration from YAML file"""
    config_path = Path("config.yaml")
    if not config_path.exists():
        raise FileNotFoundError("config.yaml not found!")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Validate config
    if 'author' not in config:
        raise ValueError("Author not specified in config.yaml")
    if 'categories' not in config:
        raise ValueError("Categories not specified in config.yaml")
    if len(config['categories']) > 10:
        raise ValueError("Maximum 10 categories allowed")
    
    return config

# Load configuration
CONFIG = load_config()
AUTHOR = CONFIG['author']
CATEGORIES = [(cat['display_name'], cat['file_prefix']) for cat in CONFIG['categories']]

def convert_heic_to_jpg(folder_path):
    """Convert all HEIC images in the folder to JPG format"""
    heic_files = list(folder_path.glob("*.heic")) + list(folder_path.glob("*.HEIC"))
    
    if not heic_files:
        return
    
    converted_count = 0
    for heic_path in heic_files:
        try:
            # Open HEIC image
            with Image.open(heic_path) as img:
                # Create JPG filename
                jpg_path = heic_path.with_suffix('.jpg')
                
                # Convert and save as JPG
                img.convert('RGB').save(jpg_path, 'JPEG', quality=95)
                
                # Remove original HEIC file
                heic_path.unlink()
                
                converted_count += 1
        except Exception as e:
            print(f"Error converting {heic_path}: {str(e)}")
    
    if converted_count > 0:
        print(f"Converted {converted_count} HEIC images to JPG")

class ImageApp(tk.Tk):
    """Main application class with navigation"""
    def __init__(self):
        super().__init__()
        self.title("Image Processing Tool")
        
        # Make application full screen
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}+0+0")
        
        # Setup folder structure
        self.base_folder = Path("images")
        self.to_process_folder = self.base_folder / "0_to_process"
        self.categorized_folder = self.base_folder / "1_categorized"
        self.cropped_folder = self.base_folder / "2_cropped"
        self.multi_cropped_folder = self.base_folder / "3_multi_cropped"
        self.rotated_folder = self.base_folder / "4_rotated"
        
        # Create folders if they don't exist
        self.to_process_folder.mkdir(parents=True, exist_ok=True)
        self.categorized_folder.mkdir(parents=True, exist_ok=True)
        self.cropped_folder.mkdir(parents=True, exist_ok=True)
        self.multi_cropped_folder.mkdir(parents=True, exist_ok=True)
        self.rotated_folder.mkdir(parents=True, exist_ok=True)
        
        # Convert HEIC images to JPG at startup
        convert_heic_to_jpg(self.to_process_folder)
        
        # Create notebook for tab navigation
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create tabs
        self.categorizer_frame = ttk.Frame(self.notebook)
        self.crop_frame = ttk.Frame(self.notebook)
        self.multi_crop_frame = ttk.Frame(self.notebook)
        self.rotator_frame = ttk.Frame(self.notebook)
        
        # Add tabs in order
        self.notebook.add(self.categorizer_frame, text="Categorize Images")
        self.notebook.add(self.crop_frame, text="Crop Image")
        self.notebook.add(self.multi_crop_frame, text="Multi-Crop Images")
        self.notebook.add(self.rotator_frame, text="Rotate Images")
        
        # Initialize widgets
        self.categorizer = Categorizer(self.categorizer_frame, self)
        self.crop = Crop(self.crop_frame, self)
        self.multi_crop = MultiCropper(self.multi_crop_frame, self)
        self.rotator = Rotator(self.rotator_frame, self)
        
        # Set up global key bindings for each tab
        self.bind('<Return>', self.handle_return_key)
        self.bind('<Delete>', self.handle_delete_key)
        
        # Bind tab change event to update focus
        self.notebook.bind('<<NotebookTabChanged>>', self.tab_changed)
    
    def tab_changed(self, event):
        """Handle tab change event to update focus"""
        current_tab = self.notebook.select()
        if current_tab == str(self.categorizer_frame):
            self.categorizer.focus_set()
        elif current_tab == str(self.crop_frame):
            self.crop.focus_set()
        elif current_tab == str(self.multi_crop_frame):
            self.multi_crop.focus_set()
        elif current_tab == str(self.rotator_frame):
            self.rotator.focus_set()
    
    def handle_return_key(self, event):
        """Handle Return key press based on active tab"""
        current_tab = self.notebook.select()
        if current_tab == str(self.categorizer_frame):
            self.categorizer.keep_image()
        elif current_tab == str(self.crop_frame):
            self.crop.save_and_next()
    
    def handle_delete_key(self, event):
        """Handle Delete key press based on active tab"""
        current_tab = self.notebook.select()
        if current_tab == str(self.categorizer_frame):
            self.categorizer.delete_image()

class Categorizer(tk.Frame):
    """Widget for categorizing images"""
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.pack(fill=tk.BOTH, expand=True)
        
        # Initialize category counters
        self.category_counters = {}
        self._initialize_category_counters()
        
        # Create main container
        self.container = tk.Frame(self)
        self.container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create left frame for image
        self.left_frame = tk.Frame(self.container)
        self.left_frame.pack(side=tk.LEFT, padx=(0, 10), fill=tk.BOTH, expand=True)
        
        # Create image label
        self.image_label = tk.Label(self.left_frame)
        self.image_label.pack(pady=10)
        
        # Create button frame with fixed height
        self.button_frame = tk.Frame(self.left_frame, height=50)
        self.button_frame.pack(pady=10, fill=tk.X)
        self.button_frame.pack_propagate(False)  # Prevent shrinking
        
        # Create buttons
        self.keep_button = tk.Button(self.button_frame, text="Keep", command=self.keep_image, 
                                     padx=20, pady=5)
        self.keep_button.pack(side=tk.LEFT, padx=5)
        
        self.delete_button = tk.Button(self.button_frame, text="Delete", command=self.delete_image,
                                      padx=20, pady=5)
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
        
        # Store the image folder path and get all image files
        self.image_files = [f for f in self.app.to_process_folder.glob("*") 
                          if f.suffix.lower() in ('.png', '.jpg', '.jpeg', '.gif', '.bmp')]
        self.current_index = 0
        
        # Bind number keys to categories
        self.setup_key_bindings()
        
        # Load and display the first image
        self.load_current_image()
    
    def _initialize_category_counters(self):
        """Initialize counters for all categories based on existing files"""
        for _, category_prefix in CATEGORIES:
            self.category_counters[category_prefix] = self._get_category_count(category_prefix)
    
    def _get_category_count(self, category):
        """Get the next available number for a category based on existing files"""
        existing_files = list(self.app.categorized_folder.glob(f"{category}_*.*"))
        if not existing_files:
            return 0
        
        # Extract numbers from existing files
        numbers = []
        for file in existing_files:
            try:
                # Split the filename and get the number part
                number_part = file.stem.split('_')[1]
                if number_part.isdigit():
                    numbers.append(int(number_part))
            except (IndexError, ValueError):
                continue
        
        # If no valid numbers found, start from 0
        if not numbers:
            return 0
            
        # Return the highest number found
        return max(numbers)
    
    def _get_unique_filename(self, category, suffix):
        """Generate a unique filename for the category"""
        while True:
            self.category_counters[category] += 1
            new_filename = f"{category}_{AUTHOR}_{self.category_counters[category]}{suffix}"
            if not (self.app.categorized_folder / new_filename).exists():
                return new_filename
    
    def setup_key_bindings(self):
        """Setup keyboard shortcuts for categories and actions"""
        # Bind number keys to categories
        for i in range(len(CATEGORIES)):
            self.app.bind(str(i), self.create_key_handler(i))
        
        # Bind Enter to Keep and Delete to delete
        self.app.bind('<Return>', lambda e: self.keep_image())
        self.app.bind('<Delete>', lambda e: self.delete_image())
    
    def create_key_handler(self, index):
        """Create a handler for number key press"""
        def handler(event):
            if self.app.notebook.select() == str(self.app.categorizer_frame):
                if index < len(CATEGORIES):
                    self.selected_category.set(CATEGORIES[index][1])
        return handler
        
    def load_current_image(self):
        if not self.image_files:
            messagebox.showinfo("Complete", "No more images to process!")
            return
            
        if self.current_index >= len(self.image_files):
            messagebox.showinfo("Complete", "All images have been processed!")
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
        self.app.title(f"Image Processing Tool - {image_path.name}")
        
        # Clear radio button selection
        self.selected_category.set("")
        
    def keep_image(self):
        if not self.selected_category.get():
            messagebox.showwarning("Warning", "Veuillez sélectionner une catégorie avant de continuer.")
            return
            
        current_image = self.image_files[self.current_index]
        category = self.selected_category.get()
        
        # Get a unique filename for the category
        new_filename = self._get_unique_filename(category, current_image.suffix)
        new_path = self.app.categorized_folder / new_filename
        
        try:
            # Move the file to the categorized folder
            current_image.rename(new_path)
            # Remove the processed file from the list
            self.image_files.pop(self.current_index)
            # Move to next image
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

class Crop(tk.Frame):
    """Widget for single image cropping"""
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.pack(fill=tk.BOTH, expand=True)
        
        # Initialize variables
        self.image_files = [f for f in self.app.categorized_folder.glob("*") 
                          if f.suffix.lower() in ('.png', '.jpg', '.jpeg', '.gif', '.bmp')]
        self.current_index = 0
        self.current_image = None
        self.photo_image = None
        self.selection_start = None
        self.selection_rect = None
        self.crop_counter = {}
        
        # Create main container
        self.container = tk.Frame(self)
        self.container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create canvas for image display and selection
        self.canvas_frame = tk.Frame(self.container)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg='gray')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Create info frame
        self.info_frame = tk.Frame(self.container)
        self.info_frame.pack(fill=tk.X, pady=5)
        
        self.file_label = tk.Label(self.info_frame, text="", font=('Arial', 10))
        self.file_label.pack(side=tk.LEFT, padx=5)
        
        self.progress_label = tk.Label(self.info_frame, text="", font=('Arial', 10))
        self.progress_label.pack(side=tk.LEFT, padx=5)
        
        # Create button frame
        self.button_frame = tk.Frame(self.container, height=60, bg="lightgray")
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        
        # Add buttons
        self.prev_button = tk.Button(self.button_frame, text="Previous", command=self.prev_image,
                                   padx=20, pady=8, bg="#e0e0e0", font=('Arial', 10, 'bold'))
        self.prev_button.pack(side=tk.LEFT, padx=20, pady=10)
        
        self.skip_button = tk.Button(self.button_frame, text="Skip (N)", command=self.next_image,
                                   padx=20, pady=8, bg="#FFA500", fg="white", font=('Arial', 10, 'bold'))
        self.skip_button.pack(side=tk.LEFT, padx=20, pady=10)
        
        self.save_button = tk.Button(self.button_frame, text="Save Crop", command=self.save_crop,
                                   padx=20, pady=8, bg="#4CAF50", fg="white", font=('Arial', 10, 'bold'))
        self.save_button.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Bind events
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.bind("<n>", lambda e: self.next_image())
        self.bind("<N>", lambda e: self.next_image())
        
        # Load first image
        if self.image_files:
            self.load_current_image()
    
    def _get_crop_count(self, base_name):
        """Get the next available number for a specific base name"""
        if base_name in self.crop_counter:
            return self.crop_counter[base_name]
        
        # Check existing files with this base name
        existing_files = list(self.app.cropped_folder.glob(f"{base_name}_crop_*.*"))
        if not existing_files:
            return 1
        
        # Extract numbers from existing files
        numbers = []
        for file in existing_files:
            try:
                number_part = file.stem.split('_crop_')[1]
                if number_part.isdigit():
                    numbers.append(int(number_part))
            except (IndexError, ValueError):
                continue
        
        # If no valid numbers found, start from 1
        if not numbers:
            return 1
            
        # Return the highest number found + 1
        return max(numbers) + 1
    
    def load_current_image(self):
        """Load and display the current image"""
        if not self.image_files or self.current_index >= len(self.image_files):
            messagebox.showinfo("Complete", "No more images to process!")
            return
        
        # Get current image path
        self.current_image_path = self.image_files[self.current_index]
        
        # Get base filename for naming crops
        self.current_base_name = self.current_image_path.stem
        
        # Initialize or get crop counter for this base name
        if self.current_base_name not in self.crop_counter:
            self.crop_counter[self.current_base_name] = self._get_crop_count(self.current_base_name)
        
        try:
            # Open and resize image to fit canvas
            self.current_image = Image.open(self.current_image_path)
            
            # Calculate resize dimensions to fit canvas while maintaining aspect ratio
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width <= 1:  # Canvas not yet drawn
                canvas_width = 800
                canvas_height = 600
            
            # Calculate resize dimensions
            img_width, img_height = self.current_image.size
            scale = min(canvas_width/img_width, canvas_height/img_height)
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            
            # Resize image
            display_img = self.current_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            self.photo_image = ImageTk.PhotoImage(display_img)
            
            # Update canvas
            self.canvas.delete("all")
            self.canvas.create_image(canvas_width//2, canvas_height//2, 
                                   image=self.photo_image, anchor=tk.CENTER)
            
            # Store scale factor for later use in cropping
            self.scale_factor = scale
            
            # Update information
            self.file_label.configure(text=f"File: {self.current_image_path.name}")
            self.progress_label.configure(text=f"Image {self.current_index + 1} of {len(self.image_files)}")
            
            # Update application title
            self.app.title(f"Image Processing Tool - Cropping: {self.current_image_path.name}")
            
            # Clear any existing selection
            if self.selection_rect:
                self.canvas.delete(self.selection_rect)
                self.selection_rect = None
            self.selection_start = None
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")
            self.next_image()
    
    def on_press(self, event):
        """Handle mouse press event"""
        # Clear previous selection
        if self.selection_rect:
            self.canvas.delete(self.selection_rect)
        
        # Store starting point
        self.selection_start = (event.x, event.y)
    
    def on_drag(self, event):
        """Handle mouse drag event"""
        if not self.selection_start:
            return
        
        # Delete previous rectangle
        if self.selection_rect:
            self.canvas.delete(self.selection_rect)
        
        # Calculate square dimensions
        x1, y1 = self.selection_start
        x2, y2 = event.x, event.y
        
        # Make it a square by using the smaller dimension
        size = min(abs(x2 - x1), abs(y2 - y1))
        
        # Determine the direction of the square
        if x2 < x1:
            x2 = x1 - size
        else:
            x2 = x1 + size
            
        if y2 < y1:
            y2 = y1 - size
        else:
            y2 = y1 + size
        
        # Draw new rectangle
        self.selection_rect = self.canvas.create_rectangle(
            x1, y1, x2, y2,
            outline='red', width=2
        )
    
    def on_release(self, event):
        """Handle mouse release event"""
        if not self.selection_start:
            return
        
        # Finalize the selection
        x1, y1 = self.selection_start
        x2, y2 = event.x, event.y
        
        # Make it a square
        size = min(abs(x2 - x1), abs(y2 - y1))
        
        if x2 < x1:
            x2 = x1 - size
        else:
            x2 = x1 + size
            
        if y2 < y1:
            y2 = y1 - size
        else:
            y2 = y1 + size
        
        # Update the rectangle
        if self.selection_rect:
            self.canvas.coords(self.selection_rect, x1, y1, x2, y2)
        
        # Store the final selection coordinates
        self.selection_coords = (x1, y1, x2, y2)
    
    def save_crop(self):
        """Save the current selection as a crop"""
        if not hasattr(self, 'selection_coords'):
            messagebox.showwarning("Warning", "Please select an area to crop first!")
            return
        
        try:
            # Get selection coordinates
            x1, y1, x2, y2 = self.selection_coords
            
            # Convert canvas coordinates to image coordinates
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            # Calculate image position on canvas
            img_width = self.photo_image.width()
            img_height = self.photo_image.height()
            img_x = (canvas_width - img_width) // 2
            img_y = (canvas_height - img_height) // 2
            
            # Convert selection coordinates to image coordinates
            x1 = (x1 - img_x) / self.scale_factor
            y1 = (y1 - img_y) / self.scale_factor
            x2 = (x2 - img_x) / self.scale_factor
            y2 = (y2 - img_y) / self.scale_factor
            
            # Ensure coordinates are within image bounds
            x1 = max(0, min(x1, self.current_image.width))
            y1 = max(0, min(y1, self.current_image.height))
            x2 = max(0, min(x2, self.current_image.width))
            y2 = max(0, min(y2, self.current_image.height))
            
            # Crop the image
            crop = self.current_image.crop((x1, y1, x2, y2))
            
            # Create filename
            extension = self.current_image_path.suffix
            crop_filename = f"{self.current_base_name}_crop_{self.crop_counter[self.current_base_name]}{extension}"
            crop_path = self.app.cropped_folder / crop_filename
            
            # Save crop
            crop.save(crop_path)
            
            # Increment counter
            self.crop_counter[self.current_base_name] += 1
            
            # Move to next image
            self.next_image()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save crop: {str(e)}")
    
    def next_image(self):
        """Move to next image"""
        if self.current_index < len(self.image_files) - 1:
            self.current_index += 1
            self.load_current_image()
        else:
            messagebox.showinfo("Complete", "All images have been processed!")
    
    def prev_image(self):
        """Move to previous image"""
        if self.current_index > 0:
            self.current_index -= 1
            self.load_current_image()

class MultiCropper(tk.Frame):
    """Widget for multi-cropping images"""
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.pack(fill=tk.BOTH, expand=True)
        
        # Initialize crop counter
        self.crop_counter = {}
        
        # Get all images in cropped folder (from single crop widget)
        self.image_files = [f for f in self.app.cropped_folder.glob("*") 
                           if f.suffix.lower() in ('.png', '.jpg', '.jpeg', '.gif', '.bmp')]
        self.current_index = 0
        
        # Create UI
        self.create_widgets()
        
        # Load first image
        if self.image_files:
            self.load_current_image()
        
        # Bind keys
        self.bind("<r>", lambda e: self.regenerate_crops())
        self.bind("<R>", lambda e: self.regenerate_crops())
    
    def create_widgets(self):
        # Main container
        self.container = tk.Frame(self)
        self.container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top section - Original image and info
        self.top_frame = tk.Frame(self.container)
        self.top_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.original_label = tk.Label(self.top_frame)
        self.original_label.pack(side=tk.LEFT, padx=5)
        
        self.info_frame = tk.Frame(self.top_frame)
        self.info_frame.pack(side=tk.LEFT, padx=20, fill=tk.Y)
        
        self.file_label = tk.Label(self.info_frame, text="", font=('Arial', 10))
        self.file_label.pack(anchor=tk.W, pady=2)
        
        self.progress_label = tk.Label(self.info_frame, text="", font=('Arial', 10))
        self.progress_label.pack(anchor=tk.W, pady=2)
        
        # Middle section - Crops grid
        self.crops_frame = tk.Frame(self.container)
        self.crops_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=10)
        
        # 3x3 grid for crops
        self.crop_frames = []
        self.crop_labels = []
        self.crop_selected = [False] * 9
        
        # Create 3x3 grid
        for row in range(3):
            for col in range(3):
                index = row * 3 + col
                frame = tk.Frame(self.crops_frame, borderwidth=2, relief="groove")
                frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
                
                # Configure grid to make cells equal size
                self.crops_frame.grid_columnconfigure(col, weight=1)
                self.crops_frame.grid_rowconfigure(row, weight=1)
                
                # Create label for crop
                label = tk.Label(frame)
                label.pack(fill=tk.BOTH, expand=True)
                
                # Bind click event
                label.bind("<Button-1>", lambda e, idx=index: self.toggle_selection(idx))
                
                self.crop_frames.append(frame)
                self.crop_labels.append(label)
        
        # Create a separate frame at the bottom of the main container for buttons
        button_container = tk.Frame(self.container, height=60, bg="lightgray")
        button_container.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        
        # Add buttons with larger size and clear colors
        self.prev_button = tk.Button(button_container, text="Previous", command=self.prev_image,
                                  padx=20, pady=8, bg="#e0e0e0", font=('Arial', 10, 'bold'))
        self.prev_button.pack(side=tk.LEFT, padx=20, pady=10)
        
        self.refresh_button = tk.Button(button_container, text="Refresh Crops (R)", command=self.regenerate_crops,
                                     padx=20, pady=8, bg="#2196F3", fg="white", font=('Arial', 10, 'bold'))
        self.refresh_button.pack(side=tk.LEFT, padx=20, pady=10)
        
        self.next_button = tk.Button(button_container, text="Save & Next", command=self.save_and_next,
                                  padx=20, pady=8, bg="#4CAF50", fg="white", font=('Arial', 10, 'bold'))
        self.next_button.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Custom binding for this widget
        self.bind("<Return>", lambda e: self.save_and_next())
    
    def _get_crop_count(self, base_name):
        """Get the next available number for a specific base name"""
        if base_name in self.crop_counter:
            return self.crop_counter[base_name]
        
        # Check existing files with this base name
        existing_files = list(self.app.multi_cropped_folder.glob(f"{base_name}_crop_*.*"))
        if not existing_files:
            return 1
        
        # Extract numbers from existing files
        numbers = []
        for file in existing_files:
            try:
                number_part = file.stem.split('_crop_')[1]
                if number_part.isdigit():
                    numbers.append(int(number_part))
            except (IndexError, ValueError):
                continue
        
        # If no valid numbers found, start from 1
        if not numbers:
            return 1
            
        # Return the highest number found + 1
        return max(numbers) + 1
    
    def load_current_image(self):
        """Load the current image and generate crops"""
        if not self.image_files or self.current_index >= len(self.image_files):
            messagebox.showinfo("Complete", "No more images to crop!")
            return
        
        # Get current image path
        self.current_image_path = self.image_files[self.current_index]
        
        # Get base filename (without extension) for naming crops
        self.current_base_name = self.current_image_path.stem
        
        # Initialize or get crop counter for this base name
        if self.current_base_name not in self.crop_counter:
            self.crop_counter[self.current_base_name] = self._get_crop_count(self.current_base_name)
        
        # Reset selection
        self.crop_selected = [False] * 9
        
        # Open image
        try:
            original = Image.open(self.current_image_path)
            
            # Display original image (resized)
            max_size = (300, 300)
            display_img = original.copy()
            display_img.thumbnail(max_size, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(display_img)
            self.original_label.configure(image=photo)
            self.original_label.image = photo
            
            # Update information
            self.file_label.configure(text=f"File: {self.current_image_path.name}")
            self.progress_label.configure(text=f"Image {self.current_index + 1} of {len(self.image_files)}")
            
            # Calculate original dimensions for crop positions
            width, height = original.size
            
            # Generate nine crops
            self.crops = []
            crop_positions = self._generate_crop_positions(width, height)
            
            for i, (x, y, w, h) in enumerate(crop_positions):
                # Create crop
                crop = original.crop((x, y, x + w, y + h))
                self.crops.append(crop)
                
                # Create thumbnail for display
                max_crop_size = (200, 200)
                crop_display = crop.copy()
                crop_display.thumbnail(max_crop_size, Image.Resampling.LANCZOS)
                
                # Convert to PhotoImage
                photo = ImageTk.PhotoImage(crop_display)
                
                # Update label
                self.crop_labels[i].configure(image=photo)
                self.crop_labels[i].image = photo
                
                # Reset frame border
                self.crop_frames[i].configure(background="lightgray")
            
            # Update application title
            self.app.title(f"Image Processing Tool - Cropping: {self.current_image_path.name}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process image: {str(e)}")
            self.current_index += 1
            self.load_current_image()
    
    def _generate_crop_positions(self, width, height):
        """Generate 9 random square crop positions within the image"""
        # Use the smaller dimension to determine max crop size
        min_dimension = min(width, height)
        
        # Less aggressive crop size (40-60% of the smaller dimension)
        min_crop_size = int(min_dimension * 0.4)
        max_crop_size = int(min_dimension * 0.6)
        
        crop_positions = []
        
        for _ in range(9):
            # Random square size
            crop_size = random.randint(min_crop_size, max_crop_size)
            
            # Random position (ensure crop is within image bounds)
            x = random.randint(0, width - crop_size)
            y = random.randint(0, height - crop_size)
            
            crop_positions.append((x, y, crop_size, crop_size))
        
        return crop_positions
    
    def toggle_selection(self, index):
        """Toggle selection of a crop"""
        if 0 <= index < 9:
            self.crop_selected[index] = not self.crop_selected[index]
            # Update visual indication
            color = "green" if self.crop_selected[index] else "lightgray"
            self.crop_frames[index].configure(background=color)
    
    def prev_image(self):
        """Go to previous image"""
        if self.current_index > 0:
            self.current_index -= 1
            self.load_current_image()
    
    def save_and_next(self):
        """Save selected crops and advance to next image"""
        if not self.image_files or self.current_index >= len(self.image_files):
            return
        
        # Save selected crops
        for i, selected in enumerate(self.crop_selected):
            if selected and i < len(self.crops):
                try:
                    # Get file extension from original
                    extension = self.current_image_path.suffix
                    
                    # Create filename with original name and crop index
                    crop_filename = f"{self.current_base_name}_crop_{self.crop_counter[self.current_base_name]}{extension}"
                    crop_path = self.app.multi_cropped_folder / crop_filename
                    
                    # Save crop
                    self.crops[i].save(crop_path)
                    
                    # Increment counter for next crop
                    self.crop_counter[self.current_base_name] += 1
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save crop: {str(e)}")
        
        # Move to next image
        self.current_index += 1
        
        if self.current_index < len(self.image_files):
            self.load_current_image()
        else:
            messagebox.showinfo("Complete", "All images have been processed!")
    
    def regenerate_crops(self):
        """Regenerate crops for the current image"""
        if not self.image_files or self.current_index >= len(self.image_files):
            return
            
        # Reset selection
        self.crop_selected = [False] * 9
        
        try:
            # Get current image
            image_path = self.image_files[self.current_index]
            original = Image.open(image_path)
            
            # Calculate original dimensions for crop positions
            width, height = original.size
            
            # Generate new crop positions
            crop_positions = self._generate_crop_positions(width, height)
            
            # Clear existing crops
            self.crops = []
            
            # Create new crops
            for i, (x, y, w, h) in enumerate(crop_positions):
                # Create crop
                crop = original.crop((x, y, x + w, y + h))
                self.crops.append(crop)
                
                # Create thumbnail for display
                max_crop_size = (200, 200)
                crop_display = crop.copy()
                crop_display.thumbnail(max_crop_size, Image.Resampling.LANCZOS)
                
                # Convert to PhotoImage
                photo = ImageTk.PhotoImage(crop_display)
                
                # Update label
                self.crop_labels[i].configure(image=photo)
                self.crop_labels[i].image = photo
                
                # Reset frame border
                self.crop_frames[i].configure(background="lightgray")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to regenerate crops: {str(e)}")

class Rotator(tk.Frame):
    """Widget for rotating images"""
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.pack(fill=tk.BOTH, expand=True)
        
        # Create main container
        self.container = tk.Frame(self)
        self.container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create info label
        self.info_label = tk.Label(self.container, text="Click the button below to generate rotated versions of all images in the multi-cropped folder.", 
                                 font=('Arial', 12), wraplength=600)
        self.info_label.pack(pady=20)
        
        # Create status label
        self.status_label = tk.Label(self.container, text="", font=('Arial', 10))
        self.status_label.pack(pady=10)
        
        # Create button
        self.rotate_button = tk.Button(self.container, text="Generate Rotated Images", 
                                     command=self.generate_rotated_images,
                                     padx=20, pady=10, bg="#2196F3", fg="white",
                                     font=('Arial', 12, 'bold'))
        self.rotate_button.pack(pady=20)
        
        # Define rotation intervals
        self.rotation_intervals = [
            (-35, -20),
            (-20, -5),
            (5, 20),
            (20, 35)
        ]
    
    def generate_rotated_images(self):
        """Generate rotated versions of all images in the multi-cropped folder"""
        # Get all images in multi-cropped folder
        image_files = [f for f in self.app.multi_cropped_folder.glob("*") 
                      if f.suffix.lower() in ('.png', '.jpg', '.jpeg', '.gif', '.bmp')]
        
        if not image_files:
            messagebox.showinfo("Info", "No images found in the multi-cropped folder!")
            return
        
        total_images = len(image_files)
        processed = 0
        
        try:
            for image_path in image_files:
                # Update status
                self.status_label.configure(text=f"Processing {image_path.name}...")
                self.update()
                
                # Open image
                with Image.open(image_path) as img:
                    # Generate 4 rotated versions
                    for i, (min_angle, max_angle) in enumerate(self.rotation_intervals):
                        # Generate random angle within interval
                        angle = random.uniform(min_angle, max_angle)
                        
                        # Rotate image
                        rotated = img.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)
                        
                        # Create filename for rotated image
                        base_name = image_path.stem
                        extension = image_path.suffix
                        rotated_filename = f"{base_name}_rot_{i+1}{extension}"
                        rotated_path = self.app.rotated_folder / rotated_filename
                        
                        # Save rotated image
                        rotated.save(rotated_path)
                
                processed += 1
                self.status_label.configure(text=f"Processed {processed}/{total_images} images")
                self.update()
            
            messagebox.showinfo("Complete", f"Successfully generated rotated versions of {total_images} images!")
            self.status_label.configure(text="")
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.status_label.configure(text="")

def main():
    app = ImageApp()
    app.mainloop()

if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
