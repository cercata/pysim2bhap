# pysim2bhap
bHaptics support for simulators
## Microsoft Flight Simulator
This has started as a prototype for having some haptics feedback within [MSFS](https://www.flightsimulator.com/), using the [X40 Vest](https://www.bhaptics.com/tactsuit/tactsuit-x40) and [Tactosy for arms](https://www.bhaptics.com/tactsuit/tactosy-for-arms) from [bHaptics](https://www.bhaptics.com/). It should work also with the [X16 Vest](https://www.bhaptics.com/tactsuit/tactsuit-x16).

In order to work, you'll need to enable [SimConnect](https://docs.flightsimulator.com/html/Programming_Tools/SimConnect/SimConnect_SDK.htm) in your MSFS installation.

This uses the excelent package [pysimconnect](https://github.com/patricksurry/pysimconnect) from @patricksurry to get the data from de sim.
