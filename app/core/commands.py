from app.core.history import Command
import copy

class AddWidgetCommand(Command):
    def __init__(self, main_window, widget_config, tab_index):
        self.main_window = main_window
        self.widget_config = widget_config
        self.tab_index = tab_index
        self.widget_id = None # Set after execution

    def execute(self):
        # Logic to add widget
        # We need to call the actual implementation in MainWindow
        # For now, we'll assume MainWindow has a method _add_widget_internal that returns the ID
        self.widget_id = self.main_window._add_widget_internal(self.widget_config, self.tab_index)

    def undo(self):
        if self.widget_id:
            self.main_window._remove_widget_internal(self.widget_id, self.tab_index)

class RemoveWidgetCommand(Command):
    def __init__(self, main_window, widget_id, tab_index):
        self.main_window = main_window
        self.widget_id = widget_id
        self.tab_index = tab_index
        self.widget_config = None # Saved before removal

    def execute(self):
        # Save config before removing
        self.widget_config = self.main_window._get_widget_config(self.widget_id, self.tab_index)
        self.main_window._remove_widget_internal(self.widget_id, self.tab_index)

    def undo(self):
        if self.widget_config:
            self.main_window._add_widget_internal(self.widget_config, self.tab_index, restore_id=self.widget_id)

class UpdateParametersCommand(Command):
    def __init__(self, main_window, old_params, new_params):
        self.main_window = main_window
        self.old_params = copy.deepcopy(old_params)
        self.new_params = copy.deepcopy(new_params)

    def execute(self):
        self.main_window.parameters = copy.deepcopy(self.new_params)
        self.main_window.restart_simulator() # Refresh simulator with new params

    def undo(self):
        self.main_window.parameters = copy.deepcopy(self.old_params)
        self.main_window.restart_simulator()
