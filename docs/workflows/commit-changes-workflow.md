# Commit Changes Workflow
Workflow for commiting changes in QGIS


## Signal: on_before_commit_changes
```on_before_commit_changes``` is the signal sent by QGIS when the save button is clicked on Attribute table or commitChanges() is called.
This is the main function we use to handle commits.

## Step 1: Check field validity
Validity of fields is checked whenever new features are added or changes to attributes are made. 
An instance variable ```areAllFieldsValid``` stores the current state of validity of fields. <br/>
First step is to ensure that all fields in changes are valid. 
If not, throw an error and cancel the changes.

## Step 2: Gathers Edits, Deletes and Creates.
Next step is to gather all the edits, deletes and creates. <br/>
Loop through edits, deletes and creates given by QGIS and store the changed features.
These are then passed on to the next function to commit changes.

## Step 3: Rollback Changes
Third step is rolling back all changes.
**All changes** are rolled back, since we were unable to rollback only specific ones. <br/>
QGIS doesn't provide direct access to the edit buffer, so once the changes are in the buffer, we cannot pop them.
More changes can be added to the buffer, however, these changes are applied on the layer. 

## Step 4: Commit changes to Feature Service
All changes are committed sequentially to Feature Service.
- If a request is successful, then the change in applied in QGIS. 
- If it isn't successful, the changed feature is added to a list of features handled in the [Error Handling step](#step-6-handle-error)

No stop if a request is not successful, move on to the next request. <br/>
Since all requests are independent of each other, they can occur in any order. 
    This is because saving can only happen in one feature class at a time, due to QGIS restrictions. <br/>
Used PUT in case of Patch as well, since QGIS returns the full feature, and not just the edited parts.

## Step 5: Apply Updates to QGIS
Handle changes to other fields, if any, due to the creates and edits

## Step 6: Handle Error
Error handling is done at the end. <br/>
All errors are displayed in the dialog box, along with details returned from Feature Service. <br/>
Errors are also logged in an error file, with the file name shown on the dialog box.
    This is in case the user wants to retry.