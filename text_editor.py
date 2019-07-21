from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from tkinter.font import Font
from tkinter.simpledialog import askstring
#from tkinter import ttk
from requests import get
from requests.exceptions import MissingSchema, InvalidSchema
from json import load
from pygame.mixer import music
from pygame.mixer import init
import os

class TextBox(Text):
	def __init__(self, *args, **kwargs):
		super(TextBox, self).__init__(*args, **kwargs)		
		self.current_file = ''
		self.modified = False
		self.filetypes = [tuple(i) for i in settings['filetypes']]
		self.font = Font(family='Courier', size=10, weight='normal', slant='roman') #{'name': 'Courier', 'size': 10, 'style': 'normal'}
		self.v = StringVar()
		self.v.set(f"Position: {self.index(INSERT)}; Lines: {int(self.index('end-1c').split('.')[0])}; Chars: {len(self.get('1.0', 'end')) - 1}")
		self.tag_configure("found", background=settings['found_color'])
		self.tag_configure("bold", font=(self.font.actual()["family"], self.font.actual()["size"], 'bold'))
		self.tag_configure("italic", font=(self.font.actual()["family"], self.font.actual()["size"], 'italic'))
		self.tag_configure("underline", font=(self.font.actual()["family"], self.font.actual()["size"], 'underline'))
		self.binds()
		self.focus()

	def saveas(self, event=None):
		save_local = filedialog.asksaveasfilename(filetypes=self.filetypes)
		if not save_local:
			return False
		with open(save_local, 'w+') as f:
			f.write(self.get("1.0", "end"))
		self.current_file = save_local
		root.title(f"{self.current_file} - " + settings['title'])

	def open_file(self, event=None):
		file_name = filedialog.askopenfilename(filetypes=self.filetypes)
		if not file_name:
			return "break"
		with open(file_name, 'rb') as f:
			opened = f.read()
		if self.ask_replace(opened, msg='Opening File'):
			root.title(f"{file_name} - " + settings['title'])
			self.current_file = file_name
		return "break"

	def rename(self, event=None):
		if not self.current_file:
			file_name = filedialog.askopenfilename()
			self.focus()
			if not file_name:
				return False
		else:
			file_name = self.current_file
		path = filedialog.askdirectory()
		self.focus()
		if not path:
			path = os.path.dirname(file_name)
		new_name = askstring("Renaming File", "Enter the new name: ")
		self.focus()
		if not new_name:
			return False
		os.rename(file_name, os.path.join(path + '/', new_name))
		self.current_file = path + new_name
		root.title(f"{self.current_file} - " + settings['title'])

	def new_text(self, text):
		self.delete("1.0", "end")
		self.insert("end", text)

	def clear_highlight(self, event=None):
		self.tag_remove("found", '1.0', 'end')

	def ask_replace(self, new_str, msg='Replacing'):
		if self.get("1.0", "end") != '\n':
			asked = messagebox.askyesno(msg, 
				'Do you want to replace the current text?', 
				icon='warning')
			if asked:
				self.new_text(new_str)
			return asked
		else:
			self.new_text(new_str)
			return True

	'''def font_config(self, **kwargs):
					name = kwargs.get('name')
					size = kwargs.get('size')
					#style = kwargs.get('style')
					listing = [name, size]
					new_font = ''
					for n in listing:
						if n:
							new_font += str(n) + ' '
						else:
							print(listing.index(n))
							new_font += str(self.font[listing.index(n)]) + ' '
							print(new_font)
					print(new_font)
					self.config(font=new_font)
					print(self.cget('font'))'''

	def change_size(self, new_size):
		self.font.configure(size=new_size)

	def change_font(self, new_font):
		self.font.configure(family=new_font)

	def scrap_page(self):
		link = askstring('Scraping page', 'Enter the link you want to scrap: ')
		if not link:
			return False
		self.focus()
		try:
			response = get(link)
		except (TclError, MissingSchema, InvalidSchema, ConnectionError):
			return messagebox.showinfo('Error', 'Invalid link')
		if self.ask_replace(response.content, msg='Scraping page'):
			root.title(f"{link} - " + settings['title'])

	def tagger(self, tag):
		tagged = self.tag_names("sel.first")
		if tag in tagged:
			self.tag_remove(tag, "sel.first", "sel.last")
		else:
			self.tag_add(tag, "sel.first", "sel.last")

	def find_text(self, event=None):
		to_find = askstring('Find', 'Enter what you want to find: ')
		search_start = '1.0'
		matches = 0
		self.focus()
		if not to_find:
			return False
		while True:
			try:
				length = StringVar()
				position = self.search(to_find, search_start, stopindex='end', count=length)
				self.tag_add("found", position, f"{position}+{length.get()}c")
				search_start = f"{position}+{length.get()}c"
				matches += 1
			except TclError:
				messagebox.showinfo('Find', f'{to_find} had {matches} matches')
				break

	def stat_updater(self, event=None):
		self.v.set(f"Position: {self.index(INSERT)}; Lines: {int(self.index('end-1c').split('.')[0])}; Chars: {len(self.get('1.0', 'end')) - 1}")

	def binds(self):
		self.bind(settings["shortcuts"]["save"], self.saveas)
		self.bind(settings["shortcuts"]["open"], self.open_file)
		self.bind(settings["shortcuts"]["find"], self.find_text)
		self.bind(settings["shortcuts"]["clear_highlight"], self.clear_highlight)
		self.bind(settings["shortcuts"]["redo"], lambda x: self.event_generate("<<Redo>>"))
		self.bind("<Key>", self.stat_updater)
		self.bind("<Button>", self.stat_updater)


