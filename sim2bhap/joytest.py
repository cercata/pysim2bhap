import pygame
import time

pygame.init()
if not pygame.joystick.get_init():
  pygame.joystick.init()

if False:
  for i in range(pygame.joystick.get_count()):
    joy = pygame.joystick.Joystick(i)
    joy.init()
    print ("joy: {}-> {} {}".format(i, joy.get_name(), joy.get_numbuttons()))
  exit()
    
joy = pygame.joystick.Joystick(1)
#joy.init()
while True:

  pygame.event.pump()
  for i in range(joy.get_numbuttons()):
    print ("{}: {}".format(i, joy.get_button(i)))
  time.sleep(0.5)