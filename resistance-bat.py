import asyncio

import math
import board
from rainbowio import colorwheel
import neopixel

try:
    import urandom as random
except ImportError:
    import random


NUMFIREPIX = 84
#FIREPIXPIN = board.NEOPIXEL
FIREPIXPIN = board.A0
FIRESTRIP = neopixel.NeoPixel(
    FIREPIXPIN,
    NUMFIREPIX,
    brightness=1.0,
    auto_write=False,
    pixel_order=(1, 0, 2, 3) # For RGBW LEDs
)
PREV = 128


NUMRAINBOWPIX = 85
#RAINBOWPIXPIN = board.NEOPIXEL
RAINBOWPIXPIN = board.A2
RAINBOWSTRIP = neopixel.NeoPixel(
    RAINBOWPIXPIN,
    NUMRAINBOWPIX,
    brightness=0.3,
    auto_write=False,
    pixel_order=(1, 0, 2, 3) # For RGBW LEDs
)
WAIT = 0 # Increase the number to slow down the rainbow (range between 0-1).


async def split(first, second, offset):
    """
    Subdivide a brightness range, introducing a random offset in the middle,
    then call recursively with smaller offsets along the way.
    @param1 first:  Initial brightness value.
    @param1 second: Ending brightness value.
    @param1 offset: Midpoint offset range is +/- this amount max.
    """
    if offset != 0:
        mid = ((first + second + 1) / 2 + random.randint(-offset, offset))
        offset = int(offset / 2)
        await split(first, mid, offset)
        await split(mid, second, offset)
    else:
        level = math.pow(first / 255.0, 2.7) * 255.0 + 0.5
        FIRESTRIP.fill((int(level), int(level / 8), int(level / 48), 0))
        FIRESTRIP.write()


async def fire_fractal(PREV):
    while True:
        LVL = random.randint(64, 191)
        await split(PREV, LVL, 32)
        PREV = LVL
        await asyncio.sleep(WAIT)


async def rainbow_cycle(wait):
    while True:
        for j in range(255):
            for i in range(NUMRAINBOWPIX):
                rc_index = (i * 256 // NUMRAINBOWPIX) + j * 5
                RAINBOWSTRIP[i] = colorwheel(rc_index & 255)
            RAINBOWSTRIP.show()
            await asyncio.sleep(WAIT)


def main():
    led_task1 = asyncio.create_task(fire_fractal(PREV))
    led_task2 = asyncio.create_task(rainbow_cycle(WAIT))

    await asyncio.gather(
        led_task1,
        led_task2
    )


asyncio.run(main())
