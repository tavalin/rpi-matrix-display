import time
import pause

class Screen:
    def __init__(self):
        self.frame_rate = 30 # frames per second
        self.frame = None

        self._frame_count = 0
        self._start_time = 0
        self._wakeup_time = 0
    
    def generate_frame(self):
        # generate a frame here
        # ...
        if self._start_time == 0:
            self._start_time = time.time()  

        self.frame = "Generated frame"
        self._frame_count += 1
        self._wakeup_time = time.time() + (1/self.frame_rate)
        print ("fps: ", self._frame_count/ (time.time()-self._start_time))
    
    def wait_until_next_frame(self):
        # time.sleep(1/self.frame_rate)
        pause.until(self._wakeup_time)


class Controller:
    def __init__(self, screen):
        self.screen = screen
    
    def display_frame(self):

        pass
        # print(self.screen.frame)
    
    def run(self):
        while True:
            self.screen.generate_frame()
            self.display_frame()
            self.screen.wait_until_next_frame()

if __name__ == "__main__":
    my_screen = Screen()
    my_controller = Controller(my_screen)
    my_controller.run()