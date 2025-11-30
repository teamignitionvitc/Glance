"""
Color picker button widget for selecting colors in dialogs.
"""

from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import QColor
from PySide6.QtCore import Signal


class ColorPickerButton(QPushButton):
    """
    @brief Button that opens a color picker dialog and displays the selected color.
    @details Emits colorChanged signal when color is selected.
    """
    colorChanged = Signal(str)  # Emits hex color string
    
    def __init__(self, initial_color='#00ff00', parent=None):
        super().__init__(parent)
        self.color = initial_color
        self.setMinimumWidth(80)
        self.setMinimumHeight(30)
        self.update_button_style()
        self.clicked.connect(self.pick_color)
    
    def pick_color(self):
        """Open color picker dialog"""
        from PySide6.QtWidgets import QColorDialog
        
        current_color = QColor(self.color)
        color = QColorDialog.getColor(current_color, self, "Select Color")
        
        if color.isValid():
            self.set_color(color.name())
    
    def set_color(self, color_hex):
        """Set the button color programmatically"""
        self.color = color_hex
        self.update_button_style()
        self.colorChanged.emit(self.color)
    
    def get_color(self):
        """Get the current color as hex string"""
        return self.color
    
    def update_button_style(self):
        """Update button appearance to show current color"""
        # Calculate luminance to determine text color
        color = QColor(self.color)
        luminance = (0.299 * color.red() + 0.587 * color.green() + 0.114 * color.blue()) / 255
        text_color = '#000000' if luminance > 0.5 else '#ffffff'
        
        self.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.color}, stop:1 {self._adjust_brightness(self.color, 0.8)});
                color: {text_color};
                border: 2px solid #555;
                border-radius: 6px;
                font-weight: bold;
                padding: 6px 12px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                border: 2px solid #888;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self._adjust_brightness(self.color, 1.1)}, 
                    stop:1 {self._adjust_brightness(self.color, 0.9)});
            }}
            QPushButton:pressed {{
                border: 2px solid #aaa;
            }}
        """)
        # Show color swatch + hex value
        self.setText(f"● {self.color.upper()}")
    
    def _adjust_brightness(self, color_hex, factor):
        """Adjust color brightness"""
        try:
            color = QColor(color_hex)
            h, s, v, a = color.getHsv()
            v = min(255, int(v * factor))
            color.setHsv(h, s, v, a)
            return color.name()
        except:
            return color_hex
