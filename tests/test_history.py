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
# File:        test_history.py
# Author:      MuhammadRamzy
# Created On:  29-11-2025
#
# @brief       Unit tests for command history.
# @details     Tests undo/redo functionality.
####################################################################################################
# HISTORY:
#
#       +----- (NEW | MOD | ADD | DEL)
#       |
# No#   |       when       who                  what
# ######+*********+**********+********************+**************************************************
# 000  NEW      29-11-2025  MuhammadRamzy        feat: Redesign AddWidgetDialog with side-by-side layout and QStackedWidget
####################################################################################################

####################################################################################################
# Imports

import pytest
from app.core.history import CommandHistory, Command

class MockCommand(Command):
    def __init__(self, value, target_list):
        self.value = value
        self.target_list = target_list

    def execute(self):
        self.target_list.append(self.value)

    def undo(self):
        self.target_list.remove(self.value)

def test_command_history():
    history = CommandHistory()
    target_list = []

    # Test Push/Execute
    cmd1 = MockCommand(1, target_list)
    history.push(cmd1)
    assert target_list == [1]
    assert history.can_undo()
    assert not history.can_redo()

    # Test Undo
    history.undo()
    assert target_list == []
    assert not history.can_undo()
    assert history.can_redo()

    # Test Redo
    history.redo()
    assert target_list == [1]
    assert history.can_undo()
    assert not history.can_redo()

    # Test Limit
    limit_history = CommandHistory(limit=2)
    limit_history.push(MockCommand(1, target_list))
    limit_history.push(MockCommand(2, target_list))
    limit_history.push(MockCommand(3, target_list))
    
    assert len(limit_history._history) == 2
    assert limit_history._history[0].value == 2
    assert limit_history._history[1].value == 3

def test_redo_stack_clear():
    history = CommandHistory()
    target_list = []

    history.push(MockCommand(1, target_list))
    history.undo()
    assert history.can_redo()

    # Pushing new command should clear redo stack
    history.push(MockCommand(2, target_list))
    assert not history.can_redo()
    assert target_list == [2]