def about():
	#messagebox.showinfo('About', 'Text Editor\nCreated by R. Malon.\n\nCopyright © 2019')
	top = Toplevel(root)
	top.title("About")
	Message(top, 
		text='Text Editor\nCreated by R. Malon.\n\nCopyright © 2019').pack()

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

'''def add_tab():
	tab = Frame(notebook)
	notebook.add(tab, text=f'hi {len(tab_list)}')
	tab_list.append(tab)
	txt = Text(tab)'''

with open('settings.json', 'r') as f:
	settings = load(f)

root = Tk()
root.title("untitled - " + settings['title'])
root.iconbitmap(settings["icon"])
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(settings['size'] + "+" + str(screen_width//2-360) + "+" + str(screen_height//2-240))
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
	#tabs=tkfont.Font(font=txt_font).measure(' ' * 4), #overcomplicate?
	)
bottom_bar = Frame(root)
text_stats = Label(bottom_bar, textvariable=textbox.v)
init()

menu = Menu(root)
file_menu = Menu(menu, tearoff=0)
edit_menu = Menu(menu, tearoff=0)
options_menu = Menu(menu, tearoff=0)
font_menu = Menu(menu, tearoff=0)
font_size_menu = Menu(menu, tearoff=0)
style_menu = Menu(menu, tearoff=0)
help_menu = Menu(menu, tearoff=0)
music_menu = Menu(menu, tearoff=0)
default_music_menu = Menu(menu, tearoff=0)

menu.add_cascade(label='File', menu=file_menu)
menu.add_cascade(label='Edit', menu=edit_menu)
menu.add_cascade(label='Options', menu=options_menu)
menu.add_separator()
menu.add_cascade(label='Help', menu=help_menu)

file_menu.add_command(label='New file')#, command=add_tab)
file_menu.add_command(label='Open file', command=textbox.open_file)
file_menu.add_command(label='Save as', command=textbox.saveas)
file_menu.add_command(label='Rename file', command=textbox.rename)
file_menu.add_separator()
file_menu.add_command(label='Exit', command=root.quit)

edit_menu.add_command(label='Paste', command=lambda: textbox.event_generate("<<Paste>>"))
edit_menu.add_command(label='Copy', command=lambda: textbox.event_generate("<<Copy>>"))
edit_menu.add_command(label='Cut', command=lambda: textbox.event_generate("<<Cut>>"))
edit_menu.add_command(label='Undo', command=lambda: textbox.event_generate("<<Undo>>"))
edit_menu.add_command(label='Redo', command=lambda: textbox.event_generate("<<Redo>>"))
edit_menu.add_command(label='Find', command=textbox.find_text)
edit_menu.add_command(label='Clear highlighting', command=textbox.clear_highlight)

options_menu.add_cascade(label='Change font', menu=font_menu)
options_menu.add_cascade(label='Change font size', menu=font_size_menu)
options_menu.add_cascade(label='Change style', menu=style_menu)
options_menu.add_cascade(label='Pick a song', menu=music_menu)
options_menu.add_command(label='Scrap a webpage', command=textbox.scrap_page)

style_menu.add_command(label='Bold', command=lambda: textbox.tagger('bold'))
style_menu.add_command(label='Italic', command=lambda: textbox.tagger('italic'))
style_menu.add_command(label='Underline', command=lambda: textbox.tagger('underline'))

for font_name in settings["fonts"]:
	font_menu.add_command(label=font_name, command=lambda font_name=font_name: textbox.change_font(font_name))

for size in range(settings["min_font_size"], settings["max_font_size"], settings["font_size_interval"]):
	font_size_menu.add_command(label=size, command=lambda size=size: textbox.change_size(size))

music_menu.add_command(label='Open audio file', command=open_audio)
music_menu.add_cascade(label='Default music', menu=default_music_menu)

for song in os.listdir('sound'):
	default_music_menu.add_command(label=song, command=lambda song=song: play_song(f'sound/{song}'))

music_menu.add_separator()
music_menu.add_command(label='Pause', command=music.pause)
music_menu.add_command(label='Unpause', command=music.unpause)

help_menu.add_command(label='About', command=about)

root.bind(settings["shortcuts"]["maximize"], maximize)
root.bind(settings["shortcuts"]["menu_hider"], hide_menu)

if __name__ == '__main__':
	textbox.pack(expand=True, fill=BOTH)
	bottom_bar.pack(fill=X)
	text_stats.pack(side=LEFT)
	root.config(menu=menu)
	root.mainloop()