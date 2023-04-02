
import threading
import time
from PIL import Image
from PIL.Image import Resampling
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from apps_v2.spotify_player import SpotifyScreenOld
from modules.spotify_module import SpotifyModule
# from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions
# from RGBMatrixEmulator.emulators.canvas import Canvas
from screen import *


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
        options.hardware_mapping = config.get(
            Controller.MATRIX_CONFIG_HEADER, 'hardware_mapping', fallback='regular')
        options.rows = config.getint(
            Controller.MATRIX_CONFIG_HEADER, 'canvas_height', fallback=64)
        options.cols = config.getint(
            Controller.MATRIX_CONFIG_HEADER, 'canvas_width', fallback=64)
        options.brightness = 100 if self.emulated else config.getint(Controller.MATRIX_CONFIG_HEADER, 'brightness',
                                                                     fallback=100)
        options.gpio_slowdown = config.getint(
            Controller.MATRIX_CONFIG_HEADER, 'gpio_slowdown', fallback=1)
        options.limit_refresh_rate_hz = config.getint(Controller.MATRIX_CONFIG_HEADER, 'limit_refresh_rate_hz',
                                                      fallback=0)
        options.drop_privileges = config.get(
            Controller.MATRIX_CONFIG_HEADER, 'drop_privileges', fallback=False)
        options.pixel_mapper_config = config.get(
            Controller.MATRIX_CONFIG_HEADER, 'pixel_mapper_config', fallback='V-mapper')
        options.parallel = config.getint(
            Controller.MATRIX_CONFIG_HEADER, 'parallel', fallback=1)
        options.chain_length = config.getint(
            Controller.MATRIX_CONFIG_HEADER, 'chain_length', fallback=1)
        emulated = config.get(Controller.MATRIX_CONFIG_HEADER,
                              'is_emulated', fallback=False)

#        if emulated:
#            matrix = RGBMatrix(options=options)
#            self.canvas = matrix.CreateFrameCanvas()
#        else:
#            pass
        print(options)
        matrix = RGBMatrix(options=options)
        print("height: ", matrix.height)
        print("Width: ", matrix.width)
        self.matrix = matrix
        self.emulated = emulated
        self.canvas_width = self.matrix.width
        self.canvas_height = self.matrix.height
        self.app_list = [GifScreen(), SpotifyScreen(),
                         MainScreen(), WeatherScreen()]

        modules = {'spotify': SpotifyModule(config)}
        self.app_list = [GifScreen(), SpotifyScreenOld(
            config, modules, matrix.width, matrix.height, False), MainScreen(), WeatherScreen()]

    def start(self):
        self.render_thread = threading.Thread(
            name="render_thread", target=self.render)
        self.render_thread.start()

    def render(self):

        while True:
            # print("render")
            app = self.current_app()
            frame = app.generate_frame()
            if frame is not None:
                self.matrix.SetImage(frame)
            app.wait_for_next_frame()

    def next_app(self):
        self.app_index += 1
        self.app_index = self.app_index % len(self.app_list)

    def previous_app(self):
        self.app_index -= 1
        self.app_index = self.app_index % len(self.app_list)

    def current_app(self):
        return self.app_list[self.app_index]
