from time import sleep
from simconnect import SimConnect, PERIOD_VISUAL_FRAME
import os

varList = ["GENERAL ENG PCT MAX RPM:1", "AIRSPEED MACH", "BARBER POLE MACH",
           "ACCELERATION BODY X", "ACCELERATION BODY Y", "ACCELERATION BODY Z", 
           "SIM ON GROUND", "TRAILING EDGE FLAPS LEFT PERCENT", "LEFT WHEEL RPM", 
           "GEAR LEFT POSITION", "GEAR RIGHT POSITION", "G FORCE", "TITLE"]
ValueDict = {}

# open a connection to the SDK
# or use as a context via `with SimConnect() as sc: ... `
sc = SimConnect()

# subscribing to one or more variables is much more efficient,
# with the SDK sending updated values up to once per simulator frame.
# the variables are tracked in `datadef.simdata`
# which is a dictionary that tracks the last modified time
# of each variable.  changes can also trigger an optional callback function
datadef = sc.subscribe_simdata(
    varList,
    # request an update every ten rendered frames
    period=PERIOD_VISUAL_FRAME,
    interval=1,
)
print("Inferred variable units", datadef.get_units())

# track the most recent data update
latest = datadef.simdata.latest()

while True:


    # wait a bit...
    sleep(0.01)

    # pump the SDK event queue to deal with any recent messages
    while sc.receive():
        pass

    # show data that's been changed since the last update
    #print(f"Updated data {datadef.simdata.changedsince(latest)}")
    
    for varName in datadef.simdata:
      ValueDict[varName] = datadef.simdata[varName]

    latest = datadef.simdata.latest()
    #print (datadef.simdata)
    #exit()
    os.system("cls")
    for varName in varList: 
      if varName in ValueDict:
        print ("{:>40s} - {}".format(varName, datadef.simdata[varName]))


# explicity close the SDK connection
sc.Close()