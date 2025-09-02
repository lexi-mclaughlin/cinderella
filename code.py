# Write your code here :-)
# SPDX-FileCopyrightText: 2018 Kattni Rembor for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""Cinderella"""
import time
import board
import neopixel
import random

from digitalio import DigitalInOut, Direction, Pull
from rainbowio import colorwheel
from adafruit_led_animation.animation.SparklePulse import SparklePulse
from adafruit_led_animation.animation.Sparkle import Sparkle
from adafruit_led_animation.animation.Solid import Solid
from adafruit_led_animation.animation.blink import Blink
from adafruit_led_animation.animation.pulse import Pulse
from adafruit_led_animation.animation.comet import Comet
from adafruit_led_animation.animation.chase import Chase
from adafruit_led_animation.helper import PixelSubset
from adafruit_led_animation.pulse_generator import pulse_generator

from adafruit_led_animation.animation import Animation
from adafruit_led_animation.sequence import AnimationSequence
from adafruit_led_animation.timedsequence import TimedAnimationSequence

from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

from adafruit_bluefruit_connect.packet import Packet
from adafruit_bluefruit_connect.color_packet import ColorPacket
from adafruit_bluefruit_connect.button_packet import ButtonPacket

from adafruit_led_animation.color import calculate_intensity

# This is an animation class I wrote to make each chase string animate like a comet
from comet_chase import CometChase

pixel_pin = board.A4
bodice_pin = board.A5
num_pixels = 253
brightness = 1
max_brightness = 1
min_brightness = .2

# The bodice lights go through less fabric, they need to be dimmer by some fraction
bodice_dimmer = 4.0
min_bodice_brightness = .05

min_pulse_brightness = .2

pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=brightness, auto_write=False)
bodice_pixels = neopixel.NeoPixel(bodice_pin, 27, brightness=brightness / bodice_dimmer, auto_write=False)

hoop_1 = PixelSubset(pixels, 0, 11)
hoop_2 = PixelSubset(pixels, 11, 26)
hoop_3 = PixelSubset(pixels, 26, 42)
hoop_4 = PixelSubset(pixels, 42, 60)
hoop_5 = PixelSubset(pixels, 60, 81)
hoop_6 = PixelSubset(pixels, 81, 104)
hoop_7 = PixelSubset(pixels, 104, 130)
hoop_8 = PixelSubset(pixels, 130, 158)
hoop_9 = PixelSubset(pixels, 158, 188)
hoop_10 = PixelSubset(pixels, 188, 219)
hoop_11 = PixelSubset(pixels, 220, num_pixels)

bodice_top = PixelSubset(bodice_pixels, 0, 13)
bodice_bottom = PixelSubset(bodice_pixels, 13, 27)

hoops = [hoop_1, hoop_2, hoop_3, hoop_4, hoop_5, hoop_6, hoop_7, hoop_8, hoop_9, hoop_10, hoop_11]

OFFWHITE = (253, 150, 100)
WARMWHITE = (253, 140, 90)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# define the idle animations
sparkle = Sparkle(pixels, speed=.05, color=OFFWHITE, num_sparkles=3)
sparkle_bodice = Sparkle(bodice_pixels, speed=.15, color=OFFWHITE, num_sparkles=2)

sparkle_pulse = SparklePulse(pixels, speed=.04, period=3, color=OFFWHITE)
sparkle_pulse_bodice = SparklePulse(bodice_pixels, speed=.2, period=6, color=WARMWHITE,
                                    min_intensity=min_pulse_brightness)

chase = CometChase(pixels, speed=.08, color=OFFWHITE, size=15, spacing=60)
chase_bodice_top = CometChase(bodice_top, speed=.06, color=OFFWHITE, size=6, spacing=25, reverse=True)
chase_bodice_bottom = CometChase(bodice_bottom, speed=.06, color=OFFWHITE, size=6, spacing=20)

long_comet = Comet(pixels, speed=0.05, color=OFFWHITE, tail_length=260, bounce=False, ring=True)
long_comet_bodice_top = Comet(bodice_top, speed=0.1, color=OFFWHITE, tail_length=37, bounce=False, ring=True,
                              reverse=True)
