import time
import errno
import struct
import os
from multiprocessing import shared_memory

structInt32    = struct.Struct("@"+"i")
structInt32_2  = struct.Struct("@"+"ii")
structFloat_3  = struct.Struct("@"+"f"*3)

structDouble   = struct.Struct("@"+"d")
structDouble_3 = struct.Struct("@"+"d"*3)
structDouble_4 = struct.Struct("@"+"d"*4)

try:
  shm = shared_memory.SharedMemory("$R3E")
except FileNotFoundError:
  print ("Raceroom not running")
  exit(1)
  
buffer = shm.buf
print (len(buffer))
major, minor = structInt32_2.unpack(bytes(buffer[:8]))
print (f"major: {major} - minor: {minor}")
counter = 0
maxSus = 0
minSus = 0

while True:
  try:
    startTime = time.time()
    timeSim, = structDouble.unpack(bytes(buffer[40:48]))
    counter += 1
    lveloc = structDouble_3.unpack(bytes(buffer[96:120]))
    #accel = structDouble_3.unpack(bytes(buffer[120:144]))
    laccel = structDouble_3.unpack(bytes(buffer[144:168]))
    gForce= structDouble_3.unpack(bytes(buffer[288:312]))
    susVel= structDouble_4.unpack(bytes(buffer[416:448]))
    rps, max_rps, urps = structFloat_3.unpack(bytes(buffer[1340:1352]))
    gear, = structInt32.unpack(bytes(buffer[1352:1356]))
    maxSus = max (maxSus, susVel[0])
    minSus = min (minSus, susVel[0])
    rpm = 9.549297 * rps
    elapsed = time.time() - startTime
    os.system('cls')
    print (f"elapsed: {elapsed}")
    print (f"timeSim: {timeSim}")
    print (f"lveloc:  {lveloc}")
    #print (f"accel:   {accel}")
    print (f"laccel:  {laccel}")
    print (f"gForce:  {gForce}")
    print (f"susVel:  {susVel}")
    print (f"maxSus:  {maxSus}")
    print (f"minSus:  {minSus}")
    print (f"rpm:  {rpm}")
    print (f"rps:  {rps}")
    print (f"max:  {max_rps}")
    print (f"gear:  {gear}")

    time.sleep(0.042)
  except:
    pass
