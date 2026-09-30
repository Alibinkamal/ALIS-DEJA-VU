"""
Tests for Undo/Redo system
"""

import unittest
import numpy as np
from app.core.image import ImageData
from app.core.undo_redo import UndoRedoManager, ImageAdjustmentCommand


class TestUndoRedo(unittest.TestCase):
    """Test undo/redo functionality"""
    
    def setUp(self):
        """Setup test data"""
        self.manager = UndoRedoManager(max_history=10)
        
        # Create a dummy image data object
        self.image_data = type('ImageData', (), {
            'update_working_image': lambda self, data: None,
            'set_adjustment': lambda self, name, value: None
        })()
    
    def test_empty_history(self):
        """Test empty history state"""
        self.assertFalse(self.manager.can_undo())
        self.assertFalse(self.manager.can_redo())
        self.assertEqual(self.manager.get_history_size(), 0)
    
    def test_single_command(self):
        """Test single command"""
        previous = np.zeros((10, 10, 3))
        new = np.ones((10, 10, 3))
        
        command = ImageAdjustmentCommand(
            "Test",
            self.image_data,
            previous,
            new,
            {"test": 1.0}
        )
        
        self.manager.execute_command(command)
        
        self.assertEqual(self.manager.get_history_size(), 1)
        self.assertTrue(self.manager.can_undo())
        self.assertFalse(self.manager.can_redo())
    
    def test_undo(self):
        """Test undo operation"""
        previous = np.zeros((10, 10, 3))
        new = np.ones((10, 10, 3))
        
        command = ImageAdjustmentCommand(
            "Test",
            self.image_data,
            previous,
            new,
            {"test": 1.0}
        )
        
        self.manager.execute_command(command)
        self.assertTrue(self.manager.undo())
        
        self.assertTrue(self.manager.can_redo())
        self.assertFalse(self.manager.can_undo())
    
    def test_undo_redo(self):
        """Test undo then redo"""
        previous = np.zeros((10, 10, 3))
        new = np.ones((10, 10, 3))
        
        command = ImageAdjustmentCommand(
            "Test",
            self.image_data,
            previous,
            new,
            {"test": 1.0}
        )
        
        self.manager.execute_command(command)
        self.manager.undo()
        self.manager.redo()
        
        self.assertTrue(self.manager.can_undo())
        self.assertFalse(self.manager.can_redo())
    
    def test_history_limit(self):
        """Test history size limit"""
        manager = UndoRedoManager(max_history=3)
        
        previous = np.zeros((10, 10, 3))
        new = np.ones((10, 10, 3))
        
        # Add 5 commands (should only keep 3)
        for i in range(5):
            command = ImageAdjustmentCommand(
                f"Command{i}",
                self.image_data,
                previous,
                new,
                {"test": float(i)}
            )
            manager.execute_command(command)
        
        # History size should be limited
        self.assertEqual(manager.get_history_size(), 3)


if __name__ == '__main__':
    unittest.main()
