from tkinter import *
from tkinter import messagebox
from tkinter import filedialog

def about():
	messagebox.showinfo('About',
	 'Text Editor v0.1\nCreated by Jailson.')

def saveas(event):
	save_local = filedialog.asksaveasfilename()
	with open(save_local, 'w+') as f:
		f.write(txt.get("1.0", "end"))

def open_file(event):
	file = filedialog.askopenfilename()
	with open(file, 'rb') as f:
		opened = f.read()
	if txt.get("1.0", "end") != '\n':
		asked = messagebox.askyesno('Opening File',
		 'Do you want to replace the current text?', icon='warning')
		if asked:
			replace_text(opened)
		else:
			return False
	replace_text(opened)
	return True

def replace_text(text):
	txt.delete("1.0", "end")
	txt.insert("end", text)

def label_updater():
	while True:
		text_info.after(500, v.set(f"Lines: {int(txt.index('end').split('.')[0]) - 1}; Letters: {len(txt.get('1.0', 'end')) - 1}"))

root = Tk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry("720x480+" + str(screen_width//2-360) + "+" + str(screen_height//2-240))
root.title('My editor')
v = StringVar()
txt = Text(root, background='#2e2e2e', foreground='#c8c8c8', insertbackground='white', 
	insertwidth=3, insertofftime=200, insertontime=500)
bottom_bar = Frame(relief=SUNKEN)
menu = Menu(root)
text_info = Label(bottom_bar, textvariable=v)

file_menu = Menu(menu, tearoff=0)
edit_menu = Menu(menu, tearoff=0)
options_menu = Menu(menu, tearoff=0)
font_menu = Menu(edit_menu, tearoff=0)
font_size_menu = Menu(edit_menu, tearoff=0)

menu.add_cascade(label='File', menu=file_menu)
menu.add_cascade(label='Edit', menu=edit_menu)
menu.add_cascade(label='Options', menu=options_menu)
menu.add_command(label='About', command=about)
menu.add_separator()
menu.add_command(label='Quit', command=root.quit)

file_menu.add_command(label='New file')
file_menu.add_command(label='Open file')
file_menu.add_command(label='Save file')

edit_menu.add_command(label='Paste', command=lambda: root.event_generate("<<Paste>>"))
edit_menu.add_command(label='Copy', command=lambda: root.event_generate("<<Copy>>"))
edit_menu.add_command(label='Cut', command=lambda: root.event_generate("<<Cut>>"))
edit_menu.add_command(label='Undo', command=lambda: root.event_generate("<<Undo>>"))
edit_menu.add_command(label='Redo', command=lambda: root.event_generate("<<Redo>>"))
#edit_menu.add_command(label='Find', command=txt.search('1.0', 'ola', stopindex='end'))

options_menu.add_cascade(label='Change font', menu=font_menu)
options_menu.add_cascade(label='Change font size', menu=font_size_menu)

font_menu.add_command(label='Arial', command=lambda: txt.config(font='Arial'))
font_menu.add_command(label='Times New Roman', command=lambda: txt.config(font='Times'))
font_menu.add_command(label='Courier', command=lambda: txt.config(font='Courier'))

root.bind("<Control-s>", saveas)
root.bind("<Control-o>", open_file)
root.bind("<Key>", lambda x: v.set(f"Lines: {int(txt.index('end').split('.')[0]) - 1}; Letters: {len(txt.get('1.0', 'end')) - 1}"))

if __name__ == '__main__':
	txt.pack(expand=True, fill=BOTH)
	txt.focus()
	bottom_bar.pack(fill=X)
	text_info.pack(side=LEFT)
	v.set(f"Lines: {int(txt.index('end').split('.')[0]) - 1}; Letters: {len(txt.get('1.0', 'end')) - 1}")
	root.config(menu=menu)
	root.mainloop()