import unittest
import tkinter as tk
import pygame
import os
from unittest.mock import patch
from musicPlayer import MusicPlayer


class TestMusicPlayer(unittest.TestCase):
    def setUp(self):
        """Initialize the MusicPlayer instance for each test."""
        self.root = tk.Tk()
        self.root.withdraw() 

        pygame.mixer.init()

        self.player = MusicPlayer()
        self.player.playlist = ["test_song_1.mp3", "test_song_2.mp3"]
        self.player.currentSongIndex = 0
        self.player.currentSong = self.player.playlist[0]
        self.player.songLength = 180  # Mock a song length of 3 minutes

    def tearDown(self):
        """Clean up after each test."""
        pygame.mixer.quit()
        self.root.destroy()

    @patch("customtkinter.CTkLabel")
    @unittest.skipIf(os.environ.get("DISPLAY") is None, "Skipping GUI tests in headless environment")
    def test_formatTime(self, mock_ctklabel):
        """Test formatting time in MM:SS format."""
        formatted_time = self.player.formatTime(125)
        self.assertEqual(formatted_time, "02:05")

    @patch("customtkinter.CTkLabel")
    @unittest.skipIf(os.environ.get("DISPLAY") is None, "Skipping GUI tests in headless environment")
    def test_playNext(self, mock_ctklabel):
        """Test playing the next song in the playlist."""
        self.player.playNext()
        self.assertEqual(self.player.currentSong, "test_song_2.mp3")

    @patch("customtkinter.CTkLabel")
    @unittest.skipIf(os.environ.get("DISPLAY") is None, "Skipping GUI tests in headless environment")
    def test_playPrevious(self, mock_ctklabel):
        """Test playing the previous song in the playlist."""
        self.player.playNext()  # Move to the second song
        self.player.playPrevious()
        self.assertEqual(self.player.currentSong, "test_song_1.mp3")

    @patch("customtkinter.CTkLabel")
    @unittest.skipIf(os.environ.get("DISPLAY") is None, "Skipping GUI tests in headless environment")
    def test_playSelectedSong(self, mock_ctklabel):
        """Test playing a selected song."""
        self.player.playSelectedSong("test_song_1.mp3")
        self.assertEqual(self.player.currentSong, "test_song_1.mp3")

    @patch("customtkinter.CTkLabel")
    @unittest.skipIf(os.environ.get("DISPLAY") is None, "Skipping GUI tests in headless environment")
    def test_setVolume(self, mock_ctklabel):
        """Testing volume."""
        self.player.setVolume(0.5)
        self.assertEqual(pygame.mixer.music.get_volume(), 0.5)

    @patch("customtkinter.CTkLabel")
    @unittest.skipIf(os.environ.get("DISPLAY") is None, "Skipping GUI tests in headless environment")
    def test_toggleMute(self, mock_ctklabel):
        """Test toggling mute."""
        self.player.toggleMute()
        self.assertTrue(self.player.isMuted)


if __name__ == "__main__":
    unittest.main()
