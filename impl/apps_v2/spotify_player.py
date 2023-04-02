import numpy as np, requests, math, time, threading
from PIL import Image, ImageFont, ImageDraw
from io import BytesIO

from screen import Screen

class SpotifyScreenOld(Screen):
    def __init__(self, config, modules, width, height, fullscreen):
        super(SpotifyScreenOld, self)
        self.modules = modules

        self.font = ImageFont.truetype("fonts/tiny.otf", 10)
        # self.font = ImageFont.truetype("fonts/Gotham-Black.otf", 10)

        self.canvas_width = width
        self.canvas_height = height

        #  -------------------------------------------------   TODO: FIX COORDS and SCALE
        self.scale_factor = int(width / 64)
        #  --------------------------------------------------

        self.title_color = (255,255,255)
        self.artist_color = (255,255,255)
        self.play_color = (102, 240, 110)

        self.full_screen_always = fullscreen

        self.current_art_url = ''
        self.current_art_img = None
        self.current_title = ''
        self.current_artist = ''

        self.title_animation_cnt = 0
        self.artist_animation_cnt = 0
        self.last_title_reset = math.floor(time.time())
        self.last_artist_reset = math.floor(time.time())
        self.scroll_delay = 4

        self.paused = True
        self.paused_time = math.floor(time.time())
        self.paused_delay = 5

        self.is_playing = False

        self.last_fetch_time = math.floor(time.time())
        self.fetch_interval = 1
        self.spotify_module = self.modules['spotify']

        self.response = None
        self.thread = threading.Thread(target=self.getCurrentPlaybackAsync)
        self.thread.start()

    def getCurrentPlaybackAsync(self):
        # delay spotify fetches
        time.sleep(3)
        while True:
            self.response = self.spotify_module.getCurrentPlayback()
            time.sleep(1)



    def generate_frame(self):
        if not self.spotify_module.queue.empty():
            self.response = self.spotify_module.queue.get()
            self.spotify_module.queue.queue.clear()
        frame = self.generateFrame(self.response)
        self._next_frame_time = time.time() + (1 / 30)
        return frame

    def generateFrame(self, response):
        if response is not None:
            (artist, title, art_url, self.is_playing, progress_ms, duration_ms) = response

            if self.full_screen_always:
                if self.current_art_url != art_url:
                    self.current_art_url = art_url
                    response = requests.get(self.current_art_url)
                    img = Image.open(BytesIO(response.content))
                    self.current_art_img = img.resize((self.canvas_width, self.canvas_height), resample=Image.LANCZOS)

                frame = Image.new("RGB", (self.canvas_width, self.canvas_height), (0,0,0))
                draw = ImageDraw.Draw(frame)

                frame.paste(self.current_art_img, (0,0))
                #return (frame, self.is_playing)
                return frame
            else:
                if not self.is_playing:
                    if not self.paused:
                        self.paused_time = math.floor(time.time())
                        self.paused = True
                else:
                    if self.paused and self.current_art_img and self.current_art_img.size == (self.canvas_width, self.canvas_height):
                        self.title_animation_cnt = 0
                        self.artist_animation_cnt = 0
                        self.last_title_reset = math.floor(time.time())
                        self.last_artist_reset = math.floor(time.time())
                    self.paused_time = math.floor(time.time())
                    self.paused = False
#    x = 10 
                if (self.current_title != title or self.current_artist != artist):
                    self.current_artist = artist
                    self.current_title = title
                    self.title_animation_cnt = 0
                    self.artist_animation_cnt = 0
                    self.last_title_reset = math.floor(time.time())
                    self.last_artist_reset = math.floor(time.time())

                current_time = math.floor(time.time())
                show_fullscreen = current_time - self.paused_time >= self.paused_delay

                # show fullscreen album art after pause delay
#                if show_fullscreen and self.current_art_img.size == (48, 48):
                if show_fullscreen and self.current_art_img.size == (48 * self.scale_factor, 48 * self.scale_factor):
                    response = requests.get(self.current_art_url)
                    img = Image.open(BytesIO(response.content))
                    self.current_art_img = img.resize((self.canvas_width, self.canvas_height), resample=Image.LANCZOS)
                elif not show_fullscreen and (self.current_art_url != art_url or self.current_art_img.size == (self.canvas_width, self.canvas_height)):
                    self.current_art_url = art_url
                    response = requests.get(self.current_art_url)
                    img = Image.open(BytesIO(response.content))
#                    self.current_art_img = img.resize((48, 48), resample=Image.LANCZOS)
                    self.current_art_img = img.resize((48 *self.scale_factor, 48 *self.scale_factor), resample=Image.LANCZOS)


                frame = Image.new("RGB", (self.canvas_width, self.canvas_height), (0,0,0))
                draw = ImageDraw.Draw(frame)

                # exit early if fullscreen
                if self.current_art_img is not None:
                    if show_fullscreen:
                        frame.paste(self.current_art_img, (0,0))
                        #return (frame, self.is_playing)
                        return frame
                    else:
#                        frame.paste(self.current_art_img, (8,14))
                        frame.paste(self.current_art_img, (8 * self.scale_factor,13 * self.scale_factor))
                freeze_title = self.title_animation_cnt == 0 and self.artist_animation_cnt > 0
                freeze_artist = self.artist_animation_cnt == 0 and self.title_animation_cnt > 0

                title_len = self.font.getsize(self.current_title)[0]
                artist_len = self.font.getsize(self.current_artist)[0]

