from bisect import bisect, bisect_left
from sys import maxsize
from qgis.core import *


class LevelPicker:
    """A class that maintains level ordinals in a sorted manner."""

    def __init__(self, qComboBoxes, prefix="Level"):
        """
        Parameters
        ----------

        qComboBoxes : array
            Array of QComboBox to maintain level picker levels.
        prefix: string
            Prefix to attach to QComboBox items
        """
        if not isinstance(qComboBoxes, list):
            raise TypeError("LevelPicker: 'qComboboxes' parameter must be an array.")
        if not isinstance(prefix, str):
            raise TypeError("LevelPicker: 'prefix' parameter must be a string.")

        for qComboBox in qComboBoxes:
            if (
                not callable(getattr(qComboBox, "blockSignals", None))
                or not callable(getattr(qComboBox, "insertItem", None))
                or not callable(getattr(qComboBox, "removeItem", None))
                or not callable(getattr(qComboBox, "currentIndexChanged", None))
            ):
                raise TypeError(
                    "LevelPicker: 'qComboboxes' must be a list of QComboBox"
                )

        for qComboBox in qComboBoxes:
            qComboBox.currentIndexChanged.connect(self._picker_level_changed)

        self.qComboBoxes = qComboBoxes
        self.prefix = prefix
        self.levels = []
        self.levels_set = set()
        self.current_index = 0

        # Add a placeholder text to QComboBox(es)
        self._toggle_placeholder(True)

    def append(self, value):
        """Adds a value to picker_levels if does not exist.
            Updates QCombobox(es) which are passed in initialization.

        Parameters
        ----------
        value : str
            Value to remove from picker_levels
        """
        if not isinstance(value, str) and not isinstance(value, int):
            raise TypeError(
                "PickerLevels: 'value' parameter must be a string or an integer."
            )
        inserted_value = int(value)

        # Value already exists - terminate
        if inserted_value in self.levels_set:
            return

        # Find the previously set value ( Stored for updating the QComboBox index if necessary )
        selected_value = -maxsize
        if len(self.levels) > 0 and len(self.qComboBoxes) > 0:
            selected_value = self.levels[self.qComboBoxes[0].currentIndex()]

        # Remove placeholder text if appending
        if len(self.levels) == 0:
            self._toggle_placeholder(False)

        # Append value
        insert_index = bisect(self.levels, inserted_value)
        self.levels.insert(insert_index, inserted_value)
        self.levels_set.add(inserted_value)
        insert_item = self.prefix + " " + str(inserted_value)
        for qComboBox in self.qComboBoxes:
            qComboBox.blockSignals(True)
            qComboBox.insertItem(insert_index, insert_item)
            qComboBox.blockSignals(False)

        # Keep selected index for QComboBox(es) as the previously selected value
        if selected_value > inserted_value:
            for qComboBox in self.qComboBoxes:
                qComboBox.setCurrentIndex(self.current_index + 1)

    def extend(self, value_list):
        for value in value_list:
            self.append(value)

    def remove(self, value):
        """Removes a value from picker_levels if exists.
            Updates QCombobox(es) which are passed in initialization.

        Parameters
        ----------
        value : str
            Value to remove from picker_levels
        """
        if not isinstance(value, str) or not isinstance(value, int):
            raise TypeError(
                "PickerLevels: 'value' parameter must be a string or an integer."
            )
        deleted_value = int(value)

        # Value already exists - terminate
        if deleted_value not in self.levels:
            return

        # Find the previously set value ( Stored for updating the QComboBox index if necessary )
        selected_value = maxsize
        if len(self.levels) > 0 and len(self.qComboBoxes) > 0:
            selected_value = self.levels[self.current_index]

        # Remove value
        remove_index = bisect(self.levels, deleted_value)
        del self.levels[remove_index]
        self.levels_set.remove(deleted_value)
        for qComboBox in self.qComboBoxes:
            qComboBox.blockSignals(True)
            qComboBox.removeItem(remove_index)
            qComboBox.blockSignals(False)

        # Keep selected index for QComboBox(es) as the previously selected value
        # Likewise reset the index if item has been deleted
        if selected_value >= deleted_value:
            selected_index = self._index_of(selected_value)
            if selected_index == -1:
                # Find the first zero or positive level ordinal
                selected_index = bisect_left(self.levels, 0)
            for qComboBox in self.qComboBoxes:
                qComboBox.setCurrentIndex(selected_index)

            # Enable placeholder text if there are no items
        if len(self.levels) == 0:
            self._toggle_placeholder(True)

    def clear(self):
        self.levels = []
        self.levels_set = set()

        for qComboBox in self.qComboBoxes:
            qComboBox.blockSignals(True)
            qComboBox.clear()
            qComboBox.blockSignals(False)
        self._toggle_placeholder(True)

    def get_ordinal(self, index=-1):
        """Returns the ordinal value of given level picker index.
            If no index or an invalid index is provided, returns current ordinal value.

        Parameters
        ----------
        index : int
            Level picker index to query ordinal
        """
        if index < 0 or index >= len(self.levels):
            return self.levels[self.current_index]
        else:
            return self.levels[index]

    def get_index(self):
        return self.current_index

    def _get_base_levels(self):
        """Returns a copy of levels array."""
        return self.levels.copy()

    def _toggle_placeholder(self, toggle):
        """NOTE: Assumes no items are inside qComboBoxes."""
        if toggle:
            for qComboBox in self.qComboBoxes:
                message = "-" if len(self.prefix) == 0 else "  -"
                qComboBox.blockSignals(True)
                qComboBox.setEnabled(False)
                qComboBox.addItem(self.prefix + message)
                qComboBox.blockSignals(False)
        else:
            for qComboBox in self.qComboBoxes:
                qComboBox.blockSignals(True)
                qComboBox.setEnabled(True)
                qComboBox.clear()
                qComboBox.blockSignals(False)

    def _index_of(self, value):
        """Returns the index of the value.
        -1 if not found.
        """
        index = bisect_left(self.levels, value)
        if index >= len(self.levels):
            return -1
        return index

    def _picker_level_changed(self, index):
        if self.current_index == index:
            return

        # Synchronize other QComboBox(es) currentIndices
        for qComboBox in self.qComboBoxes:
            qComboBox.setCurrentIndex(index)

        self.current_index = index

    def set_base_ordinal(self, value):
        """Sets currentIndex that closest matches of the value.

        Parameters
        ----------
        value : int or str
            Level picker index to query ordinal
        """
        index = bisect_left(self.levels, int(value))
        self._picker_level_changed(index)
