# pysim2bhap
bHaptics support for simulators

## How to use

- Download the lastest [release](https://github.com/cercata/pysim2bhap/releases)
- Unzip it to a folder of your choice
- Enable telemetry for the desired game. Instructions for each game in further sections.
- Launch the game and the bHaptics player.
- Launch `Sim2bHap.exe`, select a preset or select the options you want, then click run.
   * You can edit the `Sim2bHap.ini` to add your presets for you preferred planes.
   * If you change the aircraft, click stop, select new setting, and click run.

## Microsoft Flight Simulator
This has started as a prototype for having some haptics feedback within [MSFS](https://www.flightsimulator.com/), using the [Tactsuit X40](https://www.bhaptics.com/tactsuit/tactsuit-x40) Vest and [Tactosy for arms](https://www.bhaptics.com/tactsuit/tactosy-for-arms) from [bHaptics](https://www.bhaptics.com/). It should work also with the [Tactsuit X16](https://www.bhaptics.com/tactsuit/tactsuit-x16) Vest.

In order to work, you'll need to enable [SimConnect](https://docs.flightsimulator.com/html/Programming_Tools/SimConnect/SimConnect_SDK.htm) in your MSFS installation.

This uses the excellent package [pysimconnect](https://github.com/patricksurry/pysimconnect) from @patricksurry to get the data from the sim.

It supports 6 patterns in the Vest:

- When the plane approaches threshold speed, upper back starts vibrating gradually.
- When the plane approaches maximum angle of attack, my lower back starts vibrating gradually.
- When the RPM exceed a certain threshold, chest starts vibrating gradually.
- When G exceeds a certain threshold, belly starts vibrating gradually.
- When acceleration changes too quickly, all parts of the vest vibrates.
- When flaps and landing gear are moving, all parts of the vest vibrates.

![Sim2bHap screenshot](/assets/images/Sim2bHap.png)

## IL-2 Sturmovik: Great Battles

You need to enable UDP motion and telemetry data by adding the following code to your `data\startup.cfg` file:

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

It supports 7 patterns in the Vest:

- When the plane approaches threshold speed, upper back starts vibrating gradually.
- When the plane approaches maximum angle of attack, my lower back starts vibrating gradually.
- When the RPM exceed a certain threshold, chest starts vibrating gradually.
- When G exceeds a certain threshold, belly starts vibrating gradually.
- When acceleration changes too quickly, all parts of the vest vibrates.
- When flaps and landing gear are moving, all parts of the vest vibrates.
- When you fire a gun or a cannon, or when you get hit, there is vibration in the vest.

![Sim2bHapIL2 screenshot](/assets/images/Sim2bHapIL2.png)

## DCS World | Digital Combat Simulator

You must place [`DCS_To_bHap.lua`](https://github.com/cercata/pysim2bhap/blob/main/DCS_To_bHap.lua) in the folder `C:\Users\YOUR USERNAME\Saved Games\DCS\Scripts\Hooks`. If the "Hooks" folder doen's exist, create it. 

This LUA script is based on the wonderfull script from [FlyPT Mover](https://www.flyptmover.com/) by Pedro Antunes, pluse just adding a couple of variables.

It supports 7 patterns in the Vest:

- When the plane approaches threshold speed, upper back starts vibrating gradually.
- When the plane approaches maximum angle of attack, my lower back starts vibrating gradually.
- When the RPM exceed a certain threshold, chest starts vibrating gradually.
- When G exceeds a certain threshold, belly starts vibrating gradually.
- When acceleration changes too quickly, all parts of the vest vibrates.
- When flaps and landing gear are moving, all parts of the vest vibrates.
- When you fire a gun or a cannon, or when you get hit, there is vibration in the vest.

![Sim2bHapDCS screenshot](/assets/images/Sim2bHapDCS.png)

# War Thunder

There is no need to configure anything in the game, the game automatically exports data via an HTTP server on port 8111.

The same patterns as DCS World are supported. 


# Dirt Rally 2

You have to enable udp and set extradata to 3 in file: `Documents\My Games\DiRT Rally 2.0\hardwaresettings\hardware_settings_config_vr.xml`

```
<motion_platform>
    <udp enabled="true" extradata="3" ip="127.0.0.1" port="20777" delay="1" />
```

It supports 3 patterns in the vest:

- When the RPM exceed a certain threshold, chest starts vibrating gradually.
- When acceleration changes too quickly, all parts of the vest vibrates.
- When you change the gear, there is vibration in the vest. 

# Raceroom Racing Experience

No need to configure anything in the game, the game automatically exports data via shared memory.

It supports 4 patterns in the vest:

- When the RPM exceed a certain threshold, chest starts vibrating gradually.
- When you change the gear, there is vibration in the vest
- When acceleration changes too quickly, the upper part of the vest vibrates.
- If the suspension moves too quickly, the lower part of the vest closer to the wheels moving vibrates. 

# Project Cars 2 and Automobilista 2

Set Shared Memory to Project Cars 2 in Options->System.

It supports 4 patterns in the Vest:

- When the RPM exceed a certain threshold, chest starts vibrating gradually.
- When you change the gear, there is vibration in the vest.
- When acceleration changes too quickly , the upper part of the vest vibrates.
- If the suspension moves too quickly, the lower part of the vest closer to the wheels moving vibrates.

# Thanks

- Thanks to Nickbond for creating the patterns for feet.
- Thanks to Polybass for early testing