#                text_length = self.canvas_width - 12
                text_length = self.canvas_width - ( 12 * self.scale_factor)
                x_offset = 1
                spacer = "     "


                self.font.getsize(self.current_title)
                ascent, descent = self.font.getmetrics()
                text_height = self.font.getmask(self.current_title).getbbox()[3] + descent

                _left, _top, _right, title_bottom = self.font.getbbox(self.current_title)


                if title_len > text_length:
                    draw.text((x_offset-self.title_animation_cnt, 1*self.scale_factor), self.current_title + spacer + self.current_title, self.title_color, font = self.font)
#                    draw.text((x_offset-self.title_animation_cnt, 1), self.current_title + spacer + self.current_title, self.title_color, font = self.font)
                    if current_time - self.last_title_reset >= self.scroll_delay:
                        self.title_animation_cnt += 1
                    if freeze_title or self.title_animation_cnt == self.font.getsize(self.current_title + spacer)[0]:
                        self.title_animation_cnt = 0
                        self.last_title_reset = math.floor(time.time())
                else:
                    draw.text((x_offset-self.title_animation_cnt, 1), self.current_title, self.title_color, font = self.font)

                if artist_len > text_length:
#                    draw.text((x_offset-self.artist_animation_cnt, 7), self.current_artist + spacer + self.current_artist, self.artist_color, font = self.font)
                    draw.text((x_offset-self.artist_animation_cnt, title_bottom+(1*self.scale_factor)), self.current_artist + spacer + self.current_artist, self.artist_color, font = self.font)
                    if current_time - self.last_artist_reset >= self.scroll_delay:
                        self.artist_animation_cnt += 1
                    if freeze_artist or self.artist_animation_cnt == self.font.getsize(self.current_artist + spacer)[0]:
                        self.artist_animation_cnt = 0
                        self.last_artist_reset = math.floor(time.time())
                else:
#                    draw.text((x_offset-self.artist_animation_cnt, 7), self.current_artist, self.artist_color, font = self.font)
                    draw.text((x_offset-self.artist_animation_cnt, title_bottom+(1*self.scale_factor)), self.current_artist, self.artist_color, font = self.font)

# not sure what these rectangles are for?
                draw.rectangle((0,0,0,12), fill=(0,0,0))
#                draw.rectangle((52,0,63,12), fill=(0,0,0))
                draw.rectangle((52 * self.scale_factor,0*self.scale_factor,64*self.scale_factor,12 *self.scale_factor), fill=(0,0,0))

#                line_y = 63
                line_y = 125
#                draw.rectangle((0,line_y-1,63,line_y), fill=(100,100,100))
                draw.rectangle((0,line_y-1,63 * self.scale_factor,line_y), fill=(100,100,100))
                draw.rectangle((0,line_y-1,0+round(((progress_ms / duration_ms) * 100) // 1.57), line_y), fill=self.play_color)
#                drawPlayPause(draw, self.is_playing, self.play_color)
                drawPlayPause(draw, self.is_playing, self.scale_factor,self.play_color)
                #return (frame, self.is_playing)
                return frame
        else:
            #not active
            frame = Image.new("RGB", (self.canvas_width, self.canvas_height), (0,0,0))
            draw = ImageDraw.Draw(frame)

            self.current_art_url = ''
            self.is_playing = False
            self.title_animation_cnt = 0
            self.artist_animation_cnt = 0
            self.last_title_reset = math.floor(time.time())
            self.last_artist_reset = math.floor(time.time())
            self.paused = True
            self.paused_time = math.floor(time.time())

            return None

#def drawPlayPause(draw, is_playing, color):
def drawPlayPause(draw, is_playing, scale_factor, color):
    x = 10 
#    x = 15 
    y = -16 
    if not is_playing:
#        draw.line((x+45,y+19,x+45,y+25), fill = color)
#        draw.line((x+46,y+20,x+46,y+24), fill = color)
#        draw.line((x+47,y+20,x+47,y+24), fill = color)
#        draw.line((x+48,y+21,x+48,y+23), fill = color)
#        draw.line((x+49,y+21,x+49,y+23), fill = color)
#        draw.line((x+50,y+22,x+50,y+22), fill = color)

        draw.line(((x+45)*scale_factor,(y+19)*scale_factor,(x+45)*scale_factor,(y+25)*scale_factor), fill = color)
        draw.line(((x+46)*scale_factor,(y+20)*scale_factor,(x+46)*scale_factor,(y+24)*scale_factor), fill = color)
        draw.line(((x+47)*scale_factor,(y+20)*scale_factor,(x+47)*scale_factor,(y+24)*scale_factor), fill = color)
        draw.line(((x+48)*scale_factor,(y+21)*scale_factor,(x+48)*scale_factor,(y+23)*scale_factor), fill = color)
        draw.line(((x+49)*scale_factor,(y+21)*scale_factor,(x+49)*scale_factor,(y+23)*scale_factor), fill = color)
        draw.line(((x+50)*scale_factor,(y+22)*scale_factor,(x+50)*scale_factor,(y+22)*scale_factor), fill = color)
    else:
#        draw.line((x+45,y+19,x+45,y+25), fill = color)
#        draw.line((x+46,y+19,x+46,y+25), fill = color)
#        draw.line((x+49,y+19,x+49,y+25), fill = color)
#        draw.line((x+50,y+19,x+50,y+25), fill = color)

        draw.line(((x+45)*scale_factor,(y+19)*scale_factor,(x+45)*scale_factor,(y+25)*scale_factor), fill = color)
        draw.line(((x+46)*scale_factor,(y+19)*scale_factor,(x+46)*scale_factor,(y+25)*scale_factor), fill = color)
        draw.line(((x+49)*scale_factor,(y+19)*scale_factor,(x+49)*scale_factor,(y+25)*scale_factor), fill = color)
        draw.line(((x+50)*scale_factor,(y+19)*scale_factor,(x+50)*scale_factor,(y+25)*scale_factor), fill = color)
