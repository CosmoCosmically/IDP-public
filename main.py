####################################################################################################
#
# Entry point for the AGV.
#
# Copyright (c) 2026 IDP group 112. All Rights Reserved.
#
####################################################################################################

# Machine imports
import uasyncio  # type: ignore
from utime import ticks_ms, ticks_diff  # type: ignore

# Local imports
from misc.components.button import button
from overallnavigation import robot
from config import CONTROL_LOOP_POLL_RATE, DISABLE_RUN
from misc.components.LEDArray import LED_array


async def entry():
    if DISABLE_RUN:
        print("!!!Running is disabled for debug, if not expected disable in config!!!")
        start = ticks_ms()
        while ticks_diff(ticks_ms(), start) < 5000:
            LED_array.flash()
            await uasyncio.sleep_ms(100)
        return
    while True:
        button._handler(0)
        if button.state():
            await robot()
        await uasyncio.sleep_ms(1000 // CONTROL_LOOP_POLL_RATE)


uasyncio.run(entry())