long_comet_bodice_bottom = Comet(bodice_bottom, speed=0.1, color=OFFWHITE, tail_length=37, bounce=False, ring=True)

solid = Solid(pixels, color=OFFWHITE)
solid_bodice = Solid(bodice_pixels, color=OFFWHITE)

off = Solid(pixels, color=BLACK)
off_bodice = Solid(bodice_pixels, color=BLACK)


def timedAnimation(animation, interval):
    timedAnimations([animation], interval)


def timedAnimations(animations, interval):
    start = time.monotonic()
    while True:
        if time.monotonic() - start >= interval:
            break
        for animation in animations:
            animation.animate()


def light_1():
    interval = .7
    blackout()

    comet_top = Comet(bodice_top, speed=0.03 / (bodice_pixels.n / 15), color=OFFWHITE,
                      tail_length=round(bodice_pixels.n / 1.5), bounce=False, ring=True, reverse=True)
    comet_bottom = Comet(bodice_bottom, speed=0.03 / (bodice_pixels.n / 15), color=OFFWHITE,
                         tail_length=round(bodice_pixels.n / 1.5), bounce=False, ring=True)
    pulse = Pulse(bodice_pixels, speed=.02, period=interval, color=OFFWHITE, min_intensity=min_pulse_brightness)

    timedAnimations([comet_top, comet_bottom], interval)
    timedAnimation(pulse, interval / 2.0)
    for hoop in hoops:
        comet = Comet(hoop, speed=0.03 / (hoop.n / 15), color=OFFWHITE, tail_length=round(hoop.n / 1.5), bounce=False,
                      ring=True)
        pulse = Pulse(hoop, speed=.02, period=interval, color=OFFWHITE)

        timedAnimation(comet, interval)
        timedAnimation(pulse, interval / 2.0)

        hoop.fill(OFFWHITE)
    timedAnimations([solid, solid_bodice], 2)


def light_2():
    blackout()

    start = pixels.brightness / 10
    pulse = Pulse(pixels, speed=.01, period=6, color=OFFWHITE, min_intensity=start)
    chase = CometChase(pixels, speed=0.04, color=OFFWHITE, size=6, spacing=15)

    chase_bodice_top = CometChase(bodice_top, speed=0.04, color=WARMWHITE, size=5, spacing=15, reverse=True)
    chase_bodice_bottom = CometChase(bodice_bottom, speed=0.04, color=WARMWHITE, size=5, spacing=15)

    timedAnimations([chase, chase_bodice_top, chase_bodice_bottom], 5)
    fade_on_by_hoop(.3)
    timedAnimations([solid, solid_bodice], 2)


def light_3():
    blackout()

    sparkle = Sparkle(pixels, speed=.05, color=OFFWHITE, num_sparkles=10)
    sparkle_bodice = Sparkle(bodice_pixels, speed=.1, color=OFFWHITE, num_sparkles=1)
    pulse = Pulse(pixels, speed=.01, period=6, color=OFFWHITE, min_intensity=.15)
    pulse_bodice = Pulse(bodice_pixels, speed=.01, period=6, color=WARMWHITE, min_intensity=.2)

    timedAnimations([sparkle, sparkle_bodice], 5)
    timedAnimations([pulse, pulse_bodice], 3)
    timedAnimations([solid, solid_bodice], 2)


def light_4():
    blackout()

    comet = Comet(pixels, speed=0.015, color=OFFWHITE, tail_length=30, bounce=False, ring=False)
    pulse = Pulse(pixels, speed=.01, period=6, color=OFFWHITE)

    comet_bodice_top = Comet(bodice_top, speed=0.01, color=WARMWHITE, tail_length=7, bounce=False, ring=False,
                             reverse=True)
    comet_bodice_bottom = Comet(bodice_bottom, speed=0.01, color=WARMWHITE, tail_length=5, bounce=False, ring=False)
    pulse_bodice = Pulse(bodice_pixels, speed=.001, period=6, color=WARMWHITE, min_intensity=min_pulse_brightness)

    timedAnimation(comet_bodice_top, .4)
    bodice_top.fill(BLACK)
    bodice_top.show()

    timedAnimation(comet_bodice_bottom, .4)
    bodice_bottom.fill(BLACK)
    bodice_bottom.show()

    timedAnimation(comet, 4.75)
    timedAnimations([pulse, pulse_bodice], 3)
    timedAnimations([solid, solid_bodice], 2)


