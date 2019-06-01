import pyautogui
import random, time

while True:
    x = random.randint(100, 600)
    y = random.randint(100, 600)
    pyautogui.moveTo(x, y, duration=0.25)
    time.sleep(2)
