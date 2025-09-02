# This code extends the existing Chase class, but renders each bar
# with the same algorithm used by the Commet animation

import math
from adafruit_led_animation.animation import Animation
from adafruit_led_animation.color import BLACK, calculate_intensity
from adafruit_led_animation.animation.chase import Chase

class CometChase(Chase):
    def __init__(
        self, pixel_object, speed, color, size=2, spacing=3, reverse=False, name=None
    ):
        self._color_step = 0.95 / size
        self._comet_colors = []
        for n in range(size):
            self._comet_colors.append(calculate_intensity(color, n * self._color_step + 0.05))

        if reverse:
            self._comet_colors.reverse()

        super().__init__(pixel_object, speed, color, size, spacing, reverse, name)

    def bar_color(self, n, pixel_no=0):  # pylint: disable=unused-argument
        colors = self._comet_colors

        if pixel_no >= self._size:
            return (0,0,0)
        return colors[pixel_no]
