# this file contains simple helpers for ultrasonic and traffic lights

import RPi.GPIO as GPIO
import time

def setup():
    """Setup function for rpi gpio. Automatically called on import of this file."""

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

class TrafficLight(object):
    """A traffic light consisting of a red, orange and green light controlled
    by GPIOs."""
    def __init__(self, red, orange, green):
        "Set pin modes and initial state of light (stopped)."
        self.red = red
        self.orange = orange
        self.green = green

        GPIO.setup(self.red, GPIO.OUT)
        GPIO.setup(self.orange, GPIO.OUT)
        GPIO.setup(self.green, GPIO.OUT)

        GPIO.output(self.red, True)
        GPIO.output(self.orange, False)
        GPIO.output(self.green, False)

    def go(self):
        "Change lights to indicate 'go' on this route."
        GPIO.output(self.red, False)
        GPIO.output(self.green, True)

    def stop(self):
        "Change lights to indicate stop on this route."
        GPIO.output(self.green, False)
        GPIO.output(self.orange, True)
        time.sleep(3)
        GPIO.output(self.orange, False)
        GPIO.output(self.red, True)

class Ultrasonic(object):
    """An ultrasonic sensor controlled by Raspberry Pi GPIO. This class
    robustly calculates the distance of an object from the sensor.
    """

    speed_of_sound = 34300  # cm/s

    def __init__(self, trigger, echo):
        "Set pin modes."
        self.trigger = trigger
        self.echo = echo

        GPIO.setup(self.trigger, GPIO.OUT)
        GPIO.setup(self.echo, GPIO.IN)

        # half a second timeout when reading pulse length
        self.timeout = 0.3
        self.history = [999] * 5;

    def read_cm(self):
        """Send a pulse down the trigger line. Poll for a pulse coming
        back on the echo line. Based on that pulse length, calculate sensor
        distance reading. If reading is out of reasonable bounds, return None.
        """

        # send pulse
        GPIO.output(self.trigger, True)
        time.sleep(0.0001)
        GPIO.output(self.trigger, False)

        # initialise timer values
        trigger = time.time()
        start = time.time()
        stop = time.time()

        # measure length of return pulse
        while GPIO.input(self.echo) == 0 \
              and (time.time() - trigger) < self.timeout:
            start = time.time()

        while GPIO.input(self.echo) == 1 \
              and (time.time() - trigger) < self.timeout:
            stop = time.time()

        # calculate distance
        pulse_length = stop - start
        dist = (pulse_length * self.speed_of_sound) / 2

        # basic error checking on distance value
        if dist < 5 or dist > 150:
            dist = None

        # average last N measurements
        if dist is not None:
            self.history.pop(0)
            self.history.append(dist)
            return sum(self.history)/len(self.history)

        return dist

setup()
