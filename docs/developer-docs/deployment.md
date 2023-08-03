# Deployment guidelines

[QGIS Docs to publish plugin](https://plugins.qgis.org/publish/)

## Creating deployment package
1. Delete the previously compiled package plugin. Typically, it would be located at `QGIS_PLUGIN_DIR = C:\Users\<username>\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins``, under the folder AzureMapsCreator.
1. Run compile command to generate the plugin package. Check [Readme.md](../../README.md) for more information.
1. Open the newly compiled plugin directory and make sure there are no log folders.
1. Zip the file (not the contents of the file). The zip file structure should be: AzureMapsCreator.zip > AzureMapsCreator > <azure-maps-creator-plugin-content>.
1. Upload the zip in the upcoming processes. 

## Upload new plugin

1. Get an OSGEO ID from [here](https://www.osgeo.org/community/getting-started-osgeo/osgeo_userid/). This ID is needed to upload a new plugin/make changes to existing one. This is essentially how you login to QGIS Plugin Repository
2. Navigate to [QGIS Plugin Repository](https://plugins.qgis.org/plugins/). Use the upload button to upload the new plugin.
    - QGIS might reach out via email, or via a github issue, if there are any requirements missing. This is true for existing plugin as well. Do keep an eye out for that.
3. Once plugin has been uploaded, wait for approval. Someone will be assigned to your case.

## Update existing plugin
1. To update an existing plugin, navigate to [My Plugins][https://plugins.qgis.org/plugins/my]. Select the plugin to update.
2. You can update an existing version by navigating to versions, and selecting the edit/delete button alongside the version. Date of update doesn't change, fyi.
1. You can add a new version by navigating to manage tab. 
    - Make sure to make changes to the changelog to let users know what was changed. Also write the changes in the QGIS plugin repository changelog, which is available when uploading the new version.
    - Make sure to bump up version in [metada.txt](../../src/metadata.txt)