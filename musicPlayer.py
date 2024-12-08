import pygame
import customtkinter as ctk
from tkinter import filedialog
import os
import mutagen
import time
import mutagen.mp3
import random
from PIL import Image
import re
from customtkinter import CTkImage
from LyricsFetcher import LyricsFetcher


class MusicPlayer:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("Music Player")
        self.window.geometry("820x600")  
        
        # Initialize pygame mixer
        pygame.mixer.init()
        
        ctk.set_default_color_theme("green")

        self.elapsedTime = 0 
        self.pauseTime = 0

        self.deleteIcon = ctk.CTkImage(
                Image.open("assets/delete.png").resize((20, 20), Image.LANCZOS)
            )
        self.searchIcon = CTkImage(
                Image.open("assets/search.png").resize((20, 20), Image.LANCZOS)
            )
        self.volumeIcon = CTkImage(
            Image.open("assets/volume.png").resize((20, 20), Image.LANCZOS)
        )
        self.muteIcon = CTkImage(
            Image.open("assets/mute.png").resize((20, 20), Image.LANCZOS)
        )
        # main container frame
        self.container = ctk.CTkFrame(self.window, fg_color="transparent")
        self.container.pack(expand=True, fill='both', padx=20, pady=20)
        
        # sidebar frame
        self.sidebar = ctk.CTkFrame(self.container, width=200)
        self.sidebar.pack(side="left", fill="y", padx=(0, 20))
        
        # Sidebar title
        self.sidebarTitle = ctk.CTkLabel(
            self.sidebar,
            text = "Playlist",
            font = ctk.CTkFont(size=20, weight="bold")
        )
        self.sidebarTitle.pack(pady=20)

        # frame for the search bar
        self.searchFrame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.searchFrame.pack(pady=10, padx=10, fill="x")  

        # Add search icon label
        self.searchIconLabel = ctk.CTkLabel(
            self.searchFrame,
            image  = self.searchIcon,
            fg_color = "transparent",
            text = "",  
            font = ctk.CTkFont(size=14)  
        )
        self.searchIconLabel.pack(side="left", padx=(10, 5)) 

        # search entry
        self.searchVar = ctk.StringVar()
        self.searchVar.trace_add("write", self.filterPlaylist)
        
        self.searchEntry = ctk.CTkEntry(
            self.searchFrame,
            textvariable = self.searchVar,
            height = 32,
            font = ctk.CTkFont(size=13),
            border_color = "gray", 
            border_width = 1,  
            corner_radius = 8  
        )
        self.searchEntry.pack(fill="x", padx=(0, 10), pady=5)  # Add padding around the entry

        # scrollable frame for songs
        self.playlistFrame = ctk.CTkScrollableFrame(
            self.sidebar,
            width = 250,
            height = 400
        )
        self.playlistFrame.pack(fill = "both", expand = True, padx = 10, pady = 10)

        # Initialize songFrames to store references to song frames for filtering
        self.songFrames = []  # Add this line to initialize songFrames

        # Create a label for the placeholder message
        self.placeholderLabel = ctk.CTkLabel(
            self.playlistFrame,
            text = "Your playlist is empty",
            font = ctk.CTkFont(size=14),  
            text_color = "gray",
            width = 200,  
            anchor = "center"  
        )
        self.placeholderLabel.pack(pady=20)  
        
        # Store playlist songs
        self.playlist = []
        self.updatePlaceholder()  
        
        # Main content frame (for existing controls)
        self.mainContent = ctk.CTkFrame(self.container, fg_color="transparent")
        self.mainContent.pack(side="left", fill="both", expand=True)
        
        # Title label with larger font
        self.titleLabel = ctk.CTkLabel(
            self.mainContent, 
            text = "Music Player",
            font = ctk.CTkFont(size = 32, weight = "bold")
        )
        self.titleLabel.pack(pady = 30)
        
        #Song button 
        self.selectBtn = ctk.CTkButton(
            self.window,
            text = "+ Add Song",
            width = 100,
            height = 30,
            font = ctk.CTkFont(size=16),
            corner_radius = 16,
            command = self.selectSong,
        )
        self.selectBtn.place(relx = 0.97, rely = 0.02, anchor = "ne")
        
        #frame for the song info and progress
        self.songFrame = ctk.CTkFrame(self.mainContent, fg_color="transparent")
        self.songFrame.pack(fill = "x", pady = (20, 0))
        
        # Current song label
        self.currentSongLabel = ctk.CTkLabel(
            self.songFrame,
            text = "No song selected",
            font = ctk.CTkFont(size=14),
            text_color = "gray"
        )
        self.currentSongLabel.pack(pady = (0, 5))

        self.navControls = ctk.CTkFrame(self.mainContent, fg_color = "transparent")
        self.navControls.pack(fill = "x", pady = 10)

        self.navControls.grid_columnconfigure(0, weight=1)  
        self.navControls.grid_columnconfigure(6, weight=1)  

        # Shuffle button
        self.shuffleBtn = ctk.CTkButton(
            self.navControls,
            text = "Shuffle Off",
            width = 80,
            height = 40,
            font = ctk.CTkFont(size=16),
            command = self.toggleShuffle,
            fg_color = "gray"
        )
        self.shuffleBtn.grid(row = 0, column = 1, padx = 5)

        # Repeat button
        self.repeatBtn = ctk.CTkButton(
            self.navControls,
            text = "Repeat Off",
            width = 80,
            height = 40,
            font = ctk.CTkFont(size = 16),
            fg_color = "gray",
            command=self.toggleRepeat,
        )
        self.repeatBtn.grid(row = 0, column = 5, padx = 5)

        # Previous button
        self.prevButton = ctk.CTkButton(
            self.navControls,
            text = "⏮",
            width = 80,
            height = 40,
            font = ctk.CTkFont(size=16),
            command = self.playPrevious,
        )
        self.prevButton.grid(row = 0, column = 2, padx = 5)

        # Play/Pause button
        self.playPauseButton = ctk.CTkButton(
            self.navControls,
            text = "▶",
            width = 80,
            height = 40,
            font = ctk.CTkFont(size = 16),
            command = self.togglePlayPause,
        )
        self.playPauseButton.grid(row = 0, column = 3, padx = 5)

        # Next button
        self.nextButton = ctk.CTkButton(
            self.navControls,
            text = "⏭",
            width = 80,
            height = 40,
            font = ctk.CTkFont(size = 16),
            command = self.playNext,
        )
        self.nextButton.grid(row = 0, column = 4, padx = 5)
            
        # Volume controls
        self.volumeFrame = ctk.CTkFrame(self.mainContent, fg_color = "transparent")
        self.volumeFrame.pack(fill = "x", pady = (10, 0))

        # Volume label
        self.volumeLabel = ctk.CTkButton(
            self.volumeFrame, 
            image = self.volumeIcon,  
            width = 30,
            fg_color = "transparent",
            height = 30,
            text = "",
            command=self.toggleMute  # Call toggleMute on click
        )
        self.volumeLabel.pack(side = "left", padx = 0)

        # Volume slider
        self.volumeSlider = ctk.CTkSlider(
            self.volumeFrame,
            from_= 0,
            to = 1,
            number_of_steps = 10,
            command=self.setVolume
        )
        self.volumeSlider.set(1)
        self.volumeSlider.pack(side="left", fill="x", padx=(0, 0))

        self.volume = 1  # Default volume
        
        #  progress bar with determinate mode
        self.progressBar = ctk.CTkProgressBar(self.songFrame)
        self.progressBar.pack(fill = "x", pady = (0, 0))
        self.progressBar.configure(mode="determinate")
        self.progressBar.set(0)
        
        # Time labels
        self.timeFrame = ctk.CTkFrame(self.songFrame, fg_color="transparent")
        self.timeFrame.pack(fill = "x", pady = (0, 0))
        self.currentTime = ctk.CTkLabel(self.timeFrame, text= "0:00")
        self.currentTime.pack(side="left")
        self.totalTime = ctk.CTkLabel(self.timeFrame, text= "0:00")
        self.totalTime.pack(side="right")
        
        # current song index and state variables
        self.songLength = 0
        self.startTime = 0
        self.updateId = None
        self.currentSongIndex = -1
        self.currentSong = None
        self.paused = False
        self.repeat = False
        self.shuffle = False
        self.is_muted = False  

        # Bind mouse click on progress bar to seek functionality
        self.progressBar.bind("<Button-1>", self.seekSong)

        self.lyricsFrame = ctk.CTkFrame(self.mainContent, fg_color="#2E2E2E", border_color="lightgray", border_width=2)
        self.lyricsFrame.pack_forget() 

        # scrollable frame for the lyrics
        self.lyricsScrollableFrame = ctk.CTkScrollableFrame(self.lyricsFrame, fg_color="#2E2E2E")
        self.lyricsScrollableFrame.pack(fill="both", expand=True, padx=0, pady=0) 

        # label to display the lyrics
        self.lyricsLabel = ctk.CTkLabel(
            self.lyricsScrollableFrame,
            text = "",
            font = ctk.CTkFont(size=14),
            text_color = "white",
            justify = "left",  
            anchor = "w"
        )
        self.lyricsLabel.pack(pady=0, fill="x")

        self.toggleLyricsButton = ctk.CTkButton(
            self.mainContent,
            text = "Show Lyrics",
            command = self.toggleLyrics,
            corner_radius = 8,
        )
        self.toggleLyricsButton.pack(pady=(20, 0))


    def addToPlaylist(self, songPath):
        """Add a song to the playlist"""
        if songPath not in self.playlist:
            self.playlist.append(songPath)
            songName = os.path.splitext(os.path.basename(songPath))[0]  # Remove .mp3 extension
            
            # Create frame for song item
            songFrame = ctk.CTkFrame(self.playlistFrame, fg_color="transparent")
            songFrame.pack(fill="x", pady=2)
            songFrame.songPath = songPath  # Store the songPath in the frame
            self.songFrames.append(songFrame)  # Store reference to the song frame

            #play button
            playBtn = ctk.CTkButton(
                songFrame,
                text = "▶",
                width = 30,
                height = 24,
                command = lambda s = songPath: self.playSelectedSong(s)
            )
            playBtn.pack(side = "left", padx = (0, 5))

            # song label
            songLabel = ctk.CTkLabel(
                songFrame,
                text=(songName if len(songName) <= 25 else songName[:22] + '...'),
                anchor="w"
            )
            songLabel.pack(side="left", fill="x", expand=True)

            # delete button
            deleteBtn = ctk.CTkButton(
                songFrame,
                image = self.deleteIcon,  
                text = "",  
                width = 30,
                fg_color = "transparent",
                height = 30,
                command = lambda s = songPath, f = songFrame: self.deleteSong(s, f)
            )
            deleteBtn.pack(side = "right", padx = (5, 0))

            self.updatePlaceholder()

    def filterPlaylist(self, *args):
        """Filter playlist based on search text."""
        search_text = self.searchVar.get().lower()
        # Hide all frames first
        for frame in self.songFrames:
            frame.pack_forget()

        # Show matching frames
        matches_found = False
        for frame in self.songFrames:
            song_name = os.path.basename(frame.songPath).lower()  # Ensure songPath is accessed correctly
            if search_text == "" or re.search(search_text, song_name):
                frame.pack(fill="x", pady=2)
                matches_found = True

        if not self.songFrames:  # If no songs at all
            self.placeholderLabel.configure(text="Your playlist is empty")
            self.placeholderLabel.pack(pady=20)
        elif not matches_found:  # If no matches found
            self.placeholderLabel.configure(text="No matching songs found")
            self.placeholderLabel.pack(pady=20)
        else:  # Matches found
            self.placeholderLabel.pack_forget()


    def deleteSong(self, songPath, songFrame):
        """Remove a song from the playlist and delete its frame"""
        if songPath in self.playlist:
            self.playlist.remove(songPath)
            songFrame.destroy()  # Remove the UI element from the playlist
            
            # Check if the deleted song is currently playing
            if songPath == self.currentSong:
                pygame.mixer.music.stop()  # Stop playback
                self.currentSongLabel.configure(text="No song playing", text_color="gray")
                self.playPauseButton.configure(text="▶")
                self.progressBar.set(0)
                self.currentTime.configure(text="0:00")
                self.totalTime.configure(text="0:00")
                self.currentSong = None
                self.currentSongIndex = -1
                # Clear the lyrics display
                self.lyricsLabel.configure(text="No lyrics available.")  # Reset lyrics display
                self.lyricsFrame.pack_forget()  # Hide the lyrics frame if it was visible
                self.toggleLyricsButton.configure(text="Show Lyrics")  # Reset button text
        
        self.updatePlaceholder()


    def updatePlaceholder(self):
        """Update the visibility of the placeholder label."""
        if not self.playlist:  # If playlist is empty
            self.placeholderLabel.pack(pady = 20)  # Show the placeholder
        else:
            self.placeholderLabel.pack_forget()  # Hide the placeholder

    def playSelectedSong(self, songPath):
        """Play a song and update the current song index"""
        try:
            # Stop any currently playing song and clear updates
            pygame.mixer.music.stop()
            if self.updateId:
                self.window.after_cancel(self.updateId)
            
            # Load and play the new song
            self.currentSong = songPath
            self.currentSongIndex = self.playlist.index(songPath)

            # Hide the lyrics frame when the song changes
            self.lyricsFrame.pack_forget()  # Hide the lyrics frame
            self.toggleLyricsButton.configure(text="Show Lyrics") 
            
            # Get song length
            audio = mutagen.File(songPath)
            if audio is None:
                audio = mutagen.mp3.MP3(songPath)
            self.songLength = audio.info.length
            
            # Update display
            pygame.mixer.music.load(songPath)
            pygame.mixer.music.play()

            self.startTime = time.time()
            self.paused = False
            
            # Update labels
            songName = os.path.splitext(os.path.basename(songPath))[0]
            self.currentSongLabel.configure(
                text = f"Now Playing: {songName}",
                text_color = "green"
            )
            self.totalTime.configure(text = self.formatTime(self.songLength))
            self.playPauseButton.configure(text = "⏸")
            
            # Start progress updates
            self.updateProgress()
            
            self.scrapeLyrics(songName)
            
        except Exception as e:
            print(f"Error playing file: {e}")

    def updateProgress(self):
        """Update progress bar and time labels"""
        if pygame.mixer.music.get_busy() and not self.paused:
            # Calculate current position
            elapsed = time.time() - self.startTime
            if elapsed > self.songLength:
                elapsed = self.songLength
            
            # Update progress bar (0 to 1)
            progress = elapsed / self.songLength if self.songLength > 0 else 0
            progress = max(0, min(1, progress))
            self.progressBar.set(progress)
            
            # Update time label with actual elapsed time
            self.currentTime.configure(text = self.formatTime(elapsed))
            
            # Schedule next update
            self.updateId = self.window.after(100, self.updateProgress)
        else:
            # Check if song has ended
            if not self.paused and self.currentSong:
                self.playNext()  # Automatically play next song
            else:
                # When paused, show the last known elapsed time
                self.currentTime.configure(text = self.formatTime(self.elapsedTime))

    def togglePlayPause(self):
        """Toggle between play and pause"""
        current_time = time.time()
        
        if self.paused:
            # Unpause: adjust startTime to account for pause duration
            pause_duration = current_time - self.pauseTime
            self.startTime += pause_duration
            
            pygame.mixer.music.unpause()
            self.paused = False
            self.playPauseButton.configure(text="⏸")
            
            # Restore original "Now Playing" label
            if self.currentSong:
                songName = os.path.basename(self.currentSong)
                self.currentSongLabel.configure(
                    text = f"Now Playing: {songName}",
                    text_color = "green"
                )
            
            # Resume progress updates
            self.updateProgress()
        else:
            # Pause: calculate and store elapsed time
            self.elapsedTime = current_time - self.startTime
            self.pauseTime = current_time
            
            pygame.mixer.music.pause()
            self.paused = True
            self.playPauseButton.configure(text="▶")
            
            # Update the display
            if self.currentSong:
                songName = os.path.basename(self.currentSong)
                self.currentSongLabel.configure(
                    text = f"Paused: {songName}",
                    text_color="gray"
                )

    def formatTime(self, seconds):
        """Convert seconds to MM:SS format"""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes}:{seconds:02d}"
    
    def selectSong(self):
        """Select a song and add it to the playlist"""
        songPath = filedialog.askopenfilename(
            filetypes = [("Audio Files", "*.mp3 *.wav")]
        )
        if songPath:
            self.addToPlaylist(songPath)
            songName = os.path.basename(songPath)
            self.currentSongLabel.configure(text=f"Current Song: {songName}")

    def seekSong(self, event):
        """Seek the song to a specific position based on click on progress bar"""
        if self.songLength == 0:
            return
        
        # Get the position where the user clicked
        progressWidth = self.progressBar.winfo_width()
        clickX = event.x
        newPosition = (clickX / progressWidth) * self.songLength
        
        # Update playback position
        pygame.mixer.music.set_pos(newPosition)
        self.startTime = time.time() - newPosition  # Adjust the start time for progress tracking
        
        # Update progress display
        self.updateProgress()

    def toggleRepeat(self):
        """Toggle repeat mode"""
        self.repeat = not self.repeat
        if self.repeat:
            self.repeatBtn.configure(text = "Repeat On", fg_color = "#2FA571")
        else:
            self.repeatBtn.configure(text = "Repeat Off", fg_color = "gray")

    def toggleShuffle(self):
        """Toggle shuffle mode"""
        self.shuffle = not self.shuffle
        if self.shuffle:
            self.shuffleBtn.configure(text = "Shuffle On", fg_color = "#2FA571")
        else:
            self.shuffleBtn.configure(text = "Shuffle Off", fg_color = "gray")

    def playNext(self):
        """Play the next song or stop if playlist is finished"""
        if not self.playlist:
            # Stop playback completely when playlist is empty
            pygame.mixer.music.stop()
            self.currentSongLabel.configure(
                text = "No song playing", 
                text_color = "gray"
            )
            self.playPauseButton.configure(text = "▶")
            self.progressBar.set(0)
            self.currentTime.configure(text = "0:00")
            self.totalTime.configure(text = "0:00")
            self.currentSong = None
            self.currentSongIndex = -1
            return

        # Handle repeat mode first
        if self.repeat and self.currentSong:
            # If repeat is on and a song is currently playing, repeat the current song
            self.playSelectedSong(self.currentSong)
            return

        # Handle shuffle mode
        if self.shuffle:
            # Play a random song from the playlist
            self.currentSongIndex = random.randint(0, len(self.playlist) - 1)
        else:
            # Play the next song in order
            self.currentSongIndex += 1

            # Stop if we've reached the end of the playlist
            if self.currentSongIndex >= len(self.playlist):
                pygame.mixer.music.stop()
                self.currentSongLabel.configure(
                    text = "Playlist finished", 
                    text_color = "gray"
                )
                self.playPauseButton.configure(text = "▶")
                self.progressBar.set(0)
                self.currentTime.configure(text = "0:00")
                self.totalTime.configure(text = "0:00")
                self.currentSong = None
                self.currentSongIndex = -1
                return

        # Play the next song
        nextSong = self.playlist[self.currentSongIndex]
        self.playSelectedSong(nextSong)

    def playPrevious(self):
        """Play the previous song in the playlist"""
        if not self.playlist:
            return
        
        if self.currentSongIndex > 0:
            self.currentSongIndex -= 1
        else:
            self.currentSongIndex = len(self.playlist) - 1  # Loop to last song
        
        prevSong = self.playlist[self.currentSongIndex]
        self.playSelectedSong(prevSong)

    def setVolume(self, volume):
        """Set the volume of the music player"""
        self.volume = float(volume) 
        pygame.mixer.music.set_volume(self.volume)
        self.is_muted = False  # Unmute when volume is adjusted
        self.volumeLabel.configure(image = self.volumeIcon)  

    def toggleMute(self):
        """Toggle mute state"""
        if self.is_muted:
            # Unmute
            pygame.mixer.music.set_volume(self.volume)  # Restore volume
            self.volumeLabel.configure(image = self.volumeIcon)  # Change to volume icon
            self.volumeSlider.set(self.volume)  # Restore slider position
        else:
            # Mute
            self.volume = pygame.mixer.music.get_volume()  # Store current volume
            pygame.mixer.music.set_volume(0)  # Mute
            self.volumeLabel.configure(image = self.muteIcon)  # Change to mute icon
            self.volumeSlider.set(0)  # Set slider to 0 when muted
        
        self.is_muted = not self.is_muted  # Toggle mute state

    def scrapeLyrics(self, song_name, artist_name=None):
        """Fetch lyrics for the current song."""
        lyrics = LyricsFetcher.fetch_lyrics(song_name, artist_name)
        self.lyricsLabel.configure(text=lyrics) 


    def toggleLyrics(self):
       """Toggle the visibility of the lyrics frame."""
       if self.lyricsFrame.winfo_ismapped():
           self.lyricsFrame.pack_forget()  
           self.toggleLyricsButton.configure(text="Show Lyrics")
       else:
           if self.currentSong:
               songName = os.path.splitext(os.path.basename(self.currentSong))[0]  # removing mp3 extension
               songLyrics = self.scrapeLyrics(songName)  # Fetch lyrics
               self.lyricsLabel.configure(text=songLyrics)  # Update the lyrics label
           else:
               self.lyricsLabel.configure(text="No song selected.")
           self.lyricsFrame.pack(fill="both", expand=True, pady=(20, 0))
           self.toggleLyricsButton.configure(text="Hide Lyrics")

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    player = MusicPlayer()
    player.run() 




    