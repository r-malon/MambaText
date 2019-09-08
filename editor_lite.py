from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from tkinter.simpledialog import askstring
from requests import get
from requests.exceptions import MissingSchema, InvalidSchema
from pygame.mixer import music
from pygame.mixer import init
from json import load
from random import choice
import os

with open('settings.json', encoding='utf-8') as f:
	settings = load(f)

with open(settings['lang_file'], encoding='utf-8') as f:
	lang = load(f)

class TextBox(Text):
	def __init__(self, *args, **kwargs):
		super(TextBox, self).__init__(*args, **kwargs)
		self.current_file = ''
		self.modified = False
		self.filetypes = [tuple(i) for i in settings['filetypes']]
		self.config(font='Verdana 12 normal')
		self.stats = StringVar()
		self.stats.set(f"{lang['stats'][0]}: {self.index(INSERT)}; {lang['stats'][1]}: {int(self.index('end').split('.')[0]) - 1}; {lang['stats'][2]}: {len(self.get('1.0', 'end')) - 1}")
		self.binds()
		self.tag_configs()
		self.focus()

	def open_file(self, event=None):
		file_name = filedialog.askopenfilename(filetypes=self.filetypes)
		if not file_name:
			return "break"
		try:
			with open(file_name, encoding='utf-8') as f:
				opened = f.read()
		except UnicodeDecodeError:
			with open(file_name, 'rb') as f:
				opened = f.read()
		if self.ask_replace(opened, msg=lang['open']):
			root.title(f"{file_name} - {settings['title']}")
			self.current_file = file_name
			self.modified = False
			self.stat_updater()
		return "break"

	def saveas(self, event=None):
		save_local = filedialog.asksaveasfilename(filetypes=self.filetypes)
		if not save_local:
			return False
		with open(save_local, 'w+', encoding='utf-8') as f:
			f.write(self.get("1.0", "end").strip('\n'))
		self.current_file = save_local
		self.modified = False
		self.stat_updater()
		root.title(f"{save_local} - {settings['title']}")

	def new_text(self, text):
		self.delete("1.0", "end")
		self.insert("end", text)

	def ask_replace(self, new_str, msg=lang['ask_replace'][0]):
		if self.get("1.0", "end") != '\n':
			asked = messagebox.askyesno(msg, 
				lang['ask_replace'][1], 
				icon='warning')
			if asked:
				self.new_text(new_str)
			return asked
		else:
			self.new_text(new_str)
			return True

	def change_font(self, arg, arg_id):
		new_font = self.cget('font').split(' ')
		new_font[arg_id] = arg
		self.tag_configs()
		self.config(font=new_font)

	def scrap_page(self):
		link = askstring(lang['scrap_page'][0], lang['scrap_page'][1])
		if not link:
			return False
		self.focus()
		try:
			response = get(link)
		except (TclError, MissingSchema, InvalidSchema, ConnectionError):
			return messagebox.showinfo('Error', lang['scrap_page'][2])
		if self.ask_replace(response.content, msg=lang['scrap_page'][0]):
			root.title(f"{link} - {settings['title']}")

	def clear_highlight(self, event=None):
		for tag in self.tag_names():
			self.tag_remove(tag, '1.0', 'end')

	def stat_updater(self, event=None):
		self.stats.set(f"{lang['stats'][0]}: {self.index(INSERT)}; {lang['stats'][1]}: {int(self.index('end').split('.')[0]) - 1}; {lang['stats'][2]}: {len(self.get('1.0', 'end')) - 1}")

	def tag_configs(self):
		self.tag_configure("found", background=settings['found_color'])
		self.tag_configure("bold", font=(self.cget('font').split(' ')[0], self.cget('font').split(' ')[1], 'bold'))
		self.tag_configure("italic", font=(self.cget('font').split(' ')[0], self.cget('font').split(' ')[1], 'italic'))
		self.tag_configure("underline", font=(self.cget('font').split(' ')[0], self.cget('font').split(' ')[1], 'underline'))

	def binds(self):
		self.bind(settings["shortcuts"]["open"], self.open_file)
		self.bind(settings["shortcuts"]["saveas"], self.saveas)
		self.bind(settings["shortcuts"]["clear_highlight"], self.clear_highlight)
		self.bind(settings["shortcuts"]["redo"], lambda x: self.event_generate("<<Redo>>"))
		root.bind("<Key>", self.stat_updater)
		root.bind("<Button>", self.stat_updater)


