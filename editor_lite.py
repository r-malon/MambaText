from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from json import load

def about():
	messagebox.showinfo('About', 'Text Editor v0.1\nCreated by R. Malon.')

def saveas(event=None):
	save_local = filedialog.asksaveasfilename(filetypes=filetypes)
	if save_local == '':
		return False
	with open(save_local, 'w+') as f:
		f.write(txt.get("1.0", "end"))

def open_file(event=None):
	file_name = filedialog.askopenfilename(filetypes=filetypes)
	if file_name == '':
		return False
	with open(file_name, 'rb') as f:
		opened = f.read()
	if txt.get("1.0", "end") != '\n':
		asked = messagebox.askyesno('Opening File',
		 'Do you want to replace the current text?', icon='warning')
		if asked:
			replace_text(opened)
		else:
			return False
	else:
		replace_text(opened)
		return True

def scrap_page():
	link = askstring('Scraping page', 'Enter the link you want to scrap: ')
	try:
		response = get(link)
	except (TclError, MissingSchema, InvalidSchema, ConnectionError):
		return messagebox.showinfo('Error', 'Invalid link')
	if txt.get("1.0", "end") != '\n':
		asked = messagebox.askyesno('Scraping page',
		 'Do you want to replace the current text?', icon='warning')
		if asked:
			replace_text(response.content)
		else:
			return False
	else:
		replace_text(response.content)
		return True

def maximize(event):
	root.attributes("-fullscreen", True)
	root.bind("<F11>", minimize)
def minimize(event):
	root.attributes("-fullscreen", False)
	root.bind("<F11>", maximize)

def replace_text(text):
	txt.delete("1.0", "end")
	txt.insert("end", text)

with open('settings.json', 'r') as f:
	settings = load(f)

root = Tk()
filetypes = [tuple(i) for i in settings['filetypes']]
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(settings['size'] + "+" + str(screen_width//2-360) + "+" + str(screen_height//2-240))
root.title(settings['title'])
v = StringVar()
bottom_bar = Frame(relief=SUNKEN)
menu = Menu(root)
text_info = Label(bottom_bar, textvariable=v)
txt = Text(root, background=settings['background'], foreground=settings['text_color'],
 insertbackground=settings['insert_color'], insertwidth=settings['insert_width'],
  insertofftime=200, insertontime=500)

file_menu = Menu(menu, tearoff=0)
edit_menu = Menu(menu, tearoff=0)
options_menu = Menu(menu, tearoff=0)
font_menu = Menu(menu, tearoff=0)
help_menu = Menu(menu, tearoff=0)

menu.add_cascade(label='File', menu=file_menu)
menu.add_cascade(label='Edit', menu=edit_menu)
menu.add_cascade(label='Options', menu=options_menu)
menu.add_cascade(label='Help', menu=help_menu)

file_menu.add_command(label='Open file', command=open_file)
file_menu.add_command(label='Save file', command=saveas)

edit_menu.add_command(label='Paste', command=lambda: txt.event_generate("<<Paste>>"))
edit_menu.add_command(label='Copy', command=lambda: txt.event_generate("<<Copy>>"))
edit_menu.add_command(label='Cut', command=lambda: txt.event_generate("<<Cut>>"))
edit_menu.add_command(label='Undo', command=lambda: txt.event_generate("<<Undo>>"))
edit_menu.add_command(label='Redo', command=lambda: txt.event_generate("<<Redo>>"))

options_menu.add_cascade(label='Change font')

font_menu.add_command(label='Arial', command=lambda: txt.config(font='Arial'))
font_menu.add_command(label='Times New Roman', command=lambda: txt.config(font='Times'))
font_menu.add_command(label='Courier', command=lambda: txt.config(font='Courier'))
font_menu.add_command(label='Georgia', command=lambda: txt.config(font='Georgia'))
font_menu.add_command(label='Verdana', command=lambda: txt.config(font='Verdana'))

help_menu.add_command(label='About', command=about)
help_menu.add_command(label='Quit', command=root.quit)

root.bind("<Control-s>", saveas)
root.bind("<Control-o>", open_file)
root.bind("<Key>", lambda x: v.set(f"Position: {txt.index(INSERT)}; Lines: {int(txt.index('end').split('.')[0]) - 1}; Letters: {len(txt.get('1.0', 'end')) - 1}"))
root.bind("<Button>", lambda x: v.set(f"Position: {txt.index(INSERT)}; Lines: {int(txt.index('end').split('.')[0]) - 1}; Letters: {len(txt.get('1.0', 'end')) - 1}"))
root.bind("<F11>", maximize)
root.bind("<Control-Shift-Z>", lambda x: txt.event_generate("<<Redo>>"))
root.bind("<Alt-m>", hide_menu)

if __name__ == '__main__':
	txt.pack(expand=True, fill=BOTH)
	txt.focus()
	bottom_bar.pack(fill=X)
	text_info.pack(side=LEFT)
	v.set(f"Position: {txt.index(INSERT)}; Lines: {int(txt.index('end').split('.')[0]) - 1}; Letters: {len(txt.get('1.0', 'end')) - 1}")
	root.config(menu=menu)
	root.mainloop()
