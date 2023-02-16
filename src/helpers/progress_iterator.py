from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class ProgressIterator:
    """A class used to generate a progress dialog w/ an iterative method."""

    def __init__(self, count=100, msg="", window_title=""):
        """
        Parameters
        ----------

        count : int
            The count of progress items.
            Ex. If count is 4 then progress bar would be in the sequence of
                0% 25% 50% 75% 100%
        msg : str
            The initial message to show on the dialog
        window_title: str
            The title of this dialog window
        """
        if not isinstance(count, int):
            raise Exception("ProgressIterator: 'count' parameter must be an integer.")
        if count < 1:
            raise Exception(
                "ProgressIterator: 'count' parameter value must be greater than 0."
            )

        self.count = count
        self.value = 0
        self.on_cancel_func = None

        self.progress = QProgressDialog(msg, "Cancel", 0, count)
        self.progress.setAutoClose(True)
        self.progress.setWindowTitle(window_title)

        QApplication.processEvents()

    def next(self, msg=""):
        """Increment progress bar & update the message.

        Parameters
        ----------
        msg : str
            The message to show on the progress dialog
        """
        if self.value >= self.count or self.progress.wasCanceled():
            return

        self.value += 1
        self.progress.setLabelText(msg)
        self.progress.setValue(self.value)
        QApplication.processEvents()

    def set_message(self, msg=""):
        """Sets the progress message without incrementing the progress bar.

        Parameters
        ----------
        msg : str
            The message to show on the progress dialog
        """
        self.progress.setLabelText(msg)
        QApplication.processEvents()

    def set_error(self, msg=""):
        """Sets the progress message without incrementing the progress bar.
        'Cancel' button will change to 'Close' button.

        Parameters
        ----------
        msg : str
            The message to show on the progress dialog
        """
        self.progress.setLabelText(msg)
        self.progress.setCancelButtonText("Close")
        QApplication.processEvents()

    def on_cancel(self, func):
        """Function to be invoked when progress is canceled by a user

        Parameters
        ----------
        func : function
            The function to execute on cancel
        """
        if self.on_cancel_func:
            self.progress.canceled.disconnect(self.on_cancel_func)

        self.progress.canceled.connect(func)
        self.on_cancel_func = func
        QApplication.processEvents()

    def _get_progress_dialog(self):
        return self.progress

    def close(self):
        """Closes the progress iterator."""
        self.progress.cancel()