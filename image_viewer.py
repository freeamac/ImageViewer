import base64
from dataclasses import dataclass
from io import BytesIO
import os
from pathlib import Path
import tkinter as tk
from tkinter import PhotoImage, filedialog, messagebox, simpledialog
import sys
import xml.etree.ElementTree as ET

from PIL import Image, ImageTk


class Slideshow:
    def __init__(self, root, image_collection, collection_name):
        # Initialize slideshow window
        self.root = tk.Toplevel(root)
        self.root.attributes("-fullscreen", True)  # Make it fullscreen
        self.images = image_collection
        self.current_index = 0
        self.running = True
        self.parent = root  # Reference to the main window
        self.root.title(collection_name)

        # Label to display images in the slideshow
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.image_area = tk.Label(self.main_frame, bg="black")
        self.image_area.pack(fill=tk.BOTH, side=tk.TOP, expand=True)

        # Area for image metadata display
        self.image_metadata_frame = tk.Frame(self.main_frame, bg="lightgray", height=50)
        self.image_metadata_line1_frame = tk.Frame(self.image_metadata_frame, bg="lightgray")
        self.caption_text_label = tk.Label(self.image_metadata_line1_frame, bg="lightgray", fg="black", text="No Image Information")
        self.caption_text_label.pack(side=tk.TOP, pady=10)
        self.date_label = tk.Label(self.image_metadata_line1_frame, bg="lightgray", fg="black", text="")
        self.date_label.pack(side=tk.LEFT, padx=10)
        self.asa_label = tk.Label(self.image_metadata_line1_frame, bg="lightgray", fg="black", text="")
        self.asa_label.pack(side=tk.RIGHT, padx=10)
        self.image_metadata_line1_frame.pack(side=tk.TOP, fill=tk.X)
        self.image_metadata_line2_frame = tk.Frame(self.image_metadata_frame, bg="lightgray")
        self.location_label = tk.Label(self.image_metadata_line2_frame, bg="lightgray", fg="black", text="")
        self.location_label.pack(side=tk.LEFT, padx=10)
        self.roll_number_label = tk.Label(self.image_metadata_line2_frame, bg="lightgray", fg="black", text="")
        self.roll_number_label.pack(side=tk.RIGHT, padx=10)
        self.image_metadata_line2_frame.pack(side=tk.TOP, fill=tk.X)
        self.image_metadata_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Ask the user for the slideshow interval (in seconds)
        self.interval = self.get_slideshow_interval()

        # Bind the Escape key to exit fullscreen mode
        self.root.bind("<Escape>", lambda event: self.exit_fullscreen())

        # Start the slideshow by showing the first image
        self.show_image(self.current_index)
        self.schedule_next_image()

    def get_slideshow_interval(self):
        """Prompt the user to enter the slideshow interval."""
        try:
            # Ask user for the interval in seconds
            self.root.withdraw()  # Hide the main window while dialog is open
            interval = simpledialog.askinteger(
                "Slideshow Interval",
                "Enter the time (in seconds) for each slide:",
                minvalue=1,
                maxvalue=60,
                parent=self.parent,  # Attach dialog to slideshow window
            )
            self.root.deiconify()  # Restore the main window
            return interval if interval else 3  # Default to 3 seconds if no input
        except Exception as e:
            print(f"Error getting slideshow interval: {e}")
            self.root.deiconify()  # Restore the main window
            return 3  # Fallback to default interval

    def show_image(self, index):
        """Display the current image based on index."""
        try:
            image_path = self.images[index].image_path
            image = Image.open(image_path)

            # Get the screen dimensions for resizing the image
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight() - 200  # Leave space for metadata

            # Resize image to fit screen size
            image.thumbnail((screen_width, screen_height))
            self.current_image = ImageTk.PhotoImage(image)

            # Update the label with the image
            self.image_area.config(image=self.current_image)

            # Get image metadata information
            self.caption_text_label.config(text=self.images[index].image_cpation)
            self.date_label.config(text=self.images[index].image_date)
            if self.images[index].image_asa is not None:
                self.asa_label.config(text=f"ASA: {self.images[index].image_asa}")
            else:
                self.asa_label.config(text="")
            self.location_label.config(text=self.images[index].image_location)
            if self.images[index].roll_number is not None:
                self.roll_number_label.config(text=f"{self.images[index].roll_number} of {self.images[index].roll_max}")
            else:
                self.roll_number_label.config(text="")
        except Exception as e:
            # Display error if the image can't be loaded
            messagebox.showerror("Error", f"Failed to load image: {e}")
            self.exit_fullscreen()

    def schedule_next_image(self):
        """Schedule the next image after the current interval."""
        if self.running and self.images:
            # Update index to show the next image
            self.current_index = (self.current_index + 1) % len(self.images)
            self.root.after(self.interval * 1000, self.show_next_image)  # Delay in ms

    def show_next_image(self):
        """Show the next image and schedule the next frame."""
        if self.running:
            self.show_image(self.current_index)
            self.schedule_next_image()

    def exit_fullscreen(self, event=None):
        """Stop the slideshow and exit fullscreen mode."""
        self.running = False
        self.root.destroy()  # Close the slideshow window
        self.parent.focus_force()  # Return focus to the main window


