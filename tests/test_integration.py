import pytest
import os
import json
import tempfile
from PySide6.QtCore import Qt
from app.ui.main_window import MainWindow

@pytest.fixture
def main_window(qtbot):
    """Fixture to create and clean up MainWindow"""
    window = MainWindow()
    qtbot.addWidget(window)
    return window

def test_app_lifecycle(main_window, qtbot):
    """Test application startup and basic initialization"""
    # Verify window title
    assert "Glance" in main_window.windowTitle()
    
    # Verify critical components are initialized
    assert main_window.simulator is not None
    assert main_window.data_logger is not None
    assert main_window.filter_manager is not None
    assert main_window.history is not None
    
    # Verify initial phase
    assert main_window.stack.count() > 0
    
    # Simulate switching to setup
    main_window.show_phase("setup")
    qtbot.wait(100)
    
    # Simulate switching to dashboard
    main_window.show_phase("dashboard")
    qtbot.wait(100)
    assert main_window.stack.currentWidget() == main_window.dashboard_page

def test_project_management(main_window, qtbot):
    """Test saving and loading projects"""
    # Create a temporary file for the project
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        project_path = tmp.name
    
    try:
        # 1. Modify state
        main_window.dashboard_title_text = "Integration Test Dashboard"
        main_window.parameters.append({
            "id": "test_param",
            "name": "Test Parameter",
            "unit": "V",
            "type": "float32"
        })
        
        # 2. Save Project
        main_window.save_project(file_path=project_path)
        assert os.path.exists(project_path)
        
        # Verify JSON content
        with open(project_path, 'r') as f:
            data = json.load(f)
            assert data['dashboard_title_text'] == "Integration Test Dashboard"
            assert any(p['id'] == 'test_param' for p in data['parameters'])
        
        # 3. Reset State (New Project)
        # We can simulate this by creating a new window or manually resetting
        # For this test, let's create a fresh window to load into
        new_window = MainWindow()
        qtbot.addWidget(new_window)
        
        # 4. Load Project
        new_window.load_project(file_path=project_path)
        
        # Verify state is restored
        assert new_window.dashboard_title_text == "Integration Test Dashboard"
        assert any(p['id'] == 'test_param' for p in new_window.parameters)
        
    finally:
        # Cleanup
        if os.path.exists(project_path):
            os.remove(project_path)

def test_undo_redo_integration(main_window, qtbot):
    """Test Undo/Redo integration in the main window"""
    initial_params_count = len(main_window.parameters)
    
    # Add a parameter via dialog logic (simulated)
    new_param = {"id": "undo_test", "name": "Undo Test", "unit": "A"}
    new_params = list(main_window.parameters)
    new_params.append(new_param)
    
    # Push command directly as we can't easily drive the modal dialog
    from app.core.commands import UpdateParametersCommand
    cmd = UpdateParametersCommand(main_window, main_window.parameters, new_params)
    main_window.history.push(cmd)
    
    assert len(main_window.parameters) == initial_params_count + 1
    assert main_window.history.can_undo()
    
    # Undo
    main_window.undo()
    assert len(main_window.parameters) == initial_params_count
    assert main_window.history.can_redo()
    
    # Redo
    main_window.redo()
    assert len(main_window.parameters) == initial_params_count + 1
