import tkinter as tk
from tkinter import filedialog, ttk
import pygame
import os
import random
import json
from tkinter import font
from PIL import Image, ImageTk
import io
import mutagen
from mutagen.id3 import ID3
from mutagen.mp3 import MP3


class VibeJoyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("VibeJoy Media Player")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        self.root.configure(bg="#0f0f0f")

        pygame.init()
        pygame.mixer.init()

        self.playlist = []
        self.current_track_index = -1
        self.paused = False
        self.shuffling = False
        self.repeating = False
        self.current_position = 0
        self.track_length = 0

        # Create custom fonts
        self.default_font = font.Font(family="Helvetica", size=10)
        self.title_font = font.Font(family="Helvetica", size=16, weight="bold")
        self.track_font = font.Font(family="Helvetica", size=11)
        self.button_font = font.Font(family="Helvetica", size=9)

        self.load_playlist()

        # Create the UI
        self.create_widgets()
        
        # Load initial playlist
        self.update_playlist_display()
        
        # Start the update loops
        self.check_music_end()
        self.update_progress()

    def create_widgets(self):
        # Create a main frame
        main_frame = tk.Frame(self.root, bg="#0f0f0f")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Header with title
        header_frame = tk.Frame(main_frame, bg="#0f0f0f")
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(header_frame, text="VIBEJOY MEDIA PLAYER", font=self.title_font, 
                              bg="#0f0f0f", fg="#4fc3f7")
        title_label.pack()

        # Content area with album art and playlist
        content_frame = tk.Frame(main_frame, bg="#0f0f0f")
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Left side - Album Art and Track Info
        left_frame = tk.Frame(content_frame, bg="#1a1a1a", relief=tk.FLAT, bd=0)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10), expand=True)
        
        # Album art display
        self.album_art_frame = tk.Frame(left_frame, bg="#252525", width=300, height=300)
        self.album_art_frame.pack(pady=10, padx=10, fill=tk.NONE, expand=False)
        self.album_art_frame.pack_propagate(False)
        
        self.album_art_label = tk.Label(self.album_art_frame, bg="#252525", text="No Album Art", fg="#888888")
        self.album_art_label.pack(expand=True)
        
        # Track info display
        self.track_info_frame = tk.Frame(left_frame, bg="#1a1a1a")
        self.track_info_frame.pack(fill=tk.X, padx=10, pady=(10, 0))
        
        self.track_title_label = tk.Label(self.track_info_frame, text="No track selected", 
                                         font=self.title_font, bg="#1a1a1a", fg="white", 
                                         wraplength=280, justify=tk.CENTER)
        self.track_title_label.pack(pady=(0, 5))
        
        self.track_artist_label = tk.Label(self.track_info_frame, text="", 
                                          font=self.default_font, bg="#1a1a1a", fg="#bbbbbb")
        self.track_artist_label.pack()
        
        # Progress bar
        progress_frame = tk.Frame(left_frame, bg="#1a1a1a")
        progress_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.progress_label_current = tk.Label(progress_frame, text="0:00", font=("Helvetica", 8), 
                                              bg="#1a1a1a", fg="#bbbbbb")
        self.progress_label_current.pack(side=tk.LEFT)
        
        self.progress_bar = ttk.Scale(progress_frame, from_=0, to=100, command=self.seek_music)
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.progress_label_total = tk.Label(progress_frame, text="0:00", font=("Helvetica", 8), 
                                            bg="#1a1a1a", fg="#bbbbbb")
        self.progress_label_total.pack(side=tk.RIGHT)
        
        # Right side - Playlist
        right_frame = tk.Frame(content_frame, bg="#1a1a1a", relief=tk.FLAT, bd=0)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Playlist header
        playlist_header = tk.Frame(right_frame, bg="#2d2d2d")
        playlist_header.pack(fill=tk.X, padx=1, pady=1)
        
        playlist_label = tk.Label(playlist_header, text="PLAYLIST", font=self.default_font,
                                 bg="#2d2d2d", fg="#bbbbbb")
        playlist_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Playlist listbox with scrollbar
        listbox_frame = tk.Frame(right_frame, bg="#252525")
        listbox_frame.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)
        
        self.playlist_listbox = tk.Listbox(
            listbox_frame, 
            bg="#252525", 
            fg="#ffffff", 
            selectbackground="#4fc3f7",
            selectforeground="#000000",
            highlightthickness=0,
            relief=tk.FLAT,
            font=self.track_font,
            bd=0,
            activestyle=tk.NONE
        )
        self.playlist_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.playlist_listbox.bind("<Double-Button-1>", self.play_selected_track)
        
        playlist_scrollbar = tk.Scrollbar(listbox_frame, bg="#2d2d2d", troughcolor="#3a3a3a", 
                                         activebackground="#4fc3f7", relief=tk.FLAT, bd=0)
        playlist_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.playlist_listbox.config(yscrollcommand=playlist_scrollbar.set)
        playlist_scrollbar.config(command=self.playlist_listbox.yview)
        
        # Control buttons
        control_frame = tk.Frame(main_frame, bg="#0f0f0f")
        control_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Top row - utility buttons
        top_button_frame = tk.Frame(control_frame, bg="#0f0f0f")
        top_button_frame.pack(pady=5)
        
        add_folder_button = tk.Button(top_button_frame, text="Add Folder", command=self.add_folder_to_playlist,
                                     bg="#3a3a3a", fg="white", relief=tk.FLAT, font=self.button_font,
                                     activebackground="#4fc3f7", activeforeground="black", 
                                     padx=10)
        add_folder_button.grid(row=0, column=0, padx=5)
        
        remove_button = tk.Button(top_button_frame, text="Remove Selected", command=self.remove_selected_tracks,
                                 bg="#3a3a3a", fg="white", relief=tk.FLAT, font=self.button_font,
                                 activebackground="#4fc3f7", activeforeground="black", 
                                 padx=10)
        remove_button.grid(row=0, column=1, padx=5)
        
        # Middle row - playback controls
        mid_button_frame = tk.Frame(control_frame, bg="#0f0f0f")
        mid_button_frame.pack(pady=10)
        
        prev_button = tk.Button(mid_button_frame, text="⏮", command=self.prev_track,
                               bg="#3a3a3a", fg="white", relief=tk.FLAT, font=("Helvetica", 14),
                               activebackground="#4fc3f7", activeforeground="black", width=3)
        prev_button.grid(row=0, column=0, padx=5)
        
        self.play_button = tk.Button(mid_button_frame, text="▶", command=self.play_music,
                                    bg="#4fc3f7", fg="black", relief=tk.FLAT, font=("Helvetica", 14),
                                    activebackground="#6bd1ff", activeforeground="black", width=3)
        self.play_button.grid(row=0, column=1, padx=5)
        
        self.pause_button = tk.Button(mid_button_frame, text="⏸", command=self.pause_music,
                                     bg="#3a3a3a", fg="white", relief=tk.FLAT, font=("Helvetica", 14),
                                     activebackground="#4fc3f7", activeforeground="black", width=3)
        self.pause_button.grid(row=0, column=2, padx=5)
        
        stop_button = tk.Button(mid_button_frame, text="⏹", command=self.stop_music,
                               bg="#3a3a3a", fg="white", relief=tk.FLAT, font=("Helvetica", 14),
                               activebackground="#4fc3f7", activeforeground="black", width=3)
        stop_button.grid(row=0, column=3, padx=5)
        
        next_button = tk.Button(mid_button_frame, text="⏭", command=self.next_track,
                               bg="#3a3a3a", fg="white", relief=tk.FLAT, font=("Helvetica", 14),
                               activebackground="#4fc3f7", activeforeground="black", width=3)
        next_button.grid(row=0, column=4, padx=5)
        
        # Bottom row - shuffle and repeat
        bottom_button_frame = tk.Frame(control_frame, bg="#0f0f0f")
        bottom_button_frame.pack(pady=5)
        
        self.shuffle_button = tk.Button(bottom_button_frame, text="🔀 Shuffle", command=self.toggle_shuffle,
                                       bg="#3a3a3a", fg="white", relief=tk.FLAT, font=self.button_font,
                                       activebackground="#4fc3f7", activeforeground="black",
                                       padx=10)
        self.shuffle_button.grid(row=0, column=0, padx=5)
        
        self.repeat_button = tk.Button(bottom_button_frame, text="🔁 Repeat", command=self.toggle_repeat,
                                      bg="#3a3a3a", fg="white", relief=tk.FLAT, font=self.button_font,
                                      activebackground="#4fc3f7", activeforeground="black",
                                      padx=10)
        self.repeat_button.grid(row=0, column=1, padx=5)
        
        # Volume control
        volume_frame = tk.Frame(control_frame, bg="#0f0f0f")
        volume_frame.pack(pady=10, fill=tk.X)
        
        volume_label = tk.Label(volume_frame, text="Volume:", font=self.default_font,
                               bg="#0f0f0f", fg="#bbbbbb")
        volume_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.volume_slider = tk.Scale(volume_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                                     command=self.set_volume, bg="#2d2d2d", fg="white",
                                     highlightthickness=0, relief=tk.FLAT, font=("Helvetica", 8),
                                     troughcolor="#3a3a3a", activebackground="#4fc3f7", 
                                     length=150)
        self.volume_slider.set(70)  # Default volume
        self.volume_slider.pack(side=tk.LEFT)
        
        # Status bar
        self.status_bar = tk.Label(self.root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W,
                                  bg="#2d2d2d", fg="#bbbbbb", font=("Helvetica", 8))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def add_folder_to_playlist(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            added_count = 0
            for root, _, files in os.walk(folder_selected):
                for file in files:
                    if file.endswith((".mp3", ".wav", ".ogg")):
                        path = os.path.join(root, file)
                        if path not in self.playlist:
                            self.playlist.append(path)
                            added_count += 1
            self.update_playlist_display()
            self.save_playlist()
            self.status_bar.config(text=f"Added {added_count} tracks from folder")

    def update_playlist_display(self):
        self.playlist_listbox.delete(0, tk.END)
        for i, track in enumerate(self.playlist):
            display_name = os.path.basename(track)
            # Truncate long names
            if len(display_name) > 50:
                display_name = display_name[:47] + "..."
            self.playlist_listbox.insert(tk.END, display_name)
        
        # Highlight currently playing track
        if 0 <= self.current_track_index < len(self.playlist):
            self.playlist_listbox.selection_clear(0, tk.END)
            self.playlist_listbox.selection_set(self.current_track_index)
            self.playlist_listbox.see(self.current_track_index)
            self.playlist_listbox.activate(self.current_track_index)

    def play_music(self):
        if not self.playlist:
            self.status_bar.config(text="Playlist is empty")
            return

        if self.paused:
            pygame.mixer.music.unpause()
            self.paused = False
            self.play_button.config(text="⏸")
            self.status_bar.config(text=f"Playing: {os.path.basename(self.playlist[self.current_track_index])}")
        else:
            if self.current_track_index == -1:
                self.current_track_index = 0
            
            track_path = self.playlist[self.current_track_index]
            try:
                pygame.mixer.music.load(track_path)
                pygame.mixer.music.play()
                self.update_playlist_display()
                pygame.mixer.music.set_endevent(pygame.USEREVENT)
                self.play_button.config(text="⏸")
                self.status_bar.config(text=f"Playing: {os.path.basename(track_path)}")
                self.update_track_info(track_path)
            except pygame.error as e:
                self.status_bar.config(text=f"Error playing file: {str(e)}")

    def update_track_info(self, track_path):
        # Update track info display
        try:
            audio_file = MP3(track_path, ID3=ID3)
            title = os.path.basename(track_path)
            artist = ""
            
            # Try to get title and artist from ID3 tags
            if "TIT2" in audio_file.tags:
                title = str(audio_file.tags["TIT2"])
            
            if "TPE1" in audio_file.tags:
                artist = str(audio_file.tags["TPE1"])
                
            self.track_title_label.config(text=title)
            self.track_artist_label.config(text=artist)
            
            # Update track length
            self.track_length = audio_file.info.length
            minutes = int(self.track_length // 60)
            seconds = int(self.track_length % 60)
            self.progress_label_total.config(text=f"{minutes}:{seconds:02d}")
            
            # Try to get album art
            self.load_album_art(audio_file)
            
        except Exception as e:
            # Fallback to filename if we can't read tags
            self.track_title_label.config(text=os.path.basename(track_path))
            self.track_artist_label.config(text="")
            self.progress_label_total.config(text="0:00")
            self.album_art_label.config(image="", text="No Album Art")

    def load_album_art(self, audio_file):
        try:
            # Clear previous album art
            self.album_art_label.config(image="", text="")
            
            # Try to extract album art from ID3 tags
            for tag in audio_file.tags.values():
                if isinstance(tag, mutagen.id3.APIC):
                    # Load the image data
                    image_data = tag.data
                    image = Image.open(io.BytesIO(image_data))
                    
                    # Resize image to fit the display area
                    image = image.resize((280, 280), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(image)
                    
                    # Update the label with the new image
                    self.album_art_label.config(image=photo)
                    self.album_art_label.image = photo  # Keep a reference
                    return
            
            # If no album art found, display placeholder text
            self.album_art_label.config(text="No Album Art")
            
        except Exception as e:
            self.album_art_label.config(text="No Album Art")

    def update_progress(self):
        if pygame.mixer.music.get_busy() or self.paused:
            if not self.paused:
                # Update the progress bar position
                self.current_position = pygame.mixer.music.get_pos() / 1000
                
                if self.track_length > 0:
                    progress_percent = (self.current_position / self.track_length) * 100
                    self.progress_bar.set(progress_percent)
                    
                    # Update current time label
                    minutes = int(self.current_position // 60)
                    seconds = int(self.current_position % 60)
                    self.progress_label_current.config(text=f"{minutes}:{seconds:02d}")
        
        # Schedule the next update
        self.root.after(1000, self.update_progress)

    def seek_music(self, value):
        if self.current_track_index >= 0 and self.track_length > 0:
            # Calculate the position in seconds
            seek_position = (float(value) / 100) * self.track_length
            
            # Update the current position display
            self.current_position = seek_position
            
            # Update the time label
            minutes = int(seek_position // 60)
            seconds = int(seek_position % 60)
            self.progress_label_current.config(text=f"{minutes}:{seconds:02d}")
            
            # Note: Direct seeking is not supported by pygame.mixer.music,
            # so we'll just update the display but not actually seek

    def check_music_end(self):
        for event in pygame.event.get():
            if event.type == pygame.USEREVENT:
                self.handle_end_event()
        self.root.after(100, self.check_music_end)

    def play_selected_track(self, event):
        selected_index = self.playlist_listbox.curselection()
        if selected_index:
            self.current_track_index = selected_index[0]
            self.play_music()

    def pause_music(self):
        if pygame.mixer.music.get_busy() and not self.paused:
            pygame.mixer.music.pause()
            self.paused = True
            self.play_button.config(text="▶")
            self.status_bar.config(text=f"Paused: {os.path.basename(self.playlist[self.current_track_index])}")
        elif self.paused:
            pygame.mixer.music.unpause()
            self.paused = False
            self.play_button.config(text="⏸")
            self.status_bar.config(text=f"Playing: {os.path.basename(self.playlist[self.current_track_index])}")

    def stop_music(self):
        pygame.mixer.music.stop()
        self.paused = False
        self.current_track_index = -1
        self.play_button.config(text="▶")
        self.update_playlist_display()
        self.status_bar.config(text="Playback stopped")
        self.progress_bar.set(0)
        self.progress_label_current.config(text="0:00")
        self.track_title_label.config(text="No track selected")
        self.track_artist_label.config(text="")
        self.album_art_label.config(image="", text="No Album Art")

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
        
        if self.shuffling:
            self.current_track_index = random.randint(0, len(self.playlist) - 1)
        else:
            self.current_track_index = (self.current_track_index - 1 + len(self.playlist)) % len(self.playlist)
        self.play_music()

    def toggle_shuffle(self):
        self.shuffling = not self.shuffling
        if self.shuffling:
            self.shuffle_button.config(bg="#4fc3f7", fg="black")  # Active color
            self.status_bar.config(text="Shuffle mode enabled")
        else:
            self.shuffle_button.config(bg="#3a3a3a", fg="white")  # Default color
            self.status_bar.config(text="Shuffle mode disabled")

    def toggle_repeat(self):
        self.repeating = not self.repeating
        if self.repeating:
            self.repeat_button.config(bg="#4fc3f7", fg="black")  # Active color
            self.status_bar.config(text="Repeat mode enabled")
        else:
            self.repeat_button.config(bg="#3a3a3a", fg="white")  # Default color
            self.status_bar.config(text="Repeat mode disabled")

    def set_volume(self, volume):
        pygame.mixer.music.set_volume(float(volume) / 100)

    def handle_end_event(self):
        if self.repeating:
            self.play_music()  # Replay current track
        else:
            if self.current_track_index < len(self.playlist) - 1:
                self.next_track()
            else:
                self.stop_music()  # Stop if it's the last track and not repeating

    def remove_selected_tracks(self):
        selected_indices = self.playlist_listbox.curselection()
        if not selected_indices:
            self.status_bar.config(text="No tracks selected for removal")
            return

        # Convert to a list and sort in descending order to avoid index issues
        sorted_indices = sorted(list(selected_indices), reverse=True)
        removed_count = 0

        for index in sorted_indices:
            if 0 <= index < len(self.playlist):
                del self.playlist[index]
                removed_count += 1

        self.update_playlist_display()
        self.save_playlist()
        self.status_bar.config(text=f"Removed {removed_count} track(s)")

        # Reset current_track_index if the currently playing song was removed
        if self.current_track_index not in range(len(self.playlist)):
            self.current_track_index = -1
            pygame.mixer.music.stop()
            self.play_button.config(text="▶")
            self.stop_music()

    def save_playlist(self):
        try:
            with open("playlist.json", "w") as f:
                json.dump(self.playlist, f)
        except Exception as e:
            self.status_bar.config(text=f"Error saving playlist: {str(e)}")

    def load_playlist(self):
        if os.path.exists("playlist.json"):
            try:
                with open("playlist.json", "r") as f:
                    self.playlist = json.load(f)
            except Exception as e:
                self.status_bar.config(text=f"Error loading playlist: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = VibeJoyApp(root)
    root.mainloop()