@dataclass
class ImageInfo:
    def __init__(self, image_path, image_date, image_location, image_cpation, image_asa=None, roll_number=None, roll_max=None):
        self.image_path = image_path
        self.image_date = image_date
        self.image_location = image_location
        self.image_cpation = image_cpation
        self.image_asa = image_asa
        self.roll_number = roll_number
        self.roll_max = roll_max


class ImageViewerApp:
    def __init__(self, root):
        self.root = root
        self.collection_name = "Image Viewer"
        self.root.title(self.collection_name)
        self.root.state("normal")  # Start window maximized
        self.root.minsize(1000, 800)  # Set minimum window size

        # Set the custom window icon
        self.set_window_icon()

        # Initialize image list and index
        self.collection_path = ""
        self.collection_images = []
        self.current_image_index = 0

        # UI Setup
        self.setup_menu()
        self.setup_layout()

        # Bind keyboard shortcuts for navigation
        self.root.bind("<Left>", lambda event: self.show_previous_image())  # Left arrow
        self.root.bind("<Right>", lambda event: self.show_next_image())  # Right arrow
        self.root.bind("<Escape>", lambda event: self.show_first_image())  # Right arrow

    def set_window_icon(self):
        """Set the window icon using an embedded base64 string."""
        icon_base64 = self.get_icon_data()  # Use the icon data from the method

        try:
            # Decode the base64 string to binary data
            icon_data = base64.b64decode(icon_base64)

            # Convert the binary data into an Image object
            icon_image = Image.open(BytesIO(icon_data))
            icon_image = ImageTk.PhotoImage(icon_image)

            # Set the window icon
            self.root.iconphoto(True, icon_image)
        except Exception as e:
            print(f"Error setting window icon: {e}")

    def get_icon_data(self):
        """Retrieve the base64 encoded icon data."""
        try:
            # Get the correct path to the icon file, whether running in development or as a packaged app
            if getattr(sys, 'frozen', False):
                # Running in a bundled executable
                icon_path = os.path.join(sys._MEIPASS, 'camera.ico')
            else:
                # Running in a script (development mode)
                icon_path = 'camera.ico'

            # Open the icon file and encode it to base64
            with open(icon_path, 'rb') as icon_file:
                icon_data = base64.b64encode(icon_file.read()).decode('utf-8')
            return icon_data
        except Exception as e:
            print(f"Error loading icon: {e}")
            return None

    def setup_menu(self):
        self.menu_bar = tk.Menu(self.root)

        self.menu_bar.add_command(label="Open", command=self.open_collection)
        self.menu_bar.add_command(label="Reset", command=self.reset_collection)
        self.menu_bar.add_command(label="Slideshow", command=self.start_slideshow)

        self.root.config(menu=self.menu_bar)

    def retrieve_collection(self):
        self.show_image(self.current_image_index)

    def setup_layout(self):
        """Set up the main layout of the application."""
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Label to display the current image
        self.image_area = tk.Label(
            self.main_frame, text="No Image Loaded", bg="gray", fg="white"
        )
        self.image_area.pack(fill=tk.BOTH, expand=True)

        # Area for image metadata display
        self.image_metadata_frame = tk.Frame(self.main_frame, bg="lightgray", height=50)
        self.image_metadata_line1_frame = tk.Frame(self.image_metadata_frame, bg="lightgray")
        self.caption_text_label = tk.Label(self.image_metadata_line1_frame, bg="lightgray", fg="black", text="No Image Information")
        self.caption_text_label.pack(side=tk.TOP, pady=10)
        self.date_label = tk.Label(self.image_metadata_line1_frame, bg="lightgray", fg="black", text="")
        self.date_label.pack(side=tk.LEFT, padx=10)
        self.asa_label = tk.Label(self.image_metadata_line1_frame, bg="lightgray", fg="black", text="")
        self.asa_label.pack(side=tk.RIGHT, padx=10)
        self.image_metadata_line1_frame.pack(side=tk.TOP, fill=tk.X)
        self.image_metadata_line2_frame = tk.Frame(self.image_metadata_frame, bg="lightgray")
        self.location_label = tk.Label(self.image_metadata_line2_frame, bg="lightgray", fg="black", text="")
        self.location_label.pack(side=tk.LEFT, padx=10)
        self.roll_number_label = tk.Label(self.image_metadata_line2_frame, bg="lightgray", fg="black", text="")
        self.roll_number_label.pack(side=tk.RIGHT, padx=10)
        self.image_metadata_line2_frame.pack(side=tk.TOP, fill=tk.X)
        self.image_metadata_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Bottom frame to hold navigation buttons
        self.bottom_frame = tk.Frame(self.root, bg="lightgray", height=50)
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.setup_bottom_buttons()

    def setup_bottom_buttons(self):
        """Set up navigation buttons at the bottom of the window."""
        # Clear previous buttons if any
        for widget in self.bottom_frame.winfo_children():
            widget.destroy()

        # Navigation buttons: Backward, Forward, Home
        # Get the correct path to the image files, whether running in development or as a packaged app
        if getattr(sys, 'frozen', False):
            # Running in a bundled executable
            left_arrow_path = os.path.join(sys._MEIPASS, 'color_left.gif')
            home_image_path = os.path.join(sys._MEIPASS, 'home.gif')
            right_arrow_path = os.path.join(sys._MEIPASS, 'color_right.gif')
        else:
            # Running in a script (development mode)
            left_arrow_path = 'color_left.gif'
            home_image_path = 'home.gif'
            right_arrow_path = 'color_right.gif'

        left_arrow = PhotoImage(file=left_arrow_path)
        self.back_button = tk.Button(
            self.bottom_frame, image=left_arrow, command=self.show_previous_image
        )
        self.back_button.image = left_arrow  # Keep a reference to avoid garbage collection
        home_image = PhotoImage(file=home_image_path)
        self.home_button = tk.Button(
            self.bottom_frame, image=home_image, command=self.show_first_image
        )
        self.home_button.image = home_image  # Keep a reference to avoid garbage collection
        right_arrow = PhotoImage(file=right_arrow_path)
        self.forward_button = tk.Button(
            self.bottom_frame, image=right_arrow, command=self.show_next_image
        )
        self.forward_button.image = right_arrow  # Keep a reference to avoid garbage collection

        # Label for image number and total image count
        self.image_count_label = tk.Label(
            self.bottom_frame, text="Image 0 of 0", bg="lightgray", fg="black"
        )
        self.image_count_label.pack(side=tk.LEFT, padx=10)

        # Pack the buttons into the bottom frame
        self.forward_button.pack(side=tk.RIGHT, padx=5, pady=5)
        self.home_button.pack(side=tk.RIGHT, padx=5, pady=5)
        self.back_button.pack(side=tk.RIGHT, padx=5, pady=5)

    def retrieve_image_paths(self, collection_path):
        """ Read the collection information and return a list of immage information objects. """
        image_paths = []
        try:
            with open(self.collection_path, 'r', encoding="utf-8") as fp:
                xml_content = fp.read()
                root = ET.fromstring(xml_content)
                self.collection_name = root.find('title').text
                for image in root.findall('picture'):
                    image_info = ImageInfo(
                        image_path=collection_path / Path(image.find('image').text),
                        image_date=image.find('date').text,
                        image_location=image.find('location').text,
                        image_cpation=image.find('caption').text,
                        image_asa=image.find('asa').text if image.find('asa') is not None else None,
                        roll_number=image.find('roll_num').text if image.find('roll_num') is not None else None,
                        roll_max=image.find('roll_max').text if image.find('roll_max') is not None else None,
                    )
                    image_paths.append(image_info)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read collection: {e}")
        return image_paths

    def reset_collection(self):
        """Clear the image list and reset the display."""
        self.collection_images = []
        self.current_image_index = 0
        self.collection_path = ""
        self.collection_name = "Image Viewer"
        self.image_area.config(image="", text="No Image Loaded")
        self.image_count_label.config(text="Image 0 of 0")
        self.caption_text_label.config(text="")
        self.date_label.config(text="")
        self.asa_label.config(text="")
        self.location_label.config(text="")
        self.roll_number_label.config(text="")
        self.root.title(self.collection_name)
        messagebox.showinfo("Reset", "Image list cleared.")

    def open_collection(self):
        """Allow the user to open a collection of images."""
        self.collection_path = filedialog.askopenfilename(
            title="Select Image Collection",
            filetypes=[("Slides Show Collecction", "*.xml")],
        )
        if self.collection_path:
            # Add selected images to the list
            self.collection_images = self.retrieve_image_paths(Path(self.collection_path).parent)
            self.root.title(self.collection_name)
            self.current_image_index = 0
            self.show_image(self.current_image_index)

    def show_image(self, index):
        """Display an image at the given index."""
        if not self.collection_images:
            self.image_area.config(image="", text="No Image Loaded")
            return

        try:
            # Open the image and fit it within the available area
            image_path = self.collection_images[index].image_path
            image = Image.open(image_path)

            # Get the size of the image area
            area_width = self.image_area.winfo_width()
            area_height = self.image_area.winfo_height() - self.bottom_frame.winfo_height()

            # Resize the image to fit
            image.thumbnail((area_width, area_height))

            # Convert the image to a format tkinter can use
            self.current_image = ImageTk.PhotoImage(image)
            self.image_area.config(image=self.current_image, text="")

            # Get image metadata information
            self.caption_text_label.config(text=self.collection_images[index].image_cpation)
            self.date_label.config(text=self.collection_images[index].image_date)
            if self.collection_images[index].image_asa is not None:
                self.asa_label.config(text=f"ASA: {self.collection_images[index].image_asa}")
            else:
                self.asa_label.config(text="")
            self.location_label.config(text=self.collection_images[index].image_location)
            if self.collection_images[index].roll_number is not None:
                self.roll_number_label.config(text=f"{self.collection_images[index].roll_number} of {self.collection_images[index].roll_max}")
            else:
                self.roll_number_label.config(text="")

            # Display image metadata information

            # Update the image count label
            self.update_image_count_label()
        except Exception as e:
            # Show an error if the image fails to load
            messagebox.showerror("Error", f"Failed to load image {image_path}: {e}")

    def show_previous_image(self):
        """Display the previous image in the list."""
        if self.collection_images:
            self.current_image_index = (self.current_image_index - 1) % len(self.collection_images)
            self.show_image(self.current_image_index)

    def show_next_image(self):
        """Display the next image in the list."""
        if self.collection_images:
            self.current_image_index = (self.current_image_index + 1) % len(self.collection_images)
            self.show_image(self.current_image_index)

    def show_first_image(self):
        """Display the first image in the list."""
        if self.collection_images:
            self.current_image_index = 0
            self.show_image(self.current_image_index)

    def update_image_count_label(self):
        """Update the label showing the current image number and total count."""
        total_images = len(self.collection_images)
        current_image = self.current_image_index + 1  # User-friendly, starting at 1
        self.image_count_label.config(text=f"Image {current_image} of {total_images}")

    def start_slideshow(self):
        """Start the slideshow of images."""
        if self.collection_images:
            Slideshow(self.root, self.collection_images, self.collection_name)


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageViewerApp(root)
    root.mainloop()
