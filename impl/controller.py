import threading
import time

from PIL import Image
from PIL.Image import Resampling
from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions
from RGBMatrixEmulator.emulators.canvas import Canvas
from impl.screen import *


class Controller:
    MATRIX_CONFIG_HEADER: str = "Matrix"
    REFRESH_RATE: int = 25

    def __init__(self, config):
        self.frames = 0
        self.startTime = None
        self.config = config
        self.app_list = None
        self.app_index = 0
        self.render_thread = None
        self.canvas_height = 0
        self.canvas_width = 0
        self.matrix = None
        self.emulated = False
        self.app_index = 0
        self.canvas = None

    def configure_display(self):
        # Initialize the LED matrix
        config = self.config
        options = RGBMatrixOptions()
        options.hardware_mapping = config.get(Controller.MATRIX_CONFIG_HEADER, 'hardware_mapping', fallback='regular')
        options.rows = config.getint(Controller.MATRIX_CONFIG_HEADER, 'height', fallback=64)
        options.cols = config.getint(Controller.MATRIX_CONFIG_HEADER, 'width', fallback=64)
        options.brightness = 100 if self.emulated else config.getint(Controller.MATRIX_CONFIG_HEADER, 'brightness',
                                                                     fallback=100)
        options.gpio_slowdown = config.getint(Controller.MATRIX_CONFIG_HEADER, 'gpio_slowdown', fallback=1)
        options.limit_refresh_rate_hz = config.getint(Controller.MATRIX_CONFIG_HEADER, 'limit_refresh_rate_hz',
                                                      fallback=0)
        options.drop_privileges = config.get(Controller.MATRIX_CONFIG_HEADER, 'hardware_mapping', fallback=False)

        emulated = config.get(Controller.MATRIX_CONFIG_HEADER, 'is_emulated', fallback=False)

        if emulated:
            matrix = RGBMatrix(options=options)
            self.canvas = matrix.CreateFrameCanvas()
        else:
            pass
        #    matrix = rgbmatrix(options=options)

        self.matrix = matrix
        self.emulated = emulated
        self.canvas_width = self.matrix.width
        self.canvas_height = self.matrix.height
        self.app_list = [GifScreen(), SpotifyScreen(), MainScreen(), WeatherScreen()]

    def start(self):
        self.render_thread = threading.Thread(name="render_thread", target=self.render)
        self.render_thread.start()

    def render(self):

        if self.startTime is None:
            self.startTime = time.time()

        refresh_time = 1 / Controller.REFRESH_RATE  # 1 second divided by rate
        timer = self.startTime
        while True:
            app = self.current_app()
            frame = app.generate_frame()
            # frame = Image.open("image1.png")
            if frame is None:
                frame = Image.new("RGB", (self.canvas_width, self.canvas_height), (0, 0, 0))
            else:
                frame.thumbnail((self.canvas_width, self.canvas_height), Resampling.LANCZOS)
            if self.emulated:
                pass
                #self.canvas.SetImage(frame.convert('RGB'))
                # self.matrix.SetImage(frame.convert('RGB'))  # is this because the matrix can only use rgb rather than rgba?
                #self.matrix.SwapOnVSync(self.canvas)

            dur = time.time() - self.startTime
            dur2 = time.time() - timer
            sleep_dur = refresh_time - dur2
            print ("sleep dur:", sleep_dur)
            time.sleep(max(0, sleep_dur))
            timer = time.time()
            self.frames += 1

            fps = self.frames / dur
            print("fps: ", fps)

    def next_app(self):
        self.app_index += 1
        self.app_index = self.app_index % len(self.app_list)

    def previous_app(self):
        self.app_index -= 1
        self.app_index = self.app_index % len(self.app_list)

    def current_app(self):
        return self.app_list[self.app_index]
