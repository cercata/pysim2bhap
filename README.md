# pysim2bhap
bHaptics support for simulators
## Microsoft Flight Simulator
This has started as a prototype for having some haptics feedback within [MSFS](https://www.flightsimulator.com/), using the [Tactsuit X40](https://www.bhaptics.com/tactsuit/tactsuit-x40) Vest and [Tactosy for arms](https://www.bhaptics.com/tactsuit/tactosy-for-arms) from [bHaptics](https://www.bhaptics.com/). It should work also with the [Tactsuit X16](https://www.bhaptics.com/tactsuit/tactsuit-x16) Vest.

In order to work, you'll need to enable [SimConnect](https://docs.flightsimulator.com/html/Programming_Tools/SimConnect/SimConnect_SDK.htm) in your MSFS installation.

This uses the excelent package [pysimconnect](https://github.com/patricksurry/pysimconnect) from @patricksurry to get the data from de sim.

Actually it supports 6 patterns in the Vest:

- When the plane aproaches non exceed speed, my upper back starts vibrating gradually.
- When the plane aproaches maximum angle of Attack, my lower back starts vibrating gradually.
- When the RPM exceed threshold, my chest starts vibrating gradually
- When G's exceed threshold, my belly starts vibrating gradually
- When acceleration changes to quickly , all the vest vibrates
- Vibration when flaps and landing gear are moving

![Sim2bHap screenshot](/assets/images/Sim2bHap.png)

## IL2 Battle of Series

You need to enable UDP motion and telemetry data adding this to your `data\startup.cfg` file:

```
[KEY = motiondevice]
	addr = "127.0.0.1"
	decimation = 2
	enable = true
	port = 29373
[END]

[KEY = telemetrydevice]
	addr = "127.0.0.1"
	decimation = 2
	enable = true
	port = 29373
[END]
```

Actually it supports 7 patterns in the Vest:

- When the plane aproaches non exceed speed, my upper back starts vibrating gradually.
- When the plane aproaches maximum angle of Attack, my lower back starts vibrating gradually.
- When the RPM exceed threshold, my chest starts vibrating gradually
- When G's exceed threshold, my belly starts vibrating gradually
- When acceleration changes to quickly , all the vest vibrates
- Vibration when flaps and landing gear are moving
- Vibration when you fire the gun or cannons, and when you get hit

![Sim2bHapIL2 screenshot](/assets/images/Sim2bHapIL2.png)