def fade_on_by_hoop(interval):
    blackout()

    pulse = Pulse(bodice_pixels, speed=.005, period=interval * 3, color=WARMWHITE, min_intensity=min_pulse_brightness)
    timedAnimation(pulse, interval * 1.5)
    for hoop in hoops:
        pulse = Pulse(hoop, speed=.01, period=interval * 2, color=OFFWHITE)
        timedAnimation(pulse, interval)
        hoop.fill(OFFWHITE)


def blackout():
    pixels.fill(BLACK)
    pixels.show()
    bodice_pixels.fill(BLACK)
    bodice_pixels.show()


light_up_sequences = [light_1, light_2, light_3, light_4]
idle_animations = [[sparkle_pulse, sparkle_pulse_bodice], [chase, chase_bodice_top, chase_bodice_bottom],
                   [sparkle, sparkle_bodice],
                   [long_comet, long_comet_bodice_top, long_comet_bodice_bottom], [solid, solid_bodice]]
idle_animations_bodice = [sparkle_pulse_bodice]

# Setup Bluetooth
ble = BLERadio()
ble.name = "BibbityBobbityBoo"
uart = UARTService()
advertisement = ProvideServicesAdvertisement(uart)
ble.start_advertising(advertisement)

# Setup Button
btn = DigitalInOut(board.A1)
btn.pull = Pull.UP  # up is truthy, down is falsey
prev_button_state = btn.value

startup = True
is_off = False
idle_index = 0

while True:

    if not ble.connected and not ble.advertising:
        ble.start_advertising(advertisement)

    if startup:
        random.choice(light_up_sequences)()
        startup = False

    # button trigger
    if btn.value != prev_button_state and not btn.value:
        if not is_off:
            is_off = True
        else:
            startup = True
            is_off = False
    prev_button_state = btn.value

    if is_off:
        pixels.fill(BLACK)
        pixels.show()
        bodice_pixels.fill(BLACK)
        bodice_pixels.show()

    if ble.connected and uart.in_waiting:
        packet = Packet.from_stream(uart)
        if isinstance(packet, ButtonPacket) and packet.pressed:
            if not is_off:
                if packet.button == ButtonPacket.BUTTON_1:
                    light_1()
                elif packet.button == ButtonPacket.BUTTON_2:
                    light_2()
                elif packet.button == ButtonPacket.BUTTON_3:
                    light_4()
                elif packet.button == ButtonPacket.BUTTON_4:
                    is_off = True
                elif packet.button == ButtonPacket.DOWN:
                    pixels.brightness = max(pixels.brightness - .05, min_brightness)
                    bodice_pixels.brightness = max(
                        bodice_pixels.brightness - (.05 / bodice_dimmer),
                        min_bodice_brightness
                    )
                elif packet.button == ButtonPacket.UP:
                    pixels.brightness = min(pixels.brightness + .05, max_brightness)
                    bodice_pixels.brightness = min(
                        max(pixels.brightness / bodice_dimmer, min_bodice_brightness),
                        max_brightness / bodice_dimmer
                    )
                elif packet.button == ButtonPacket.RIGHT:
                    idle_index = (idle_index + 1) % len(idle_animations)
                    blackout()
                elif packet.button == ButtonPacket.LEFT:
                    idle_index = (idle_index - 1) % len(idle_animations)
                    blacktou

            elif packet.button == ButtonPacket.BUTTON_4:
                is_off = False
                light_2()

    if not is_off:
        for animation in idle_animations[idle_index]:
            animation.animate()



