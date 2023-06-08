# Future Work
These are a few important tasks that can be done in the future.

1. Add automated testing support to QGIS
1. Add metrics to monitor QGIS (Internal)
1. Safe handle and optimize multiple updates on same feature (pre-saving, i.e. simultaneously).
1. Main flow of azure_maps_plugin.py file can be divided into two parts - loading data and editing data. 
    - Seperate the two flows into seperate files to reduce code clutter and clean implementation.
    - Add documentation to explain the two flows and connection between the two.
1. Parallelize edits made for faster user experience
1. Allow cancellation of operations
1. Multi dataset loading
1. Reload single layer
