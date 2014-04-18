from Tkinter import *
import sys
import gc

class FixedMenu(Menu):
    # A fix for the .delete() method in Menu.
    # To delete commands defined in the menu items deleted.
    # Also changed the comment: INDEX2 is actually INCLUDED.
    def delete(self, index1, index2=None):
        """Delete menu items between INDEX1 and INDEX2 (included)."""
	print self._tclCommands
	if index2 is None:
	    index2 = index1
	# First find out what entries have defined commands.
	cmds = []
	for i in range(self.index(index1), self.index(index2)+1):
	    c = str(self.entrycget(i, 'command'))
	    if c in self._tclCommands:
		# I don't want to delete the command already, since it
		# seems mystical to do that while the entry is not yet deleted.
		cmds.append(c)
	# Delete the menu entries.
	self.tk.call(self._w, 'delete', index1, index2)
	# Now that the menu entries have been deleted, we can delete their commands.
	for c in cmds:
	    self.deletecommand(c)


def test1(M):
    # Test with a single command
    gc.collect()
    root = Tk()
    button = Menubutton(root, text='Window')
    menu = M(button)
    button['menu'] = menu
    def command():
	print 'command button pressed'
    rc = sys.getrefcount(command)
    menu.add_command(command=command) # or add_radiobutton etc
    idx = menu.index(END)
    menu.delete(idx)
    gc.collect()
    rc1 = sys.getrefcount(command)
    print 'leak test with class', M,
    if rc1 != rc:
	print 'failed: command is now hold by', rc1, 'references'
    else:
	print 'succeeded: command is now hold by', rc1, 'references'
    
    root.destroy()

def test2(M):
    # Test with 3 commands, especially to see that deleting a range works.

    gc.collect()
    root = Tk()
    button = Menubutton(root, text='Window')
    menu = M(button)
    button['menu'] = menu
    def command0():
	print 'command 0 button pressed'
	'deleting 0 and 1'
	menu.delete(idx0, idx1)
    def command1():
	print 'command 1 button pressed'
    def command2():
	print 'command 2 button pressed'
	print 'deleting at END'
	menu.delete(END)
	root.quit()
    rc = [sys.getrefcount(x) for x in (command0, command1, command0)]
    del x
    button.pack()
    menu.add_command(command=command0,label='press first') # or add_radiobutton etc
    idx0 = menu.index(END)
    menu.add_radiobutton(command=command1,label='command1') 
    menu.add_command(label='no Command') # to see that delete works even when no command supplied
    idx1 = menu.index(END)
    menu.add_command(command=command2,label='press last')
    idx2 = menu.index(END)
    root.mainloop()

    gc.collect()
    rc1 = [sys.getrefcount(x) for x in (command0, command1, command0)]
    del x
    print 'leak test with class', M,
    if rc1 != rc:
	print 'failed: command is now hold by', rc1, 'references, should be', rc
    else:
	print 'succeeded: command is now hold by', rc1, 'references'
    
    root.destroy()



for M in (Menu, FixedMenu,):
    test1(M)
    test2(M)
