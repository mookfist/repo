Mookfist Kodi Repository - 0.2.0 Development Branch
===================================================

Welcome to the Mookfist Kodi repository. Here you will find various addons for the Kodi media center.

This is a development branch. Use at your own risk.

## Installation

To install the repository, you must manually download and install the repository addon.

1. Download https://github.com/mookfist/repo/raw/0.2.0devel/zips/repository.mookfist/repository.mookfist-2.1.zip
2. Goto your Addons screen in Kodi
3. Select "Install from Zip" and select the repository.mookfist-2.0.zip file you downloaded

The repository is now installed and you can now install the various addons available.

## Available Addons

### Functionality

These addons provide additional functionality to Kodi

* [Mookfist Milights](https://github.com/mookfist/repo/tree/0.2.0devel/script.service.mookfist-milights) - A plugin that will control milights or other LimitlessLED-based lights
* [script.module.colorpicker](https://github.com/mookfist/repo/tree/0.2.0devel/script.module.colorpicker) - A ColorPicker dialog window class

### Python Libraries

These addons expose various python libraries for use by the plugins
* [python-requests](https://github.com/mookfist/repo/tree/0.2.0devel/script.module.python-requests) -  [Requests](http://docs.python-requests.org/en/latest/) library for a simpler HTTP API
* [python-qbittorent](https://github.com/mookfist/repo/tree/0.2.0devel/script.module.python-qbittorrent ) - A [python library](https://pypi.python.org/pypi/qbittorrent) for controlling the [QBittorrent](http://www.qbittorrent.org) client
* [python-milights](https://github.com/mookfist/repo/tree/0.2.0devel/script.module.python-milights) - A [python library](https://pypi.python.org/pypi/milight) to speak to Milights and other [LimitlessLED](http://www.limitlessled.com) based products.
* [python-simplejson](https://github.com/mookfist/repo/tree/0.2.0devel/script.module.python-simplejson) - A [python library](https://pypi.python.org/pypi/simplejson) to manipulate JSON
* [python-mookfist-lled-controller](https://github.com/repo/tree/0.2.0devel/script.module.python-mookfist-lled-controller) - A [python library](https://pypi.python.org/pypi/mookfist-lled-controller) to control LimitlessLED-based wifi bridges

### Helper Scripts

These python scripts make managing the repo a bit easier and could be of use to you:

* [addons_repo_generator.py](https://github.com/mookfist/repo/blob/0.2.0devel/addons_repo_generator.py) - Generates the addons.xml the file and zip files from existing addons.
* [pypi_addon_generator](https://github.com/mookfist/repo/blob/0.2.0devel/pypi_addon_generator.py) - Generates a kodi addon from a python library hosted at PyPI
* [git_addon_generator](https://github.com/mookfist/repo/blog/0.2.0devel/git_addon_generator.py) - Prepares a kodi addon from a git repository

## Contributing

Feel free to submit issues and pull requests.
