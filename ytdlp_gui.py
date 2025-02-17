import os
import yt_dlp
import tkinter as tk
from tkinter import filedialog
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
from kivy.core.window import Window
import threading


class YTDLApp(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "YTDL GUI by Adamant"
        Window.size = (400, 690)
        self.last_download_percent = None
        self.downloading = False
        self.is_merging = False
        self.selected_format = "mp4"

    def build(self):
        layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

        self.url_input = TextInput(hint_text="Enter video URL", multiline=False, size_hint=(1, None), height=30)
        layout.add_widget(self.url_input)

        self.check_button = Button(text="Get available quatities", size_hint=(1, None), height=50)
        self.check_button.bind(on_press=self.on_button_press(self.start_check_link_thread))
        layout.add_widget(self.check_button)

        self.quality_spinner = Spinner(values=[], text="Select Quality", size_hint=(1, None), height=50)
        layout.add_widget(self.quality_spinner)

        self.folder_input = TextInput(hint_text="D:/downloads/videos (sample)", multiline=False, size_hint=(1, None), height=30)
        layout.add_widget(self.folder_input)

        self.folder_button = Button(text="Choose Folder", size_hint=(1, None), height=50)
        self.folder_button.bind(on_press=self.on_button_press(self.choose_folder))
        layout.add_widget(self.folder_button)

        self.format_spinner = Spinner(
            values=["mp4", "mkv"],
            text="Select Format (default: mp4)",
            size_hint=(1, None),
            height=50
        )
        layout.add_widget(self.format_spinner)

        self.filename_input = TextInput(hint_text="File name (optional)", multiline=False, size_hint=(1, None), height=30)
        layout.add_widget(self.filename_input)

        self.download_button = Button(text="Download", size_hint=(1, None), height=50)
        self.download_button.bind(on_press=self.on_button_press(self.start_download_thread))
        layout.add_widget(self.download_button)

        self.log_output = TextInput(hint_text="Logs...", multiline=True, readonly=True, size_hint=(1, 0.5))
        layout.add_widget(self.log_output)

        self.show_instructions()

        return layout

    def on_button_press(self, func):
        def wrapper(instance):
            original_color = instance.background_color
            instance.background_color = (0.5, 0.5, 0.5, 1)
            Clock.schedule_once(lambda dt: setattr(instance, 'background_color', original_color), 0.1)
            func(instance)
        return wrapper

    def log(self, message):
        def update_log(*args):
            self.log_output.text += message + '\n'
            self.log_output.cursor = (0, len(self.log_output.text))
        Clock.schedule_once(update_log)

    def choose_folder(self, instance):
        root = tk.Tk()
        root.withdraw()
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_input.text = folder_selected

    def start_check_link_thread(self, instance):
        threading.Thread(target=self.check_link, daemon=True).start()

    def check_link(self):
        url = self.url_input.text.strip()
        if not url:
            self.log("Error: Please enter a video URL!")
            return

        try:
            self.log("Checking available qualities...")

            with yt_dlp.YoutubeDL() as ydl:
                info = ydl.extract_info(url, download=False)

            formats = [
                f"{fmt['format_id']} - {fmt.get('resolution', 'audio only')} ({fmt.get('format_note', 'Unknown')})"
                for fmt in info.get("formats", []) if fmt.get("format_id")
            ]

            self.log(f"Found {len(formats)} formats.")
            Clock.schedule_once(lambda dt: self.update_spinner(formats))

            self.log(f"Title: {info['title']}")
            self.log("Available qualities loaded.")
        except Exception as e:
            self.log(f"Error: {e}")

    def update_spinner(self, formats):
        self.quality_spinner.values = formats
        self.quality_spinner.text = formats[0] if formats else ""

    def start_download_thread(self, instance):
        threading.Thread(target=self.download_video, daemon=True).start()

    def download_video(self):
        url = self.url_input.text.strip()
        quality = self.quality_spinner.text.strip()
        folder = self.folder_input.text.strip()
        filename = self.filename_input.text.strip()
        selected_format = self.format_spinner.text.strip()

        if not url:
            self.log("Error: No video URL provided.")
            return
        if not folder:
            self.log("Error: No folder selected for saving.")
            return
        if not quality:
            self.log("Error: No video quality selected.")
            return
        if selected_format == "Select Format (default: mp4)" or not selected_format:
            selected_format = "mp4"

        output_folder = os.path.abspath(folder)
        format_code = quality.split(" - ")[0]
        output_filename = filename if filename else "%(title)s"

        options = {
            "format": f"{format_code}+bestaudio",
            "merge_output_format": selected_format,
            "outtmpl": os.path.join(output_folder, f"{output_filename}.%(ext)s"),
            "postprocessors": [{"key": "FFmpegVideoConvertor", "preferedformat": selected_format}],
            "progress_hooks": [self.ytdl_hook],
        }

        try:
            self.log(f"Starting download ({quality}) in {selected_format} format...")
            with yt_dlp.YoutubeDL(options) as ydl:
                ydl.download([url])
            self.log("Download and merging completed!")
        except Exception as e:
            self.log(f"Error during download: {e}")

    def ytdl_hook(self, d):
        if d['status'] == 'downloading':
            percent = d['_percent_str']
            speed = d['_speed_str']

            if percent != self.last_download_percent:
                self.last_download_percent = percent
                if not self.is_merging:
                    self.log(f"Downloading: {percent} at {speed}")

        elif d['status'] == 'finished':
            if not self.is_merging:
                self.is_merging = True
                self.log("Download complete, merging files...")

        elif d['status'] == 'postprocessing':
            if self.is_merging:
                self.log("Merging formats...")
                self.is_merging = False

    def show_instructions(self):
        instructions = (
            "Welcome to YTDL GUI!\n\n"
            "Steps to use:\n"
            "1. Enter the video URL in the 'Enter video URL' field.\n"
            "2. Press 'Get available quatities' to fetch video.\n"
            "3. Select the desired video quality from the dropdown.\n"
            "4. Choose the folder to save the video.\n"
            "5. Select the output format (mp4, mkv).\n"
            "6. Optionally, enter a custom filename.\n"
            "7. Press 'Download' to start the video download.\n\n"
            "Enjoy downloading your videos!"
        )
        self.log(instructions)


if __name__ == "__main__":
    YTDLApp().run()
