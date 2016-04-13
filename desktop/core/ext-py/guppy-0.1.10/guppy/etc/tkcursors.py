#._cv_part guppy.etc.tkcursors

# A Tk window that shows what cursor shapes are available.
# Moving the mouse over the cursor name shows the cursor in that shape.

from Tkinter import *

def tkcursors(master=None):
    if master is None:
	root = Tk()
    else:
	root = master
    for i, cursor in enumerate((
	'X_cursor',
	'arrow',
	'based_arrow_down',
	'based_arrow_up',
	'boat',
	'bogosity',
	'bottom_left_corner',
	'bottom_right_corner',
	'bottom_side',
	'bottom_tee',
	'box_spiral',
	'center_ptr',
	'circle',
	'clock',
	'coffee_mug',
	'cross',
	'cross_reverse',
	'crosshair',
	'diamond_cross',
	'dot',
	'dotbox',
	'double_arrow',
	'draft_large',
	'draft_small',
	'draped_box',
	'exchange',
	'fleur',

	'gobbler',
	'gumby',
	'hand1',
	'hand2',
	'heart',
	'icon',
	'iron_cross',
	'left_ptr',
	'left_side',
	'left_tee',
	'leftbutton',
	'll_angle',
	'lr_angle',
	'man',
	'middlebutton',
	'mouse',
	'pencil',
	'pirate',
	'plus',
	'question_arrow',
	'right_ptr',
	'right_side',
	'right_tee',
	'rightbutton',
	'rtl_logo',
	'sailboat',
	'sb_down_arrow',

	'sb_h_double_arrow',
	'sb_left_arrow',
	'sb_right_arrow',
	'sb_up_arrow',
	'sb_v_double_arrow',
	'shuttle',
	'sizing',
	'spider',
	'spraycan',
	'star',
	'target',
	'tcross',
	'top_left_arrow',
	'top_left_corner',
	'top_right_corner',
	'top_side',
	'top_tee',
	'trek',
	'ul_angle',
	'umbrella',
	'ur_angle',
	'watch',
	'xterm'


	)):

	w = Label(root, text=cursor,cursor=cursor,
		  width=20,anchor=W,relief=SUNKEN)
	col, row = divmod(i, 27)
	w.grid(row=row, column=col)
    if master is None:
	root.mainloop()

if __name__ == '__main__':
    tkcursors()

