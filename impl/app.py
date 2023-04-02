
import argparse
import configparser
import inspect
import os
import sys
from io import BytesIO
import controller

import flask
# get config
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(current_dir + "\rpi-rgb-led-matrix\bindings\python")


#from rgbmatrix import RGBMatrix, RGBMatrixOptions
#from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions

#from impl import controller
from controller import Controller

controller = None


# Define the Flask app
app = flask.Flask(__name__)


# Define a route to display the current image
@app.route("/")
def display_image():
    # global app_index
    # Show the current image on the LED matrix

    img_io: BytesIO = BytesIO()
    current_app = controller.current_app()
    frame = current_app.generate_frame()
    frame.save(img_io, 'PNG', quality=70)
    img_io.seek(0)

    # Return the current image as an HTTP response
    return flask.send_file(img_io, mimetype="image/png")


# Define a route to cycle through the images
@app.route("/next")
def next_image():
    controller.next_app()
    # Redirect to the display_image route to show the new image
    return flask.redirect("/")


@app.route("/previous")
def previous_image():
    controller.previous_app()
    # Redirect to the display_image route to show the new image
    return flask.redirect("/")


def main():
    config = configparser.ConfigParser()
    parsed_configs = config.read('../config.ini')
    if len(parsed_configs) == 0:
        print("no config file found")
        sys.exit(0)

    global controller
    controller = Controller(config)
    controller.configure_display()
    controller.start()

    # Start the Flask app
    app.run(host="0.0.0.0", port=8080, debug=False)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted with Ctrl-C')
        sys.exit(0)
