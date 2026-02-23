####################################################################################################
#
# Logic related to the LED array.
#
# Copyright (c) 2026 IDP group 112. All Rights Reserved.
#
####################################################################################################
from grabber.components.types.resistance import REEL_ARR, Reel

from machine import Pin  # type: ignore
from misc.config import LED_FLASH_DEBOUNCE, LED_STROBE_DEBOUNCE, LED_RESET_TIMEOUT
from utime import sleep_ms, ticks_ms, ticks_diff  # type: ignore
from config import LED_PINS


class LEDArray:
    """
    Controls a multi-LED array for reel indication and status feedback.
    """
    def __init__(self):
        self.LEDS = {k: Pin(v, Pin.OUT) for k, v in LED_PINS.items()}
        self.f_c = 0
        self.l_f = ticks_ms()

    def transition(self, reel):
        """
        Activate the LED corresponding to a specific reel and disable others.

        Args:
            reel (Reel): Reel identifier.
        """
        self.all(0)
        self.LEDS[reel].on()

    def off(self):
        """
        Turn all LEDs off.
        """
        self.all(0)

    def all(self, val):
        """
        Set all LEDs to a given value.

        Args:
            val (int): 0 for off, 1 for on.
        """
        for _, led in self.LEDS.items():
            led.value(val)

    def strobe(self):
        """
        Cycle through reel LEDs sequentially with debounce and reset timeout.
        """
        t_d = ticks_diff(ticks_ms(), self.l_f)
        if t_d < LED_STROBE_DEBOUNCE:
            return
        elif t_d > LED_RESET_TIMEOUT:
            self.all(0)
            self.f_c = 0
        LED_array.transition(REEL_ARR[self.f_c])
        self.f_c = (self.f_c + 1) % 4
        self.l_f = ticks_ms()

    def flash(self):
        """
        Flash all LEDs on and off with debounce and reset timeout.
        """
        t_d = ticks_diff(ticks_ms(), self.l_f)
        if t_d < LED_FLASH_DEBOUNCE:
            return
        elif t_d > LED_RESET_TIMEOUT:
            self.all(0)
            self.f_c = 0
        self.f_c = (self.f_c + 1) % 2
        self.all(self.f_c)
        self.l_f = ticks_ms()


LED_array = LEDArray()

if __name__ == "__main__":
    start = ticks_ms()
    while ticks_diff(ticks_ms(), start) < 5000:
        LED_array.strobe()
        sleep_ms(100)
    start = ticks_ms()
    while ticks_diff(ticks_ms(), start) < 5000:
        LED_array.flash()
        sleep_ms(100)
    LED_array.off()
