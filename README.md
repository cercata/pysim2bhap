# pysim2bhap
bHaptics support for simulators

## How to use

- Download the lastest [release](https://github.com/cercata/pysim2bhap/releases)
- Unzip it to a folder of your choice
- Enable telemetry for the desired game. Instructions for each game in further sections.
- Launch the game, and the bHaptics player.
- Launch `Sim2bHap.exe`, select a preset or select the options you want, then click run.
   * You can edit the `Sim2bHap.ini` to add your presets for you preferred planes.
   * If you change the aircraft, click stop, select new setting, and click run.

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

## IL-2 Sturmovik: Great Battles

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

## DCS World | Digital Combat Simulator

You must place [`DCS_To_bHap.lua`](https://github.com/cercata/pysim2bhap/blob/main/DCS_To_bHap.lua) in the folder `C:\Users\YOUR USERNAME\Saved Games\DCS\Scripts\Hooks`. If the "Hooks" folder doen's exist, create it. 

This LUA script is based on the wonderfull script from [FlyPT Mover](https://www.flyptmover.com/) by Pedro Antunes, just adding a couple of variables.

Actually it supports 7 patterns in the Vest:

- When the plane aproaches non exceed speed, my upper back starts vibrating gradually.
- When the plane aproaches maximum angle of Attack, my lower back starts vibrating gradually.
- When the RPM exceed threshold, my chest starts vibrating gradually
- When G's exceed threshold, my belly starts vibrating gradually
- When acceleration changes to quickly , all the vest vibrates
- Vibration when flaps and landing gear are moving
- Vibration when you fire the gun or cannons

![Sim2bHapDCS screenshot](/assets/images/Sim2bHapDCS.png)

# War Thunder

No need to configure anything on the game, the game automatically exports data via an HTTP server on port 8111

The same patterns than DCS are supported. 


# Dirt Rally 2

You have to enable udp and set extradata to 3 in file: `Documents\My Games\DiRT Rally 2.0\hardwaresettings\hardware_settings_config_vr.xml`

```
<motion_platform>
    <udp enabled="true" extradata="3" ip="127.0.0.1" port="20777" delay="1" />
```

Actually it supports 3 patterns in the Vest:

- When the RPM exceed threshold, my chest starts vibrating gradually
- When acceleration changes to quickly , all the vest vibrates
- Vibration when you change gear

# Raceroom Racing Experience

No need to configure anything on the game, the game automatically exports data via shared memory

Actually it supports 4 patterns in the Vest:

- When the RPM exceed threshold, my chest starts vibrating gradually
- Vibration when you change gear
- When acceleration changes to quickly , the upper of the vest vibrates
- If the suspension moves too fast, the lower part of the best vibrates, only the part close to the wheel(s) moving.

