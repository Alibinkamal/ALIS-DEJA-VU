import unittest
from app.core.undo_redo import UndoRedoManager,CallableCommand
class TestHistory(unittest.TestCase):
 def test_undo_redo(self):
  state=[0];m=UndoRedoManager(5)
  m.execute_command(CallableCommand("increment",lambda:state.__setitem__(0,1),lambda:state.__setitem__(0,0)))
  self.assertEqual(state[0],1);self.assertTrue(m.undo());self.assertEqual(state[0],0);self.assertTrue(m.redo());self.assertEqual(state[0],1)
if __name__=="__main__":unittest.main()
