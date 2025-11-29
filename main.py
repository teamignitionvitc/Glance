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
# File:        main.py
# Author:      Shawn Liju Thomas
# Created On:  16-09-2025
#
# @brief       Entry point for the Glance Telemetry Dashboard application.
# @details     Initializes the QApplication, sets up the main window, and starts the event loop.
####################################################################################################
# HISTORY:
#
#       +----- (NEW | MODify | ADD | DELete)
#       |
# No#   |       when       who                  what
# ######+*********+**********+********************+**************************************************
# 000  NEW      16-09-2025  Shawn Liju Thomas    Initial creation
####################################################################################################

####################################################################################################
# Imports

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from app.ui.main_window import MainWindow

####################################################################################################

if __name__ == "__main__":
    """
    @brief Main entry point of the application.
    @details Sets up the Qt application, loads the icon, creates the main window, and executes the event loop.
    """
    # Fix for PyInstaller/Py2App to find resources
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    icon_path = os.path.join(base_path, "docs", "public", "Glance_nobg_jl.ico")

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(icon_path))
    
    window = MainWindow()
    window.setWindowIcon(QIcon(icon_path))
    window.show()
    
    sys.exit(app.exec())