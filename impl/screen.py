from abc import ABC, abstractmethod
from PIL.Image import LANCZOS
from PIL import Image, ImageSequence
import time
import pause


class Screen(ABC):

    def __init__(self):
        self._next_frame_time = time.time()

    @abstractmethod
    def generate_frame(self):
        return NotImplementedError("not implemented")

    def wait_for_next_frame(self):
        pause.until(self._next_frame_time)


class SpotifyScreen(Screen):

    def __init__(self):
        super(SpotifyScreen, self)

    def generate_frame(self):
        print("Implemented generate_frame in SpotifyScreen")
        frame = Image.open("image1.png").convert('RGB').resize([128, 128], LANCZOS)
        self._next_frame_time = time.time() + (1 / 30)
        return frame




class MainScreen(Screen):

    def __init__(self):
        super(MainScreen, self)

    def generate_frame(self):
        print("Implemented generate_frame in MainScreen")
        frame = Image.open("image2.png").convert('RGB').resize([128, 128], LANCZOS)
        self._next_frame_time = time.time() + (1 / 30)
        return 




class WeatherScreen(Screen):

    def __init__(self):
        super(WeatherScreen, self)

    def generate_frame(self):
        print("Implemented generate_frame in WeatherScreen")
        frame = Image.open("image3.png").convert('RGB').resize([128, 128], LANCZOS)
        self._next_frame_time = time.time() + (1 / 30)
        return frame



class GifScreen(Screen):

    def __init__(self):
        super(GifScreen, self)
        self._frames = []
        with Image.open("giphy.gif") as gif:
            for frame in ImageSequence.Iterator(gif):
                frame = frame.convert('RGB').resize([128, 128], LANCZOS)
                self._frames.append(frame)
        self._frame_idx = 0

    def generate_frame(self):

        # print("GifScreen generate frame")
        # print ("_frame_idx = ", self._frame_idx)
        frame = self._frames[self._frame_idx]

        self._next_frame_time = time.time() + frame.info['duration'] / 1000
        if self._frame_idx == len(self._frames) - 1:
            self._frame_idx = 0
        else:
            self._frame_idx += 1

        return frame


