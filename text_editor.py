from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from tkinter.simpledialog import askstring
#from tkinter import ttk
from requests import get
from requests.exceptions import MissingSchema
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

def scrap_page():
	link = askstring('Scraping page', 'Enter the link you want to scrap: ')
	try:
		response = get(link)
	except (TclError, MissingSchema):
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

def replace_text(text):
	txt.delete("1.0", "end")
	txt.insert("end", text)

def find_text(event=None):
	to_find = askstring('Find', 'Enter what you want to find: ')
	search_start = '1.0'
	matches = 0
	while True:
		try:
			length = StringVar()
			position = txt.search(to_find, search_start, stopindex='end', count=length)
			txt.tag_add("found", position, f"{position}+{length.get()}c")
			search_start = f"{position}+{length.get()}c"
			matches += 1
		except TclError:
			messagebox.showinfo('Find', f'{to_find} had {matches} matches')
			break
	txt.focus()

def play_song(path):
	music.load(path)
	music.play()

def maximize(event):
	root.attributes("-fullscreen", True)
	root.bind("<F11>", minimize)

def minimize(event):
	root.attributes("-fullscreen", False)
	root.bind("<F11>", maximize)

def show_menu(event):
	root.config(menu=menu)
	root.bind("<Alt-m>", hide_menu)

def hide_menu(event):
	root.config(menu='')
	root.bind("<Alt-m>", show_menu)

font = current_font, current_font_size, current_style = 'Courier', 10, 'normal'

def font_config(font=current_font, size=current_font_size, style=current_style):
	txt.config(font=(font, size, style))
	current_font, current_font_size, current_style = font, size, style

'''def add_tab():
	tab = Frame(notebook)
	notebook.add(tab, text=f'hi {len(tab_list)}')
	tab_list.append(tab)
	txt = Text(tab)'''

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
#font = current_font, current_font_size, current_style = 'Courier', 10, 'normal'
txt = Text(root, background=settings['background'], foreground=settings['text_color'],
 insertbackground=settings['insert_color'], insertwidth=settings['insert_width'],
  insertofftime=200, insertontime=500, font=font)
txt.tag_configure("found", background=settings['found_color'])
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
options_menu.add_cascade(label='Scrap a webpage', command=scrap_page)

font_menu.add_command(label='Arial', command=lambda: txt.config(font='Arial'))
font_menu.add_command(label='Times New Roman', command=lambda: txt.config(font='Times'))
font_menu.add_command(label='Courier', command=lambda: txt.config(font='Courier'))
font_menu.add_command(label='Georgia', command=lambda: txt.config(font='Georgia'))
font_menu.add_command(label='Verdana', command=lambda: txt.config(font='Verdana'))
font_menu.add_command(label='Comic Sans', command=lambda: txt.config(font=('Comic Sans MS', 10, 'bold')))
font_menu.add_command(label='Trebuchet', command=lambda: txt.config(font=('Trebuchet MS', 10)))

for i in range(8, 26, 2):
	font_size_menu.add_command(label=str(i), command=lambda: font_config(size=i))

for song in listdir('sound'):
	music_menu.add_command(label=song, command=lambda: play_song(f'sound/{song}'))
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
root.bind("<Alt-m>", hide_menu)

if __name__ == '__main__':
	txt.pack(expand=True, fill=BOTH)
	txt.focus()
	bottom_bar.pack(fill=X)
	text_info.pack(side=LEFT)
	v.set(f"Position: {txt.index(INSERT)}; Lines: {int(txt.index('end').split('.')[0]) - 1}; Letters: {len(txt.get('1.0', 'end')) - 1}")
	root.config(menu=menu)
	print(txt.cget('font'))
	root.mainloop()