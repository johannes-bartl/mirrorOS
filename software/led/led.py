import board
import time
import neopixel
import sys

n_leds = 30
# j = 10
pixels = neopixel.NeoPixel(board.D18,n_leds,brightness=1, auto_write=False)
if sys.argv[1] == "on":
    # for j in range(n_leds):
        # pixels[j] = (255,255,255)
    pixels.fill((255, 255, 255))
    pixels.show()
if sys.argv[1] == 'off':
    # for j in range(n_leds):
    #     pixels[j] = (0, 0, 0)
    pixels.fill((0,0,0))
    pixels.show()
    time.sleep(0.1)  # Add a small delay to ensure the LEDs are updated
    # pixels.deinit()

    pixels.fill((0, 0, 0))
    pixels.show()
    time.sleep(0.1)  # Add a small delay to ensure the LEDs are updated


    pixels.fill((0,0,0))
    pixels.show()
    time.sleep(0.1)  # Add a small delay to ensure the LEDs are updated
    pixels.deinit()

# for i,c,c2 in zip(range(n_leds),range(0,255,255//30),range(0,255,255//30)[::-1]):
#     print(i,c,c2)
#     pixels[i] = (c,255, c2 )
#     pixels.show()
#     time.sleep(0.1)
#     pixels[i] = (0,0,0)
#     pixels.show()
# for i in range(n_leds)[::-1]:
#     time.sleep(0.03)
#     pixels[i] = (0,0,255 )
#     pixels.show()
#     time.sleep(0.03)
#     pixels[i] = (0,0,0)
#     pixels.show()

