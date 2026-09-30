from typing import Callable,List,Optional
class EditCommand:
 def __init__(self,name):self.name=name
 def execute(self):raise NotImplementedError
 def undo(self):raise NotImplementedError
 def redo(self):self.execute()
class CallableCommand(EditCommand):
 def __init__(self,name,do:Callable,undo:Callable):super().__init__(name);self._do=do;self._undo=undo
 def execute(self):self._do()
 def undo(self):self._undo()
class ImageAdjustmentCommand(CallableCommand): pass
class UndoRedoManager:
 def __init__(self,max_history=50):self.max_history=max_history;self.history:List[EditCommand]=[];self.current_index=-1
 def execute_command(self,c):
  if self.current_index<len(self.history)-1:self.history=self.history[:self.current_index+1]
  c.execute();self.history.append(c);self.current_index+=1
  if len(self.history)>self.max_history:self.history.pop(0);self.current_index-=1
 def undo(self):
  if self.current_index<0:return False
  self.history[self.current_index].undo();self.current_index-=1;return True
 def redo(self):
  if self.current_index>=len(self.history)-1:return False
  self.current_index+=1;self.history[self.current_index].redo();return True
 def can_undo(self):return self.current_index>=0
 def can_redo(self):return self.current_index<len(self.history)-1
 def get_undo_name(self):return self.history[self.current_index].name if self.can_undo() else None
 def get_redo_name(self):return self.history[self.current_index+1].name if self.can_redo() else None
 def clear(self):self.history.clear();self.current_index=-1
 def get_history_size(self):return len(self.history)
