####################################################################################################
#
# Logic related to the button.
#
# Copyright (c) 2026 IDP group 112. All Rights Reserved.
#
####################################################################################################

# Machine imports
from machine import Pin  # type: ignore
from utime import sleep_ms, ticks_ms, ticks_diff  # type: ignore

# Local imports
from config import BUTTON_PIN

TIMEOUT = 1000


class Button:
    def __init__(self):
        self.b = Pin(BUTTON_PIN, Pin.IN)
        self._triggered = False
        self._debounce = None

    def state(self):
        triggered = self._triggered
        if self._triggered:
            self._debounce = ticks_ms()
            self._triggered = False
        return triggered

    def _handler(self, _):
        if self._debounce and ticks_diff(ticks_ms(), self._debounce) < TIMEOUT:
            return
        if self.b.value():
            self._triggered = True


button = Button()


if __name__ == "__main__":
    while True:
        button._handler("")
        print(button.state())
        sleep_ms(10)
