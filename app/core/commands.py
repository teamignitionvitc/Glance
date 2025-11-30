"""
                                        ::                                                      
                                        ::                                                      
                                        ::                                                      
                                        ::                                                      
                                        ::                                                      
    ..    ..........    :.      ::      ::     .........  ..    ..........    ...      .        
    ::    ::            : .:.   ::     .::.       ::      ::    ::       :    :: :.    :        
    ::    ::   ..:::    :   .:. ::    ::::::      ::      ::    ::       :    ::   ::  :        
    ::    ::......::    :      :::    ::::::      ::      ::    ::.......:    ::     :::        
                                      ::::::                                                    
                                      :.::.:                                                    
                         .::::          ::          ::::.                                      
                       .::::::::.       ::       .:::::::::                                    
                       ::::::::::::....::::.....:::::::::::                                    
                        .:::::::::::::::::::::::::::::::::.        

                    Copyright (c) 2025 Ignition Software Department

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3, with the additional restriction
that this software may not be used for commercial purposes without
explicit written permission from the authors.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

"""
####################################################################################################
# File:        commands.py
# Author:      MuhammadRamzy
# Created On:  29-11-2025
#
# @brief       Command pattern implementations for undo/redo functionality.
# @details     Provides command classes for widget and parameter operations.
####################################################################################################
# HISTORY:
#
#       +----- (NEW | MOD | ADD | DEL)
#       |
# No#   |       when       who                  what
# ######+*********+**********+********************+**************************************************
# 000  NEW      29-11-2025  MuhammadRamzy        feat: Redesign AddWidgetDialog with side-by-side
#                                                layout and QStackedWidget
####################################################################################################

####################################################################################################
# Imports

from app.core.history import Command
import copy

####################################################################################################

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
        # Refresh UI after adding widget
        self.main_window.refresh_active_displays_list()
        self.main_window.mark_as_unsaved()

    def undo(self):
        if self.widget_id:
            self.main_window._remove_widget_internal(self.widget_id, self.tab_index)
            # Refresh UI after removing widget
            self.main_window.refresh_active_displays_list()
            self.main_window.mark_as_unsaved()

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
        # Refresh UI after removing widget
        self.main_window.refresh_active_displays_list()
        self.main_window.mark_as_unsaved()

    def undo(self):
        if self.widget_config:
            self.main_window._add_widget_internal(self.widget_config, self.tab_index, restore_id=self.widget_id)
            # Refresh UI after restoring widget
            self.main_window.refresh_active_displays_list()
            self.main_window.mark_as_unsaved()

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
