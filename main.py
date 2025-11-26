import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import pygame
import os
import random
import json
import io
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from mutagen.wave import WAVE
from mutagen.oggvorbis import OggVorbis
import time
import threading
from PIL import Image, ImageTk

ctk.set_appearance_mode("Dark")

class VibeJoyApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("VibeJoy Media Player")
        self.geometry("1000x700")
        self.iconbitmap("icon.ico")

        # Initialize Pygame Mixer only
        pygame.mixer.init()

        # State Variables
        self.playlist = []
        self.current_track_index = -1
        self.paused = False
        self.shuffling = False
        self.repeating = False
        self.song_length = 0
        self.is_playing = False
        self.playlist_buttons = []
        
        # Time tracking
        self.start_time = 0
        self.current_pos = 0
        self.last_update_time = 0

        # Load Playlist
        self.load_playlist()

        # Layout Configuration
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create Widgets
        self.create_sidebar()
        self.create_main_area()
        self.create_controls()

        # Start Update Loop
        self.update_loop()

    def create_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color="#000000")
        self.sidebar_frame.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="VibeJoy", font=("Helvetica", 28, "bold"), text_color="#FFFFFF")
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.add_folder_btn = ctk.CTkButton(self.sidebar_frame, text="Add Folder", command=self.add_folder_to_playlist, fg_color="#1DB954", hover_color="#1ED760", text_color="#FFFFFF")
        self.add_folder_btn.grid(row=1, column=0, padx=20, pady=10)

        self.remove_btn = ctk.CTkButton(self.sidebar_frame, text="Remove Selected", command=self.remove_selected_track, fg_color="transparent", border_width=2, text_color="#B3B3B3", hover_color="#282828")
        self.remove_btn.grid(row=2, column=0, padx=20, pady=10)

        self.shuffle_btn = ctk.CTkButton(self.sidebar_frame, text="Shuffle: Off", command=self.toggle_shuffle, fg_color="transparent", border_width=2, text_color="#B3B3B3", hover_color="#282828")
        self.shuffle_btn.grid(row=3, column=0, padx=20, pady=10)
        
        self.repeat_btn = ctk.CTkButton(self.sidebar_frame, text="Repeat: Off", command=self.toggle_repeat, fg_color="transparent", border_width=2, text_color="#B3B3B3", hover_color="#282828")
        self.repeat_btn.grid(row=4, column=0, padx=20, pady=10)

        self.clear_playlist_btn = ctk.CTkButton(self.sidebar_frame, text="Clear Playlist", command=self.clear_playlist, fg_color="transparent", border_width=2, text_color="#B3B3B3", hover_color="#282828")
        self.clear_playlist_btn.grid(row=5, column=0, padx=20, pady=10)

        self.theme_switch = ctk.CTkSwitch(self.sidebar_frame, text="Dark Mode", command=self.toggle_theme, onvalue="on", offvalue="off", progress_color="#1DB954")
        self.theme_switch.select()
        self.theme_switch.grid(row=7, column=0, padx=20, pady=20)

    def create_main_area(self):
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#121212")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Album Cover
        self.album_cover_label = ctk.CTkLabel(self.main_frame, text="")
        self.album_cover_label.grid(row=0, column=0, pady=(0, 20))

        # Now Playing Info
        self.song_info_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.song_info_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        
        self.track_title_label = ctk.CTkLabel(self.song_info_frame, text="No Song Playing", font=("Helveticab", 32, "bold"), text_color="#FFFFFF")
        self.track_title_label.pack(anchor="w")
        
        self.track_artist_label = ctk.CTkLabel(self.song_info_frame, text="Unknown Artist", font=("Helvetica", 18), text_color="#B3B3B3")
        self.track_artist_label.pack(anchor="w")

        # Playlist List
        self.playlist_frame = ctk.CTkScrollableFrame(self.main_frame, label_text="Playlist", label_text_color="#FFFFFF", fg_color="#1E1E1E")
        self.playlist_frame.grid(row=2, column=0, sticky="nsew")
        
        self.update_playlist_display()

    def create_controls(self):
        self.controls_frame = ctk.CTkFrame(self, corner_radius=10, height=120, fg_color="#181818")
        self.controls_frame.grid(row=1, column=1, sticky="ew", padx=20, pady=20)
        self.controls_frame.grid_columnconfigure(1, weight=1)

        # Progress Bar
        self.progress_slider = ctk.CTkSlider(self.controls_frame, from_=0, to=100, command=self.seek_music, button_color="#1DB954", progress_color="#FFFFFF", button_hover_color="#1ED760")
        self.progress_slider.set(0)
        self.progress_slider.grid(row=0, column=0, columnspan=4, sticky="ew", padx=20, pady=(20, 10))

        self.time_label = ctk.CTkLabel(self.controls_frame, text="0:00 / 0:00", text_color="#B3B3B3")
        self.time_label.grid(row=0, column=4, padx=20, pady=(20, 10))

        # Buttons
        self.btn_frame = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        self.btn_frame.grid(row=1, column=0, columnspan=5, pady=10)

        self.prev_btn = ctk.CTkButton(self.btn_frame, text="⏮", width=50, height=40, command=self.prev_track, font=("Helvetica", 20), fg_color="transparent", text_color="#FFFFFF", hover_color="#282828")
        self.prev_btn.pack(side="left", padx=10)

        self.play_pause_btn = ctk.CTkButton(self.btn_frame, text="▶", width=60, height=50, command=self.play_pause_music, font=("Helvetica", 24, "bold"), fg_color="#1DB954", text_color="#FFFFFF", hover_color="#1ED760")
        self.play_pause_btn.pack(side="left", padx=10)

        self.next_btn = ctk.CTkButton(self.btn_frame, text="⏭", width=50, height=40, command=self.next_track, font=("Helvetica", 20), fg_color="transparent", text_color="#FFFFFF", hover_color="#282828")
        self.next_btn.pack(side="left", padx=10)

        # Volume
        self.volume_label = ctk.CTkLabel(self.btn_frame, text="🔊")
        self.volume_label.pack(side="left", padx=(30, 5))
        self.volume_slider = ctk.CTkSlider(self.btn_frame, from_=0, to=1, width=150, command=self.set_volume, button_color="#1DB954", progress_color="#FFFFFF", button_hover_color="#1ED760")
        self.volume_slider.set(0.5)
        self.volume_slider.pack(side="left", padx=5)

    def add_folder_to_playlist(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            for root, _, files in os.walk(folder_selected):
                for file in files:
                    if file.endswith((".mp3", ".wav", ".ogg")):
                        path = os.path.join(root, file)
                        if path not in self.playlist:
                            self.playlist.append(path)
            self.update_playlist_display()
            self.save_playlist()

    def update_playlist_display(self):
        # Clear existing buttons
        for btn in self.playlist_buttons:
            btn.destroy()
        self.playlist_buttons = []

        for i, track in enumerate(self.playlist):
            name = os.path.basename(track)
            btn = ctk.CTkButton(self.playlist_frame, text=f"{i+1}. {name}", anchor="w", 
                                command=lambda index=i: self.play_track_by_index(index),
                                fg_color="transparent", text_color="#FFFFFF", hover_color="#282828")
            btn.pack(fill="x", padx=5, pady=2)
            self.playlist_buttons.append(btn)
        
        self.highlight_current_track()

    def highlight_current_track(self):
        for i, btn in enumerate(self.playlist_buttons):
            if i == self.current_track_index:
                btn.configure(fg_color="#1DB954")
            else:
                btn.configure(fg_color="transparent")

    def play_track_by_index(self, index):
        self.current_track_index = index
        self.play_music()

    def play_music(self):
        if not self.playlist or self.current_track_index == -1:
            return

        track_path = self.playlist[self.current_track_index]
        
        if not os.path.exists(track_path):
            print(f"File not found: {track_path}")
            self.next_track()
            return
        
        try:
            pygame.mixer.music.load(track_path)
            pygame.mixer.music.play()
            self.is_playing = True
            self.paused = False
            self.current_pos = 0
            self.start_time = time.time()
            self.play_pause_btn.configure(text="⏸")
            self.highlight_current_track()
            self.update_metadata(track_path)
        except Exception as e:
            print(f"Error playing {track_path}: {e}")

    def play_pause_music(self):
        if not self.playlist:
            return
            
        if self.current_track_index == -1:
            self.current_track_index = 0
            self.play_music()
            return

        if self.paused:
            pygame.mixer.music.unpause()
            self.paused = False
            self.is_playing = True
            self.start_time = time.time() - self.current_pos
            self.play_pause_btn.configure(text="⏸")
        elif self.is_playing:
            pygame.mixer.music.pause()
            self.paused = True
            self.is_playing = False
            self.current_pos = time.time() - self.start_time
            self.play_pause_btn.configure(text="▶")
        else:
            self.play_music()

    def next_track(self):
        if not self.playlist:
            return
        
        if self.shuffling:
            self.current_track_index = random.randint(0, len(self.playlist) - 1)
        else:
            self.current_track_index = (self.current_track_index + 1) % len(self.playlist)
        self.play_music()

    def prev_track(self):
        if not self.playlist:
            return

        if pygame.mixer.music.get_pos() > 3000:
            self.play_music()
        elif self.shuffling:
            self.current_track_index = random.randint(0, len(self.playlist) - 1)
            self.play_music()
        else:
            self.current_track_index = (self.current_track_index - 1 + len(self.playlist)) % len(self.playlist)
            self.play_music()

    def toggle_shuffle(self):
        self.shuffling = not self.shuffling
        text = "Shuffle: On" if self.shuffling else "Shuffle: Off"
        self.shuffle_btn.configure(text=text, fg_color="#1f538d" if self.shuffling else "transparent")

    def toggle_repeat(self):
        self.repeating = not self.repeating
        text = "Repeat: On" if self.repeating else "Repeat: Off"
        self.repeat_btn.configure(text=text, fg_color="#1f538d" if self.repeating else "transparent")

    def toggle_theme(self):
        if self.theme_switch.get() == "on":
            ctk.set_appearance_mode("Dark")
            self.sidebar_frame.configure(fg_color="#000000")
            self.main_frame.configure(fg_color="#121212")
            self.controls_frame.configure(fg_color="#181818")
            self.track_title_label.configure(text_color="#FFFFFF")
            self.track_artist_label.configure(text_color="#B3B3B3")
            self.playlist_frame.configure(label_text_color="#FFFFFF", fg_color="#1E1E1E")
            self.time_label.configure(text_color="#B3B3B3")
            self.logo_label.configure(text_color="#FFFFFF")
            self.add_folder_btn.configure(text_color="#FFFFFF")
            self.remove_btn.configure(text_color="#B3B3B3")
            self.shuffle_btn.configure(text_color="#B3B3B3")
            self.repeat_btn.configure(text_color="#B3B3B3")
            self.clear_playlist_btn.configure(text_color="#B3B3B3")
            self.prev_btn.configure(text_color="#FFFFFF")
            self.play_pause_btn.configure(text_color="#FFFFFF")
            self.next_btn.configure(text_color="#FFFFFF")
            for btn in self.playlist_buttons:
                btn.configure(text_color="#FFFFFF")

        else:
            ctk.set_appearance_mode("Light")
            self.sidebar_frame.configure(fg_color="#F0F0F0")
            self.main_frame.configure(fg_color="#FFFFFF")
            self.controls_frame.configure(fg_color="#E0E0E0")
            self.track_title_label.configure(text_color="#000000")
            self.track_artist_label.configure(text_color="#333333")
            self.playlist_frame.configure(label_text_color="#000000", fg_color="#F5F5F5")
            self.time_label.configure(text_color="#333333")
            self.logo_label.configure(text_color="#000000")
            self.add_folder_btn.configure(text_color="#000000")
            self.remove_btn.configure(text_color="#333333")
            self.shuffle_btn.configure(text_color="#333333")
            self.repeat_btn.configure(text_color="#333333")
            self.clear_playlist_btn.configure(text_color="#333333")
            self.prev_btn.configure(text_color="#000000")
            self.play_pause_btn.configure(text_color="#000000")
            self.next_btn.configure(text_color="#000000")
            for btn in self.playlist_buttons:
                btn.configure(text_color="#000000")

    def set_volume(self, value):
        pygame.mixer.music.set_volume(float(value))

    def seek_music(self, value):
        if self.is_playing or self.paused:
            new_pos = float(value)
            try:
                pygame.mixer.music.play(start=new_pos)
                self.current_pos = new_pos
                self.start_time = time.time() - new_pos
                if self.paused:
                    pygame.mixer.music.pause()
            except Exception as e:
                print(f"Seek error: {e}")

    def update_metadata(self, path):
        try:
            audio = None
            image = None
            if path.endswith(".mp3"):
                audio = MP3(path, ID3=ID3)
                if 'APIC:' in audio.tags:
                    artwork = audio.tags['APIC:'].data
                    image = Image.open(io.BytesIO(artwork))
                
            elif path.endswith(".ogg"):
                audio = OggVorbis(path)
            elif path.endswith(".wav"):
                audio = WAVE(path)
            
            if image is None:
                image = Image.open("icon.png")

            image = image.resize((200, 200), Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            self.album_cover_label.configure(image=photo)
            self.album_cover_label.image = photo

            if audio:
                self.song_length = audio.info.length
                self.progress_slider.configure(to=self.song_length)
                
                # Extract tags
                title = os.path.basename(path)
                artist = "Unknown Artist"
                
                if path.endswith(".mp3") and audio.tags:
                    title = audio.tags.get('TIT2', [title])[0]
                    artist = audio.tags.get('TPE1', [artist])[0]
                
                self.track_title_label.configure(text=str(title))
                self.track_artist_label.configure(text=str(artist))
            else:
                self.song_length = 0
                self.track_title_label.configure(text=os.path.basename(path))
                self.track_artist_label.configure(text="Unknown Format")

        except Exception as e:
            print(f"Error reading metadata: {e}")
            self.song_length = 0
            self.track_title_label.configure(text=os.path.basename(path))

    def format_time(self, seconds):
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes}:{seconds:02d}"

    def update_loop(self):
        # Check for music end
        if self.is_playing and not pygame.mixer.music.get_busy():
            # Music stopped naturally (or error)
            # Check if we reached the end of the song approximately
            # Or just assume it ended if we didn't pause it.
            if not self.paused:
                 if self.repeating:
                     self.play_music()
                 else:
                     if self.current_track_index < len(self.playlist) - 1:
                         self.next_track()
                     else:
                         self.is_playing = False
                         self.play_pause_btn.configure(text="▶")
                         self.current_pos = 0
                         self.progress_slider.set(0)
                         self.time_label.configure(text=f"0:00 / {self.format_time(self.song_length)}")

        # Update Progress
        if self.is_playing and not self.paused:
            self.current_pos = time.time() - self.start_time
            if self.current_pos > self.song_length:
                self.current_pos = self.song_length
            
            self.progress_slider.set(self.current_pos)
            self.time_label.configure(text=f"{self.format_time(self.current_pos)} / {self.format_time(self.song_length)}")

        self.after(500, self.update_loop)

    def clear_playlist(self):
        self.playlist = []
        self.current_track_index = -1
        pygame.mixer.music.stop()
        self.is_playing = False
        self.paused = False
        self.track_title_label.configure(text="No Song Playing")
        self.track_artist_label.configure(text="Unknown Artist")
        self.time_label.configure(text="0:00 / 0:00")
        self.progress_slider.set(0)
        self.play_pause_btn.configure(text="▶")
        self.update_playlist_display()
        self.save_playlist()

    def remove_selected_track(self):
        if self.current_track_index != -1:
            del self.playlist[self.current_track_index]
            
            if not self.playlist:
                self.current_track_index = -1
                pygame.mixer.music.stop()
                self.is_playing = False
                self.paused = False
                self.track_title_label.configure(text="No Song Playing")
                self.track_artist_label.configure(text="Unknown Artist")
                self.time_label.configure(text="0:00 / 0:00")
                self.progress_slider.set(0)
                self.play_pause_btn.configure(text="▶")
            elif self.current_track_index >= len(self.playlist):
                self.current_track_index = 0
            
            self.update_playlist_display()
            self.save_playlist()
            
            if self.playlist:
                self.play_track_by_index(self.current_track_index)
            else:
                self.highlight_current_track()

    def save_playlist(self):
        with open("playlist.json", "w") as f:
            json.dump(self.playlist, f)

    def load_playlist(self):
        if os.path.exists("playlist.json"):
            with open("playlist.json", "r") as f:
                self.playlist = json.load(f)

if __name__ == "__main__":
    app = VibeJoyApp()
    app.mainloop()
