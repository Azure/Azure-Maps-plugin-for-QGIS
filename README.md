# Azure Maps Creator QGIS Plugin

# DEPRECATED

This plugin is now deprecated with the deprecation of Azure Maps Creator Services. See [Azure Creator Services EOL Annoucement](https://azure.microsoft.com/en-us/updates?id=azure-maps-creator-services-retirement-on-30-september-2025)

--------

## Development

### Prerequisites

- [QGIS v3.8 or greater](https://www.qgis.org/en/site/forusers/download.html)(Long term release recommended)
    1. Install [Plugin Reloader](https://docs.qgis.org/testing/en/docs/pyqgis_developer_cookbook/plugins/plugins.html#tips-and-tricks) plugin for hot reloading.
- [QT Creator](https://www.qt.io/offline-installers) for UI design.
- [Python 3](https://www.python.org/downloads/windows/).

### Build: Windows

1. Install GNU Make

    ```powershell
    choco install make
    ```

2. Update `HOME` variable in Makefile to point to your user's path

3. Update line 2 in `.\src\build\compile.bat` to point to the correct version of QGIS installed

4. Once the previous steps are complete, you may run the following command whenever you want to apply your changes to the plugin directory:

    ```powershell
    make win-deploy 
    ```

5. Restart QGIS or execute Plugin Reloader to reload the updated plugin.

## [Contributing](./CONTRIBUTING.MD)

## [Code Of Conduct](./CODE_OF_CONDUCT.md)

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft 
trademarks or logos is subject to and must follow 
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
