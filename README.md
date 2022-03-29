# pysim2bhap
bHaptics support for simulators
## Microsoft Flight Simulator
This has started as a prototype for having some haptics feedback within [MSFS](https://www.flightsimulator.com/), using the [Tactsuit X40](https://www.bhaptics.com/tactsuit/tactsuit-x40) Vest and [Tactosy for arms](https://www.bhaptics.com/tactsuit/tactosy-for-arms) from [bHaptics](https://www.bhaptics.com/). It should work also with the [Tactsuit X16](https://www.bhaptics.com/tactsuit/tactsuit-x16) Vest.

In order to work, you'll need to enable [SimConnect](https://docs.flightsimulator.com/html/Programming_Tools/SimConnect/SimConnect_SDK.htm) in your MSFS installation.

This uses the excelent package [pysimconnect](https://github.com/patricksurry/pysimconnect) from @patricksurry to get the data from de sim.

Actually it supports 3 patterns in the Vest:

- When the plane aproaches non exceed speed, my back starts vibrating gradually.
- When the RPM exceed 95%, my chest starts vibrating gradually
- Whem G's exceed 3, my belly starts vibrating gradually

## For distribution without need to install python

pyinstaller Sim2bHap.py  --add-data "scvars.json;." --add-data "scvars_idx.json;." --hidden-import=simconnect -w

![Sim2bHap screenshot](/assets/images/Sim2bHap.png)