def about():
	messagebox.showinfo(lang['about'][0], 
		'Text Editor\nCreated by R. Malon.\n\nCopyright © 2019')
	
def play_song(path):
	if not path:
		return False
	music.load(path)
	music.play()

def open_audio():
	file_name = filedialog.askopenfilename(filetypes=[("Audio files", "*.mp3 *.ogg *.wav")])
	play_song(file_name)

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

root = Tk()
root.title(lang['untitled'] + " - " + settings['title'])
root.iconbitmap(settings["icon"])
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry('+'.join([settings['size'], 
	str(screen_width//2), 
	str(screen_height//2)]))
root.minsize(width=settings['minsize'][0], height=settings['minsize'][1])
textbox = TextBox(root, 
	background=settings['background'], 
	foreground=settings['text_color'], 
	insertbackground=settings['insert_color'], 
	insertwidth=settings['insert_width'], 
	insertofftime=settings["insertofftime"], 
	insertontime=settings["insertontime"], 
	selectforeground=settings["selectforeground"], 
	selectbackground=settings["selectbackground"]
	)
bottom_bar = Frame(root)
text_stats = Label(bottom_bar, textvariable=textbox.stats)
init()

menu = Menu(root)
file_menu = Menu(menu, tearoff=0)
edit_menu = Menu(menu, tearoff=0)
options_menu = Menu(menu, tearoff=0)
font_menu = Menu(menu, tearoff=0)
font_size_menu = Menu(menu, tearoff=0)
help_menu = Menu(menu, tearoff=0)

menu.add_cascade(label=lang['menu'][0], menu=file_menu)
menu.add_cascade(label=lang['menu'][1], menu=edit_menu)
menu.add_cascade(label=lang['menu'][2], menu=options_menu)
menu.add_separator()
menu.add_cascade(label=lang['menu'][3], menu=help_menu)

file_menu.add_command(label=lang['file'][1], command=textbox.open_file)
file_menu.add_command(label=lang['file'][3], command=textbox.saveas)
file_menu.add_separator()
file_menu.add_command(label=lang['file'][5], command=root.quit)

edit_menu.add_command(label=lang['edit'][0], command=lambda: textbox.event_generate("<<Paste>>"))
edit_menu.add_command(label=lang['edit'][1], command=lambda: textbox.event_generate("<<Copy>>"))
edit_menu.add_command(label=lang['edit'][2], command=lambda: textbox.event_generate("<<Cut>>"))
edit_menu.add_command(label=lang['edit'][3], command=lambda: textbox.event_generate("<<Undo>>"))
edit_menu.add_command(label=lang['edit'][4], command=lambda: textbox.event_generate("<<Redo>>"))

options_menu.add_cascade(label=lang['options'][0], menu=font_menu)
options_menu.add_cascade(label=lang['options'][1], menu=font_size_menu)
options_menu.add_command(label=lang['options'][5], command=textbox.scrap_page)

for font_name in settings["fonts"]:
	font_menu.add_command(label=font_name, command=lambda font_name=font_name: textbox.change_font(font_name, 0))

for size in range(settings["min_font_size"], settings["max_font_size"], settings["font_size_interval"]):
	font_size_menu.add_command(label=size, command=lambda size=size: textbox.change_font(size, 1))

help_menu.add_command(label=lang['about'][0], command=about)

root.bind(settings["shortcuts"]["maximize"], maximize)
root.bind(settings["shortcuts"]["menu_hider"], hide_menu)

if __name__ == '__main__':
	textbox.pack(expand=True, fill=BOTH)
	bottom_bar.pack(fill=X)
	text_stats.pack(side=LEFT)
	root.config(menu=menu)
	root.mainloop()