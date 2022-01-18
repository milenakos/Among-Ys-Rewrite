# License for this file:
#
#    Among Ys Rewrite
#    Copyright (C) 2022  Milenakos
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

import pygame, utils, winsound, threading, random

notes = ["F4", "G4", "A4", "B4", "C5", "D5", "E5", "F5", "G5", "A5", "B5", "C6", "D6", "B6"]
notes_small = ["F#4","G#4", "A#4", 0, "C#5", "D#5", 0, "F#5", "G#5", "A#5", 0, "C#6", "D#6"]

class Piano_task(pygame.sprite.Sprite):
	def __init__(self):
		songs = [["D5", "D5", "D6", "A5", "G#5", "G5", "F5"], ["C5", "D#5", "F5", "F#5", "F5", "D#5", "C5", "A#4", "D5", "C5"], 
		["E5", "E5", "E5", "C5", "E5", "G5", "G4"], ["C#5", "D#5", "G#4", "D#5", "F5"]]

		pygame.sprite.Sprite.__init__(self)
		self.image_def = pygame.image.load(utils.get_path("img/tasks/piano.png")).convert_alpha()
		self.image = self.image_def
		self.rect = self.image.get_rect()
		self.rect.center = (640, 360)
		self.keys = (0, 0)
		self.frequency = 0
		self.change = True
		self.render(self.keys)
		self.song = random.choice(songs)
		self.finished = False
		self.step = 0
		x = threading.Thread(target=self.play)
		x.start()

	def note(self, name):
		if name != 0:
			octave = int(name[-1])
			PITCHES = "c,c#,d,d#,e,f,f#,g,g#,a,a#,b".split(",")
			pitch = PITCHES.index(name[:-1].lower())
			self.frequency = 440 * 2 ** ((octave - 4) + (pitch - 9) / 12.)
			self.change = True
		else:
			self.frequency = 0
			self.change = True

	def render(self, keys):
		if self.keys != keys:
			self.image = self.image_def
			found = False

			temp = pygame.Surface((800, 600), flags=pygame.SRCALPHA)

			try:
				next = notes_small.index(self.song[self.step])
			except:
				next = -1

			for i in range(0, 13):
				if i != 3 and i != 6 and i != 10:
					self.key = pygame.image.load(utils.get_path("img/tasks/small_piano_static.png")).convert_alpha()
					self.key_rect = self.key.get_rect()
					if i == next:
						self.key = pygame.image.load(utils.get_path("img/tasks/small_piano_next.png")).convert_alpha()
					if self.key_rect.collidepoint(keys[0] - (i * 58) - 240 - 42, keys[1] - 280) and not found:
						self.key = pygame.image.load(utils.get_path("img/tasks/small_piano_pressed.png")).convert_alpha()
						found = True
						self.note(notes_small[i])
						if i == next:
							self.step += 1
						else:
							self.step == 0
						
					temp.blit(self.key, ((i * 58) + 42, 222))

			try:
				next = notes.index(self.song[self.step])
			except:
				next = -1
			
			for i in range(0, 14):
				self.key = pygame.image.load(utils.get_path("img/tasks/piano_static.png")).convert_alpha()
				self.key_rect = self.key.get_rect()
				if i == next:
					self.key = pygame.image.load(utils.get_path("img/tasks/piano_next.png")).convert_alpha()
				if self.key_rect.collidepoint(keys[0] - (i * 58) - 240, keys[1] - 280) and not found:
					self.key = pygame.image.load(utils.get_path("img/tasks/piano_pressed.png")).convert_alpha()
					found = True
					self.note(notes[i])
					if i == next:
						self.step += 1

				self.image.blit(self.key, (i * 58, 222))
				self.image.blit(temp, (0, 0))
			
			if not found:
				self.frequency = 0
			
			self.rect = self.image.get_rect()
			if len(self.song) <= self.step:
				self.finished = True
			self.rect.center = (640, 360)
		self.keys = keys

	def play(self):
		while True:
			if self.frequency and self.change:
				self.change = False
				y = threading.Thread(target=winsound.Beep, args=(int(self.frequency), 500,))
				y.start()

	def draw(self, screen, *args):
		screen.blit(self.image, self.rect)

if __name__ == "__main__":
	print("\nWarning: this is not main.py.\n")