"""
Undo/Redo System - Non-destructive editing with history management

Provides:
- Command pattern for reversible operations
- Memory-efficient history storage
- Undo/Redo functionality
"""

from typing import Callable, List, Any, Optional
import numpy as np


class EditCommand:
    """
    Base class for reversible edit commands.
    
    Each command knows how to:
    - Execute (apply change)
    - Undo (revert change)
    - Redo (reapply change)
    """
    
    def __init__(self, name: str):
        """
        Initialize command.
        
        Args:
            name: Human-readable command name
        """
        self.name = name
    
    def execute(self) -> None:
        """Execute the command"""
        raise NotImplementedError
    
    def undo(self) -> None:
        """Undo the command"""
        raise NotImplementedError
    
    def redo(self) -> None:
        """Redo the command"""
        raise NotImplementedError


class ImageAdjustmentCommand(EditCommand):
    """
    Command for image adjustments (exposure, contrast, etc).
    
    Stores:
    - Previous image state
    - Adjustment parameters
    - New image state
    """
    
    def __init__(
        self,
        name: str,
        image_data,
        previous_image: np.ndarray,
        new_image: np.ndarray,
        adjustment_params: dict
    ):
        """
        Initialize adjustment command.
        
        Args:
            name: Command name
            image_data: Reference to ImageData object
            previous_image: Image state before adjustment
            new_image: Image state after adjustment
            adjustment_params: Parameters of the adjustment
        """
        super().__init__(name)
        self.image_data = image_data
        self.previous_image = previous_image.copy()
        self.new_image = new_image.copy()
        self.adjustment_params = adjustment_params.copy()
    
    def execute(self) -> None:
        """Apply the adjustment"""
        self.image_data.update_working_image(self.new_image)
        for key, value in self.adjustment_params.items():
            self.image_data.set_adjustment(key, value)
    
    def undo(self) -> None:
        """Revert the adjustment"""
        self.image_data.update_working_image(self.previous_image)
    
    def redo(self) -> None:
        """Reapply the adjustment"""
        self.execute()


class UndoRedoManager:
    """
    Manages undo/redo history for non-destructive editing.
    
    Features:
    - Command history
    - Undo/Redo navigation
    - History clearing
    - Limited history size (memory management)
    """
    
    def __init__(self, max_history: int = 50):
        """
        Initialize manager.
        
        Args:
            max_history: Maximum history entries to keep
        """
        self.max_history = max_history
        self.history: List[EditCommand] = []
        self.current_index = -1
    
    def execute_command(self, command: EditCommand) -> None:
        """
        Execute a command and add to history.
        
        Args:
            command: Command to execute
        """
        # Remove any redo history when new command is executed
        if self.current_index < len(self.history) - 1:
            self.history = self.history[:self.current_index + 1]
        
        # Execute the command
        command.execute()
        
        # Add to history
        self.history.append(command)
        self.current_index += 1
        
        # Limit history size
        if len(self.history) > self.max_history:
            self.history.pop(0)
            self.current_index -= 1
    
    def undo(self) -> bool:
        """
        Undo the last command.
        
        Returns:
            bool: True if undo was successful
        """
        if self.current_index >= 0:
            self.history[self.current_index].undo()
            self.current_index -= 1
            return True
        return False
    
    def redo(self) -> bool:
        """
        Redo the last undone command.
        
        Returns:
            bool: True if redo was successful
        """
        if self.current_index < len(self.history) - 1:
            self.current_index += 1
            self.history[self.current_index].redo()
            return True
        return False
    
    def can_undo(self) -> bool:
        """Check if undo is available"""
        return self.current_index >= 0
    
    def can_redo(self) -> bool:
        """Check if redo is available"""
        return self.current_index < len(self.history) - 1
    
    def get_undo_name(self) -> Optional[str]:
        """Get the name of the command that would be undone"""
        if self.can_undo():
            return self.history[self.current_index].name
        return None
    
    def get_redo_name(self) -> Optional[str]:
        """Get the name of the command that would be redone"""
        if self.can_redo():
            return self.history[self.current_index + 1].name
        return None
    
    def clear(self) -> None:
        """Clear all history"""
        self.history.clear()
        self.current_index = -1
    
    def get_history_size(self) -> int:
        """Get number of commands in history"""
        return len(self.history)
