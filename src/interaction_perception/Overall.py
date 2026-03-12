#This is for the GUI :)
#In progress keep out...

#############----------------- VARIABLES ----------------####################

#Introduced at:
#Pass Level

#Credit Level

#Distinction Level

#High Distinction Level


##############----------------- FUNCTIONS ----------------####################
#Pass Goals
#- End-effector Override command (Override_open , Override_closed) 

def GUI():
    #GUI code here
    pass

def ee_override(GUI_EE_BUTTON):
    if(GUI_EE_BUTTON == True):
        ee_override_command = True

    return ee_override_command

#Credit Goals
# - Camera Feed Displayed in GUI
# - Display robot state on GUI e.g. “Picking Up, Releasing, Moving to Block”

#Distinction Goals
# - User input in GUI to change future block placement goal positions (1 of 3 of top level)

#High Distinction Goals
# - GUI togglable E-stop (engaged, Released)

#Other Goals
# - Define Order of Goal Blocks
