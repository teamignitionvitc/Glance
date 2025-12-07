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
# Author:      MuhammadRamzy
# Created On:  14-09-2025
#
# @brief       Entry point for the Glance Telemetry Dashboard application.
# @details     Initializes the QApplication, sets up the main window, and starts the event loop.
####################################################################################################
# HISTORY:
#
#       +----- (NEW | MOD | ADD | DEL)
#       |
# No#   |       when       who                  what
# ######+*********+**********+********************+**************************************************
# 000  NEW      14-09-2025  NeilBaranwal9        Initial creation
# 001  MOD      20-09-2025  NeilBaranwal9        Update main.py with latest changes
# 002  MOD      25-09-2025  Shawn                Fixed issue with main.py commit and updated working
#                                                main.py
# 003  MOD      26-09-2025  MuhammadRamzy        First commit with the ui/ux and flow changes
# 004  MOD      27-09-2025  MuhammadRamzy        Stream Fix
# 005  MOD      30-09-2025  Shawn                Fixed map functionality using leaflet, removed extra
#                                                items from MapWidget, cleaned up the map view
# 006  MOD      30-09-2025  NeilBaranwal9        Add Ctrl key check to disable hover interactions on
#                                                TimeGraph
# 007  MOD      01-10-2025  MuhammadRamzy        Fixed the top bar, improved the bottom bar, License
#                                                Update, added RAW TELEMETRY PACKET VIEWER, added
#                                                refresh button and functionality for the connection
#                                                settings, added option to edit the dashboard header
#                                                and updated project saving methods, tab layout save
#                                                and load with dock arrangment saves, dummy app name
#                                                added (Glance)
# 008  MOD      02-10-2025  MuhammadRamzy        UI Fix, Bottom bar fix, Default Logging location
#                                                fix, added documentaion viewer in the help menu,
#                                                _tile_evenly_safe method fix, Added Standalone Raw
#                                                telemetry
# 009  MOD      03-10-2025  MuhammadRamzy        Updated namefields
# 010  MOD      04-10-2025  MuhammadRamzy        Updated main.py, added filters, updated the doc view
#                                                to web from local method, changed the about, added
#                                                keyboard shortcuts
# 011  MOD      06-10-2025  MuhammadRamzy        Updated main.py, welcome screen ui changes, gps
#                                                delay, added splash screen
# 012  MOD      07-10-2025  MuhammadRamzy        Pytest error fix
# 013  MOD      08-10-2025  MuhammadRamzy        Improved the manage filter option, fixed text-shadow
#                                                & box-shadow error, added fullscreen and improved
#                                                the tab views, improved about, improved dashboard
#                                                config ui/ux
# 014  MOD      09-10-2025  MuhammadRamzy        Formatting
# 015  MOD      11-10-2025  MuhammadRamzy        Added Automated summary generator from the data log
# 016  MOD      12-10-2025  oslowtech            Cleaned Up the main.py file, with Documentation
#                                                Openning on Windows
# 017  MOD      12-10-2025  NeilBaranwal9        modularized main.py into widget.py, refactor(main):
#                                                remove redundant DataSimulator import
# 018  MOD      14-10-2025  Shawn                fixed rendering of glance on main page in
#                                                executable, Fixed ignition logo rendering in about
#                                                tab
# 019  MOD      21-10-2025  NeilBaranwal9        fixed the multiple tab saving issue
# 020  MOD      23-10-2025  Shawn                Fixed resizing on project load
# 021  MOD      30-10-2025  Shawn                Fixed issue where close button hides widget instead
#                                                of actually closing it
# 022  MOD      06-11-2025  NeilBaranwal9        updated the test.py file and fixed minor bugs
# 023  MOD      09-11-2025  Shawn                Fixed taskbar icon and app window icon loading
# 024  MOD      29-11-2025  MuhammadRamzy        feat: Redesign AddWidgetDialog with side-by-side
#                                                layout and QStackedWidget
# 025  MOD      03-12-2025  NeilBaranwal9        feat: Fixed TimeGraph crash on high-frequency data
# 026  MOD      07-12-2025  NeilBaranwal9        feat: Fix unresponsive TimeGraph buttons using QGraphicsProxyWidget
# 027  MOD      07-12-2025  NeilBaranwal9        feat: Removed invisible hover-close button from TimeGraph and from CustomTitleBar in remaining widgets
# 028  MOD      07-12-2025  Shawn                fix: Windows specific icon fixes
####################################################################################################

####################################################################################################
# Imports

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from app.ui.main_window import MainWindow

####################################################################################################

if sys.platform.startswith("win"):
  import ctypes
  try:
    myappid = "Ignition.Glance" 
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
  except Exception:
    pass

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