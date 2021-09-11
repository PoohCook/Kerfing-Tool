#Author-Pooh
#Description-Apply a kerf to a selected profile for laser cutting

import adsk.core, adsk.fusion, adsk.cam, traceback
from . import NS
from . import PT

_app = None
_ui  = None
_handlers = []


class MyCommandExecutePreviewHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        global _app, _ui, _panel
        try:
            cmdArgs = adsk.core.CommandEventArgs.cast(args)
            inputs = cmdArgs.command.commandInputs
            selector = inputs.itemById("profile_select")
            if selector.selectionCount > 0:
                selectedProfile = adsk.fusion.Profile.cast(selector.selection(0).entity)

                profileTools = PT.ProfileTools()
                kerf_width = inputs.itemById("kerf_width").value
                profileTools.offsetProfiles(selectedProfile, kerf_width)

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))                

# Event handler that reacts to when the command is destroyed. This terminates the script.            
class MyCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        global _app, _ui
        try:
            cmdArgs = adsk.core.CommandEventArgs.cast(args)
            inputs = cmdArgs.command.commandInputs
            selector = inputs.itemById("profile_select")
            selectedProfile = adsk.fusion.Profile.cast(selector.selection(0).entity)

            profileTools = PT.ProfileTools()
            kerf_width = inputs.itemById("kerf_width").value
            profileTools.offsetProfiles(selectedProfile, kerf_width)

        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Event handler that reacts to when the command is destroyed. This terminates the script.            
class MyCommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        global _app, _ui
        try:
            # When the command is done, terminate the script
            # This will release all globals which will remove all event handlers
            cmdArgs = adsk.core.CommandEventArgs.cast(args)

            adsk.terminate()
        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Event handler that creates my Command.
class MyCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        global _app, _ui
        try:
            # Get the command that was created.
            cmd = adsk.core.Command.cast(args.command)

            # Connect to the command destroyed event.
            onDestroy = MyCommandDestroyHandler()
            cmd.destroy.add(onDestroy)
            _handlers.append(onDestroy)

            # Connect to the execute event.           
            onExecute = MyCommandExecuteHandler()
            cmd.execute.add(onExecute)
            _handlers.append(onExecute) 

            # # Connect to the input changed event.           
            # onInputChanged = MyCommandInputChangedHandler()
            # cmd.inputChanged.add(onInputChanged)
            # _handlers.append(onInputChanged)    

            onExecutePreview = MyCommandExecutePreviewHandler()
            cmd.executePreview.add(onExecutePreview)
            _handlers.append(onExecutePreview)        

            # Get the CommandInputs collection associated with the command.
            inputs = cmd.commandInputs

            # Create a selection input.
            selectionInput = inputs.addSelectionInput('profile_select', 'Profile', 'Profile to Kern')
            selectionInput.addSelectionFilter(adsk.core.SelectionCommandInput.Profiles)
            selectionInput.setSelectionLimits(1,1)

            inputs.addValueInput('kerf_width', 'Kerf width', 'mm', adsk.core.ValueInput.createByString("kerf_width"))

        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def run(context):
    try:
        global _app, _ui
        _app = adsk.core.Application.get()
        _ui = _app.userInterface

        # Get the existing command definition or create it if it doesn't already exist.
        cmdDef = _ui.commandDefinitions.itemById('cmdKerfingTool')
        if not cmdDef:
            cmdDef = _ui.commandDefinitions.addButtonDefinition('cmdKerfingTool', 
                                                                'Kerf Selected Profile',
                                                                'My Second command')

        # Connect to the command created event.
        onCommandCreated = MyCommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        _handlers.append(onCommandCreated)

        # Execute the command definition.
        cmdDef.execute()

        # Prevent this module from being terminated when the script returns.
        adsk.autoTerminate(False)
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))