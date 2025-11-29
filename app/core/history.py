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
# File:        history.py
# Author:      MuhammadRamzy
# Created On:  29-11-2025
#
# @brief       Command history for undo/redo functionality.
# @details     Implements command pattern for reversible operations.
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

from typing import List, Any, Callable, Optional

####################################################################################################

class Command:
    """
    @brief Abstract base class for all undoable commands.
    """
    def execute(self):
        raise NotImplementedError

    def undo(self):
        raise NotImplementedError

class CommandHistory:
    """
    @brief Manages the history of executed commands for Undo/Redo.
    """
    def __init__(self, limit: int = 50):
        self._history: List[Command] = []
        self._redo_stack: List[Command] = []
        self._limit = limit

    def push(self, command: Command):
        """Execute a command and add it to history."""
        command.execute()
        self._history.append(command)
        self._redo_stack.clear() # Clear redo stack on new action
        
        if len(self._history) > self._limit:
            self._history.pop(0)

    def undo(self):
        """Undo the last command."""
        if not self._history:
            return
        
        command = self._history.pop()
        command.undo()
        self._redo_stack.append(command)

    def redo(self):
        """Redo the last undone command."""
        if not self._redo_stack:
            return
            
        command = self._redo_stack.pop()
        command.execute()
        self._history.append(command)

    def can_undo(self) -> bool:
        return len(self._history) > 0

    def can_redo(self) -> bool:
        return len(self._redo_stack) > 0

    def clear(self):
        self._history.clear()
        self._redo_stack.clear()
