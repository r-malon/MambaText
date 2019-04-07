from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from tkinter.simpledialog import askstring
#from tkinter import ttk
from json import load
from pygame.mixer import music
from pygame.mixer import init
from os import listdir

def about():
	messagebox.showinfo('About', 'Text Editor v0.1\nCreated by Jailson.')

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

def replace_text(text):
	txt.delete("1.0", "end")
	txt.insert("end", text)

def find_text(event=None):
	length = StringVar()
	to_find = askstring('Find', 'Enter what you want to find: ')
	position = txt.search(to_find, '1.0', stopindex='end', count=length)
	txt.tag_add("found", position, f"{position}+{length.get()}c")
	txt.focus()

def maximize(event):
	root.attributes("-fullscreen", True)
	root.bind("<F11>", minimize)

def minimize(event):
	root.attributes("-fullscreen", False)
	root.bind("<F11>", maximize)

'''def add_tab():
	tab = Frame(notebook)
	notebook.add(tab, text=f'hi {len(tab_list)}')
	tab_list.append(tab)
	txt = Text(tab)'''

with open('settings.json', 'r') as f:
	settings = load(f)

root = Tk()
filetypes = [("All Files", "*.*"),
	("Text Files", "*.txt"),
	("Python Scripts", "*.py"),
	("Markdown Documents", "*.md"),
	("JavaScript Files", "*.js"),
	("HTML Documents", "*.html"),
	("CSS Documents", "*.css")]
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
scroll = Scrollbar(txt, cursor='arrow')
txt.config(yscrollcommand=scroll.set)
txt.tag_configure("found", background="green")
init()

file_menu = Menu(menu, tearoff=0)
edit_menu = Menu(menu, tearoff=0)
options_menu = Menu(menu, tearoff=0)
font_menu = Menu(menu, tearoff=0)
font_size_menu = Menu(menu, tearoff=0)
help_menu = Menu(menu, tearoff=0)
music_menu = Menu(menu, tearoff=0)

menu.add_cascade(label='File', menu=file_menu)
menu.add_cascade(label='Edit', menu=edit_menu)
menu.add_cascade(label='Options', menu=options_menu)
menu.add_separator()
menu.add_cascade(label='Help', menu=help_menu)

file_menu.add_command(label='New file')#, command=add_tab)
file_menu.add_command(label='Open file', command=open_file)
file_menu.add_command(label='Save file', command=saveas)

edit_menu.add_command(label='Paste', command=lambda: txt.event_generate("<<Paste>>"))
edit_menu.add_command(label='Copy', command=lambda: txt.event_generate("<<Copy>>"))
edit_menu.add_command(label='Cut', command=lambda: txt.event_generate("<<Cut>>"))
edit_menu.add_command(label='Undo', command=lambda: txt.event_generate("<<Undo>>"))
edit_menu.add_command(label='Redo', command=lambda: txt.event_generate("<<Redo>>"))
edit_menu.add_command(label='Find', command=find_text)

options_menu.add_cascade(label='Change font', menu=font_menu)
options_menu.add_cascade(label='Change font size', menu=font_size_menu)
options_menu.add_cascade(label='Pick a song', menu=music_menu)

font_menu.add_command(label='Arial', command=lambda: txt.config(font='Arial'))
font_menu.add_command(label='Times New Roman', command=lambda: txt.config(font='Times'))
font_menu.add_command(label='Courier', command=lambda: txt.config(font='Courier'))
font_menu.add_command(label='Georgia', command=lambda: txt.config(font='Georgia'))
font_menu.add_command(label='Verdana', command=lambda: txt.config(font='Verdana'))
font_menu.add_command(label='Comic Sans', command=lambda: txt.config(font=('Comic Sans MS', 10, 'bold')))
font_menu.add_command(label='Trebuchet', command=lambda: txt.config(font=('Trebuchet MS', 10)))

font_size_menu.add_command(label='8')
font_size_menu.add_command(label='10')
font_size_menu.add_command(label='12')
font_size_menu.add_command(label='14')
font_size_menu.add_command(label='18')
font_size_menu.add_command(label='20')
font_size_menu.add_command(label='22')
font_size_menu.add_command(label='24')

#music_menu.add_command(label='Lazy Day Blues', command=lambda: music.play(settings['music'][0]))
for sound in listdir('sound'):
	music.load('sound/' + sound)
	music_menu.add_command(label=sound, command=music.play)
music_menu.add_command(label='Pause', command=music.pause)
music_menu.add_command(label='Unpause', command=music.unpause)

help_menu.add_command(label='About', command=about)
help_menu.add_command(label='Quit', command=root.quit)

root.bind("<Control-s>", saveas)
root.bind("<Control-o>", open_file)
root.bind("<Control-f>", find_text)
root.bind("<Key>", lambda x: v.set(f"Position: {txt.index(INSERT)}; Lines: {int(txt.index('end').split('.')[0]) - 1}; Letters: {len(txt.get('1.0', 'end')) - 1}"))
root.bind("<Button>", lambda x: v.set(f"Position: {txt.index(INSERT)}; Lines: {int(txt.index('end').split('.')[0]) - 1}; Letters: {len(txt.get('1.0', 'end')) - 1}"))
root.bind("<F11>", maximize)
root.bind("<Control-Shift-Z>", lambda x: txt.event_generate("<<Redo>>"))

if __name__ == '__main__':
	scroll.pack(side=RIGHT, fill=Y)
	txt.pack(expand=True, fill=BOTH)
	txt.focus()
	bottom_bar.pack(fill=X)
	text_info.pack(side=LEFT)
	v.set(f"Position: {txt.index(INSERT)}; Lines: {int(txt.index('end').split('.')[0]) - 1}; Letters: {len(txt.get('1.0', 'end')) - 1}")
	root.config(menu=menu)
	root.mainloop()