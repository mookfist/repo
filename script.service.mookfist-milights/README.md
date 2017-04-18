# mookfist-milights Kodi Addon v0.2.0devel

This addon is for controlling LimitlessLED-based lights (including Milights).

Supports bridge versions 4, 5 and 6.

## Installation

To install this plugin, you must install the Mookfist repository, then find the Mooklist Milights under services.

Please visit https://github.com/mookfist/mookfist-repo for more information.

## Setup

Before setting up this plugin, please make sure that your light bulbs are synced to your wifi bridge.

To use the "Testing" features, please save the configuration first then re-open the plugin settings.

### Bridge Configuratoin

Select "Scan for a bridge" to find all available wifi bridges automatically. If for some reason this not work, you can manually configure your bridge's IP address, port number, and version.

| Setting | Description |
|---------|-------------|
| Scan for a bridge | Scans for all available bridges, allowing you to choose one |
| Manually configure bridge | Enable this to manually specify the IP, port number, and version of your wifi bridge |
| IP/Hostname | IP Address of the wifi bridge |
| Port Number | Port number of the wifi bridge. For versions 4 and 5 this is typically 8899, and for version 6 it is 5987 |
| Bridge Version | Version of the wifi bridge. Versions 4 and 5 are compatible with each other but version 6 is not. |

For version 4 and 5, the default port number is 8899. For version 6 it is 5987.

### Group Configuration

You can configure each group with separate settings. Enable each group you want Kodi to control.

| Setting | Description |
|---------|-------------|
| Enable Group | Turn on to allow Kodi to control your lights |
| White | Set the color of the lights to white |
| Color Picker | Use a color picker to choose a color for the lights |
| Brightness | Set the brightness of the lights between 0 and 100 |
| Fading Speed | The speed to fade the lights |

### Tweaking

Here you can adjust various parameters of the plugin. The LimitlessLED wifi bridge is not pefect, and you may need to tweak these settings to find a sweet spot for perfect smoothness.

It's important to note that fading lights is done by sending many brightness commands to reach the desired brightness. The LimitlessLED protocol has no fading feature. Thus, if the interval for a speed setting is 1, then fading out the lights results in sending brightness 100, 99, 98, 97, etc... to the wifi bridge.


| Setting | Description |
|---------|-------------|
| Automatically dim when playing TV shows | If enabled, then the lights will automatically fade out when a TV show episode starts |
| Automatically dim when playing any video other than TV shows | If enabled lights will fade out for any type of video playback except for TV shows |
| Number of times to repeat command | Number of times to repeat a command sent to the wifi bridge. Increasing this value will make transitions slower, but may result in smoother transitions. |
| Number of milliseconds to wait before sending another command | Decreasing this value will make transitions faster, but may result in less smooth transitions. |
| Slow Speed | Interval of brightness steps for a slow speed |
| Medium Speed | Interval of brightness steps for a medium speed |
| Fast Speed | Interval of brightness steps for a fast speed |

### Testing

You can use these tools to test your configuration. Before using them, make sure that you have previously saved your configuration.

You can also enable debug logging to see exactly what is being sent to your wifi bridge.

## Integration with Other Plugins

You can integrate against this plugin via running commands, or sending notifications

### Commands

Groups are either a comma-separated list of group numbers between 1 and 4, or the word 'all' for all enabled groups.

To execute a command from your plugin you can do

```python
import xbmc

xbmc.executebuiltin('RunScript(script.service.mookfist-milights, fade_in, groups=1,2,3)')
```

Each command has a groups parameter that can be a comma separatest list of group numbers betwee 1 and 4 or the word 'all' for all groups (equivalent to `groups=1,2,3,4`).

#### Available Commands

##### Fade In

```
RunScript(script.service.mookfist-milights, fade_in, groups=[groups])
```

Fades in lights for `[groups]`

##### Fade Out

```
RunScript(script.service.mookfist-milights, fade_out, group=[groups])
```

Fades out lights for `[groups]`

##### White

```
RunScript(script.service.mookfist-milights, white, group=[groups])
```

Turns lights to white for `[groups]`

##### Color RGB

```
RunScript(script.service.mookfist-milights, white, groups=[groups] r=[r] g=[g] b=[b])
```

Sets the color for `[groups]`. `[r]` `[g]` `[b]` can be between 0 and 255. Note that not all colors are supported. If the color is a shade of grey, then the color will be set to white with the brightness adjusted.

##### Brightness

```
RunScript(script.service.mookfist-milights, brightness, groups=[groups] brightness=[brightness])
```

Sets the brightness to `[brightness]` for `[groups]`. `[brightness]` can be a value between 0 and 100.

##### On

```
RunScript(script.service.mookfist-milights, on, groups=[groups])
```

Turn on `[groups]`

##### Off

```
RunScript(script.service.mookfist-milights, off, groups=[groups])
```

Turn off `[groups]`


