from abc import ABC, abstractmethod

from PIL import Image, ImageSequence


class Screen(ABC):
    @abstractmethod
    def generate_frame(self):
        return NotImplementedError("not implemented")


class SpotifyScreen(Screen):

    def generate_frame(self):
        print("Implemented generate_frame in SpotifyScreen")
        return Image.open("image1.png")


class MainScreen(Screen):

    def generate_frame(self):
        print("Implemented generate_frame in MainScreen")
        return Image.open("image2.png")


class WeatherScreen(Screen):

    def generate_frame(self):
        print("Implemented generate_frame in WeatherScreen")
        return Image.open("image3.png")


class GifScreen(Screen):

    def __init__(self):
        self.count = 0
        self.image = Image.open("giphy.gif")
        self.curr_gif = ImageSequence.Iterator(self.image)

    def generate_frame(self):
        # print("Implemented generate_frame in GifScreen")

        try:
            print ("gif frame ", self.count)
            frame = self.curr_gif[self.count].convert('RGB')
        except IndexError:
            self.count = 0
            frame = self.curr_gif[self.count].convert('RGB')
        self.count += 1
        return frame

