mookfist-milights Kodi Addon v0.2.0devel
========================================

This addon is for controlling LimitlessLED-based lights (including Milights).

This is a development branch for the new v0.2.0 release. This release should include support for v6 bridges, along with a different form of configuration and speed control.


Supports LimitlessLED protocol v4 only.

Fading is done by sending commands to adjust the brightness until the target brightness is reached. In my testing, this can sometimes result in some funky behavior. Limitless LED does not have speed control for fading.

So when configuring this addon, you may want to experiment a bit to find the sweet spot.

Integration with Other Plugins
==============================

You can execute fade commands from other plugins by doing this:

```RunScript(special://home/addons/script.service.mookfist-milights/cmd.py fade_in 1 50)```

The arguments are:

1. fade_in or fade_out
2. group number or the word 'all' for all groups
3. target brightness or use -1 to use configured min/max brightness

Additioanl integration examples are available in /integrations

Configuration
=============

General Settings
 - Host: IP/hostname of the wifi bridge.
 - Port: Port number of the wifi bridge (usually should be 8899)
 - Scan for Wifi Bridge will scan your network for available bridges. It currently only supports one bridge. If one is found then host and port are automatically filled in.
 - Bulb Type: Choose which type of LED bulb you have. It's expected that all groups have the same type
 - Command Delay: The delay in milliseconds between each command sent to the wifi bridge
 - Enable Logging: IF true, milights will log information to your kodi.log file
 - Enable Group 1 - 4: IF enabled, the addon will send commands for that group

Global Settings
 - Set Brightness at Startup: if enabled, then your lights will be set to the maximum brightness value when Kodi starts
 - Fading Speed: How fast do you want the brightness to fade when fading in and out
 - Max/Min Brightness: How bright and dark you want the lights to get.
 - Enable Color: Kodi will change the colors of lights
 - Red/Green/Blue values: Set the RGB values for the color you want.
 - Enable Custom Pause Settings: If this is enabled, then you can have different settings when pausing a video then when playing.
   - Fading Speed: How fast you want a video to fade in and out when a video is paused/resumed
   - Pause Delay: How long to wait to fade in the lights after a video is paused

Testing
 - Make sure everything is setup by selecting Fade In or Fade Out to control the lights

Movies
 - If enabled, lights will fade in and out when playing movies. IT should be noted however, that unless a video is marked as a "TV show", ALL videos are movies, including video addons. I need to investigate a better way of determining whether you are actually watching a movie or not.

TV Shows
 - If enabled, lights will fade in and out when playing TV shows.


You can manually set the host and port number of your wifi bridge, or use the Scan feature to automatically detect it. The scan feature currently only supports one bridge.

You can set the starting colors and brightness as well. These will be applied every time Kodi starts.

You have four fade speeds: Immediate, Fast, Medium, and Slow.
