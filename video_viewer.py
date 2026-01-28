import base64
from dataclasses import dataclass
from io import BytesIO
import os
from pathlib import Path
import tkinter as tk
from tkinter import PhotoImage, filedialog, messagebox 
import sys
import xml.etree.ElementTree as ET

import cv2
from PIL import Image, ImageTk


@dataclass
class VideoInfo:
    def __init__(self, video_path, video_caption, video_date=None, video_location=None):
        self.video_path = video_path
        self.video_caption = video_caption
        self.video_date = video_date
        self.video_location = video_location


class VideoViewerApp:
    def __init__(self, root):
        self.root = root
        self.collection_name = "Video Viewer"
        self.root.title(self.collection_name)
        self.root.state("normal")  # Start window maximized
        self.root.minsize(1000, 800)  # Set minimum window size

        # Set the custom window icon
        self.set_window_icon()

        # Initialize image list and index
        self.video_capture = None
        self.running_video = False
        self.collection_path = ""
        self.collection_videos = []
        self.current_video_index = 0

        # UI Setup
        self.setup_menu()
        self.setup_layout()

        # Bind keyboard shortcuts for navigation
        self.root.bind("<Left>", lambda event: self.show_previous_video())  # Left arrow
        self.root.bind("<Right>", lambda event: self.show_next_video())  # Right arrow
        self.root.bind("<Escape>", lambda event: self.show_first_video())  # Right arrow

    def set_window_icon(self):
        """Set the window icon using an embedded base64 string."""
        icon_base64 = self.get_icon_data()  # Use the icon data from the method

        try:
            # Decode the base64 string to binary data
            icon_data = base64.b64decode(icon_base64)

            # Convert the binary data into an video object
            icon_video = Image.open(BytesIO(icon_data))
            icon_video = ImageTk.PhotoImage(icon_video)

            # Set the window icon
            self.root.iconphoto(True, icon_video)
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

        self.root.config(menu=self.menu_bar)

    def retrieve_collection(self):
        self.show_video(self.current_video_index)

    def setup_layout(self):
        """Set up the main layout of the application."""
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Label to display the current video
        self.video_area = tk.Label(
            self.main_frame, text="No video Loaded", bg="gray", fg="white"
        )
        self.video_area.pack(fill=tk.BOTH, expand=True)

        # Area for video metadata display
        self.video_metadata_frame = tk.Frame(self.main_frame, bg="lightgray", height=50)
        self.video_metadata_line1_frame = tk.Frame(self.video_metadata_frame, bg="lightgray")
        self.caption_text_label = tk.Label(self.video_metadata_line1_frame, bg="lightgray", fg="black", text="No video Information")
        self.caption_text_label.pack(side=tk.TOP, pady=10)
        self.date_label = tk.Label(self.video_metadata_line1_frame, bg="lightgray", fg="black", text="")
        self.date_label.pack(side=tk.LEFT, padx=10)
        self.location_label = tk.Label(self.video_metadata_line1_frame, bg="lightgray", fg="black", text="")
        self.location_label.pack(side=tk.RIGHT, padx=10)
        self.video_metadata_line1_frame.pack(side=tk.TOP, fill=tk.X)
        self.video_metadata_frame.pack(side=tk.BOTTOM, fill=tk.X)

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
        # Get the correct path to the video files, whether running in development or as a packaged app
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
            self.bottom_frame, image=left_arrow, command=self.show_previous_video
        )
        self.back_button.image = left_arrow  # Keep a reference to avoid garbage collection
        home_image = PhotoImage(file=home_image_path)
        self.home_button = tk.Button(
            self.bottom_frame, image=home_image, command=self.show_first_video
        )
        self.home_button.image = home_image  # Keep a reference to avoid garbage collection
        right_arrow = PhotoImage(file=right_arrow_path)
        self.forward_button = tk.Button(
            self.bottom_frame, image=right_arrow, command=self.show_next_video
        )
        self.forward_button.image = right_arrow  # Keep a reference to avoid garbage collection

        # Label for video number and total video count
        self.video_count_label = tk.Label(
            self.bottom_frame, text="video 0 of 0", bg="lightgray", fg="black"
        )
        self.video_count_label.pack(side=tk.LEFT, padx=10)

        # Pack the buttons into the bottom frame
        self.forward_button.pack(side=tk.RIGHT, padx=5, pady=5)
        self.home_button.pack(side=tk.RIGHT, padx=5, pady=5)
        self.back_button.pack(side=tk.RIGHT, padx=5, pady=5)

    def retrieve_video_paths(self, collection_path):
        """ Read the collection information and return a list of Video information objects. """
        video_paths = []
        try:
            with open(self.collection_path, 'r', encoding="utf-8") as fp:
                xml_content = fp.read()
                root = ET.fromstring(xml_content)
                self.collection_name = root.find('title').text
                for video in root.findall('video'):
                    video_info = VideoInfo(
                        video_path=collection_path / Path(video.find('source').text),
                        video_caption=video.find('caption').text,
                        video_date=video.find('date').text if video.find('date') is not None else None,
                        video_location=video.find('location').text if video.find('location') is not None else None,
                    )
                    video_paths.append(video_info)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read collection: {e}")
        return video_paths

    def reset_collection(self):
        """Clear the video list and reset the display."""
        if self.video_capture is not None:
            self.video_capture.release()
        self.collection_videos = []
        self.current_video_index = 0
        self.collection_path = ""
        self.collection_name = "video Viewer"
        self.video_area.config(image="", text="No video Loaded")
        self.video_count_label.config(text="video 0 of 0")
        self.caption_text_label.config(text="")
        self.date_label.config(text="")
        self.location_label.config(text="")
        self.root.title(self.collection_name)
        messagebox.showinfo("Reset", "video list cleared.")

    def open_collection(self):
        """Allow the user to open a collection of videos."""
        self.collection_path = filedialog.askopenfilename(
            title="Select Video Collection",
            filetypes=[("Video Show Collection", "*.xml")],
        )
        if self.collection_path:
            # Add selected videos to the list
            self.collection_videos = self.retrieve_video_paths(Path(self.collection_path).parent)
            self.root.title(self.collection_name)
            self.current_video_index = 0
            self.show_video(self.current_video_index)

    def show_video(self, index):
        """Display an video at the given index."""

        # --- Video Playback Function ---
        def update_frame():
            """Reads a new frame from the video and updates the Tkinter label."""

            # Read a frame
            have_frame, frame = self.video_capture.read()

            # Handle the frame
            if have_frame:
                # Convert the frame from BGR to RGB format (PIL/Tkinter requirement)
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_image = Image.fromarray(cv2image)

                # Get the size of the video area
                area_width = self.video_area.winfo_width()
                area_height = self.video_area.winfo_height() - self.bottom_frame.winfo_height()

                # Resize the video to fit
                frame_image.thumbnail((area_width, area_height))

                # Convert the PIL image to a Tkinter PhotoImage
                self.current_video = ImageTk.PhotoImage(image=frame_image)
                self.video_area.config(image=self.current_video, text="")

                # Call this function again after a small delay (e.g., 15 milliseconds)
                # to process the next frame and create a continuous loop
                if self.running_video:
                    self.root.after(5, update_frame)

            else:
                # Video ended. Release video and indicate done with this video
                self.video_capture.release()
                self.caption_text_label.config(text="Video playback ended.")
                self.date_label.config(text="")
                self.location_label.config(text="")

        if not self.collection_videos:
            self.video_area.config(image="", text="No Video Loaded")
            return

        try:

            self.running_video = True

            # Get and show video metadata information
            self.caption_text_label.config(text=self.collection_videos[index].video_caption)
            if self.collection_videos[index].video_date is not None:
                self.date_label.config(text=self.collection_videos[index].video_date)
            else:
                self.date_label.config(text="")
            if self.collection_videos[index].video_location is not None:
                self.location_label.config(text=self.collection_videos[index].video_location)
            else:
                self.location_label.config(text="")
            video_path = self.collection_videos[index].video_path

            # Update the video count label
            self.update_video_count_label()

            # Setup OpenCV and open the video
            self.video_capture = cv2.VideoCapture(video_path)

            if not self.video_capture.isOpened():
                raise Exception("Could not open video file.")

            # Start the frame update process
            update_frame()

        except Exception as e:
            # Show an error if the video fails to load
            messagebox.showerror("Error", f"Failed to load video {video_path}: {e}")

    def show_previous_video(self):
        """Display the previous video in the list."""
        # Trigger stopage of current video playback
        self.running_video = False

        if self.collection_videos:
            # Clean up current video capture
            if self.video_capture is not None:
                self.video_capture.release()

            self.current_video_index = (self.current_video_index - 1) % len(self.collection_videos)

            # Give some time for the cleanup before starting the next video
            self.root.after(15, self.show_video, self.current_video_index)

    def show_next_video(self):
        """Display the next video in the list."""
        # Trigger stopage of current video playback
        self.running_video = False

        if self.collection_videos:
            # Clean up current video capture
            if self.video_capture is not None:
                self.video_capture.release()

            self.current_video_index = (self.current_video_index + 1) % len(self.collection_videos)

            # Give some time for the cleanup before starting the next video
            self.root.after(15, self.show_video, self.current_video_index)

    def show_first_video(self):
        """Display the first video in the list."""
        # Trigger stopage of current video playback
        self.running_video = False

        if self.collection_videos:
            # Clean up current video capture
            if self.video_capture is not None:
                self.video_capture.release()

            self.current_video_index = 0

            # Give some time for the cleanup before starting the next video
            self.root.after(15, self.show_video, self.current_video_index)

    def update_video_count_label(self):
        """Update the label showing the current video number and total count."""
        total_videos = len(self.collection_videos)
        current_video = self.current_video_index + 1  # User-friendly, starting at 1
        self.video_count_label.config(text=f"video {current_video} of {total_videos}")


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoViewerApp(root)
    root.mainloop()
