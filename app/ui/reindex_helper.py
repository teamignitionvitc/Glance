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
# File:        reindex_helper.py
# Author:      MuhammadRamzy
# Created On:  30-11-2025
#
# @brief       Helper utilities for UI reindexing.
# @details     Provides utility functions for managing UI element indices.
####################################################################################################
# HISTORY:
#
#       +----- (NEW | MOD | ADD | DEL)
#       |
# No#   |       when       who                  what
# ######+*********+**********+********************+**************************************************
# 000  NEW      30-11-2025  MuhammadRamzy        fix: Simplify status bar and remove CI/CD workflows
####################################################################################################

####################################################################################################
# Imports

    def _reindex_tabs(self):
        """Re-sync tab_data keys with current QTabWidget indices"""
        new_tab_data = {}
        
        # Create a mapping of mainwindow -> tab_info
        # This assumes each tab has a unique mainwindow instance
        mw_to_info = {}
        for idx, info in self.tab_data.items():
            mw_to_info[info['mainwindow']] = info
            
        # Iterate through current tabs in QTabWidget
        for i in range(self.tab_widget.count()):
            # Get the widget (which is the mainwindow for that tab)
            widget = self.tab_widget.widget(i)
            
            # Find the corresponding info
            if widget in mw_to_info:
                new_tab_data[i] = mw_to_info[widget]
            else:
                # This shouldn't happen if logic is correct, but handle it
                print(f"Warning: Tab at index {i} has no data")
                
        # Also handle floating tabs - they aren't in QTabWidget but are in tab_data
        # We need to keep them. But their keys might conflict with new indices?
        # Floating tabs should probably be stored separately or with negative/special keys?
        # For now, let's keep them as is, but we need to find them.
        # Wait, if they are floating, they are NOT in QTabWidget.
        # So the loop above won't find them.
        # We need to preserve them.
        
        for idx, info in self.tab_data.items():
            if info.get('is_floating', False):
                # Keep floating tabs. 
                # Ideally we should use a stable ID instead of index for tab_data.
                # But for now, let's just make sure we don't overwrite them.
                # If a floating tab had index 0, and now we have a docked tab at index 0, collision!
                # We should probably move floating tabs to a separate dict or use a different key scheme.
                # Let's use the original index as a string or something? No, that breaks other code.
                # Let's just re-assign them to high indices? No.
                
                # CRITICAL: The current architecture using integer indices for tab_data keys is flawed 
                # when tabs can be moved/floated. 
                # However, for a quick fix, we can just ensure we don't lose them.
                # If we use `id(mainwindow)` as key, it would be stable.
                # But that requires refactoring EVERYTHING.
                
                # Let's just add them back with their current keys? 
                # But their current keys might be occupied by new docked tabs.
                # We need to find a free key.
                
                if idx not in new_tab_data:
                    new_tab_data[idx] = info
                else:
                    # Collision! Find a new free key.
                    new_key = 1000
                    while new_key in new_tab_data:
                        new_key += 1
                    new_tab_data[new_key] = info
                    
        self.tab_data = new_tab_data
