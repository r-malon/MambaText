from tkinter import *
from tkinter import messagebox, filedialog
from tkinter.simpledialog import askstring
from requests import get
from requests.exceptions import MissingSchema, InvalidSchema, InvalidURL
from pygame.mixer import music, init
from pygments import lex
from pygments.lexers import Python3Lexer, CppLexer, HtmlLexer, CssLexer, JavascriptLexer, JavaLexer, CSharpLexer, RustLexer, SqlLexer, MarkdownLexer
from json import load
from random import choice
import os

with open('settings.json', encoding='utf-8') as f:
	settings = load(f)

with open(settings['lang_file'], encoding='utf-8') as f:
	lang = load(f)

with open(settings['scheme'], encoding='utf-8') as f:
	scheme = load(f)

class TextBox(Text):
	def __init__(self, *args, **kwargs):
		super(TextBox, self).__init__(*args, **kwargs)
		self.current_file = ''
		self.modified = False # Not implemented, denotes that current file isn't saved
		self.current_lexer = Python3Lexer()
		self.filetypes = [tuple(i) for i in settings['filetypes']]
		self.stats = StringVar()
		self.stats.set(f"{lang['stats'][0]}: {self.index(INSERT)}; {lang['stats'][1]}: {int(self.index('end').split('.')[0]) - 1}; {lang['stats'][2]}: {len(self.get('1.0', 'end')) - 1}")
		self.config(font='Verdana 12 normal')
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

		if self.replace_current(opened, msg=lang['open']):
			root.title(f"{file_name} - {settings['title']}")
			self.current_file = file_name
			self.modified = False
			self.stat_updater()
		return "break"

	def save(self, event=None):
		if self.current_file:
			with open(self.current_file, 'w+', encoding='utf-8') as f:
				f.write(self.get("1.0", "end").strip('\n'))
			self.modified = False
		else:
			self.saveas()

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

		new_name = askstring(lang['rename'][0], lang['rename'][1])
		self.focus()

		if not new_name:
			return False

		try:
			os.rename(file_name, os.path.join(path + '/', new_name))
		except FileNotFoundError:
			messagebox.showerror("Error", lang['rename'][2])

		self.current_file = path + new_name
		self.modified = False
		root.title(f"{self.current_file} - {settings['title']}")

	def new_text(self, text):
		self.delete("1.0", "end")
		self.insert("end", text)

	def delete_all(self, event=None):
		if self.get("1.0", "end") != '\n':
			if messagebox.askyesno(
					lang['delete_all'][0], 
					lang['delete_all'][1], 
					icon='warning'):
				self.delete("1.0", "end")
				root.title(lang['untitled'] + " - " + settings['title'])

	def replace_current(self, new_str, msg=lang['replace_current'][0]):
		if self.get("1.0", "end") != '\n':
			asked = messagebox.askyesno(
				msg,
				lang['replace_current'][1],
				icon='warning'
			)
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
		except (TclError, MissingSchema, InvalidSchema, InvalidURL, ConnectionError):
			return messagebox.showinfo('Error', lang['scrap_page'][2])

		if self.replace_current(response.content, msg=lang['scrap_page'][0]):
			root.title(f"{link} - {settings['title']}")

	def tagger(self, tag_name):
		tagged = self.tag_names("sel.first")
		self.tag_configs()

		if tag_name in tagged:
			self.tag_remove(tag_name, "sel.first", "sel.last")
		else:
			self.tag_add(tag_name, "sel.first", "sel.last")

	def find_text(self, event=None):
		to_find = askstring(lang['find'][0], lang['find'][1])
		search_start, matches = '1.0', 0
		self.focus()

		if not to_find:
			return False

		while True:
			try:
				length = StringVar()
				position = self.search(
					to_find, 
					search_start, 
					stopindex='end', 
					count=length
				)
				self.tag_add("found", position, f"{position}+{length.get()}c")
				search_start = f"{position}+{length.get()}c"
				matches += 1
			except TclError:
				messagebox.showinfo(lang['find'][0], f"'{to_find}' {lang['find'][2]} {matches} {lang['find'][3]}")
				break

	def replace_text(self, to_find, to_replace):
		search_start = '1.0'

		while True:
			try:
				length = StringVar()
				position = self.search(
					to_find, 
					search_start, 
					stopindex='end', 
					count=length
				)
				self.delete(position, f"{position}+{length.get()}c")
				self.insert(position, to_replace)
				search_start = f"{position}+{length.get()}c"
			except TclError:
				break

	def replacer(self, event=None):
		to_find = askstring(lang['replace'][0], lang['replace'][1])
		to_replace = askstring(lang['replace'][0], lang['replace'][2])
		self.focus()

		if not to_find or not to_replace:
			return False

		self.replace_text(to_find, to_replace)

	def set_lexer(self, lexer, event=None):
		self.current_lexer = lexer
		self.highlight_all()

	def highlight(self, event=None):
		self.mark_set("range_start", self.index(INSERT)[0] + '.0')
		data = self.get("range_start", INSERT)

		for token, content in lex(data, self.current_lexer):
			self.mark_set("range_end", "range_start+%dc" % len(content))
			self.tag_add(str(token), "range_start", "range_end")
			self.mark_set("range_start", "range_end")

	def highlight_all(self):
		self.mark_set("range_start", "1.0")
		self.clear_highlights()
		data = self.get("range_start", self.index('range_start')[0] + '.end')

		for token, content in lex(data, self.current_lexer):
			self.mark_set("range_end", "range_start+%dc" % len(content))
			self.tag_add(str(token), "range_start", "range_end")
			self.mark_set("range_start", "range_end")

	def clear_highlights(self, event=None):
		for tag in self.tag_names():
			self.tag_remove(tag, '1.0', 'end')

	def stat_updater(self, event=None):
		self.stats.set(f"{lang['stats'][0]}: {self.index(INSERT)}; {lang['stats'][1]}: {int(self.index('end').split('.')[0]) - 1}; {lang['stats'][2]}: {len(self.get('1.0', 'end')) - 1}")

	def tab_press(self, event=None):
		self.insert(INSERT, '\t')
		self.stat_updater()
		return "break"

	def tag_configs(self):
		current_font = self.cget('font').split(' ')

		self.tag_configure("found", 
			background=scheme['found_color'])
		self.tag_configure("bold", 
			font=(current_font[0], current_font[1], 'bold'))
		self.tag_configure("italic", 
			font=(current_font[0], current_font[1], 'italic'))
		self.tag_configure("underline", 
			font=(current_font[0], current_font[1], 'underline'))

		for key in scheme["tokens"]:
			self.tag_configure(key[0], foreground=key[1])

	def binds(self):
		self.bind(settings["shortcuts"]["new_file"], self.delete_all)
		self.bind(settings["shortcuts"]["open"], self.open_file)
		self.bind(settings["shortcuts"]["save"], self.save)
		self.bind(settings["shortcuts"]["saveas"], self.saveas)
		self.bind(settings["shortcuts"]["find"], self.find_text)
		self.bind(settings["shortcuts"]["replace"], self.replacer)
		self.bind(settings["shortcuts"]["clear_highlights"], self.clear_highlights)
		self.bind(settings["shortcuts"]["redo"], lambda x: self.event_generate("<<Redo>>"))
		self.bind("<Tab>", self.tab_press)

		root.bind("<KeyRelease>", self.highlight)
		root.bind("<Key>", self.stat_updater)
		root.bind("<Button>", self.stat_updater)
		root.bind(settings["shortcuts"]["maximize"], maximize)
		root.bind(settings["shortcuts"]["menu_hider"], hide_menu)
		root.bind(settings["shortcuts"]["un_pause"], pause)


def about():
	top = Toplevel(root, padx=25, pady=25)
	top.iconbitmap(settings["icon"])
	top.grab_set()
	top.bind('<Escape>', lambda x: top.destroy())
	top.title(lang['about'][0])
	top.resizable(False, False)
	top.focus()

	Message(top, 
		text='MambaText', 
		font='{Trebuchet MS} 16 bold', 
		aspect=300).pack()
	Message(top, 
		text=f"{lang['about'][1]}\n\n    Copyright © 2020", 
		font='{Trebuchet MS} 12', 
		aspect=300).pack()

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
	root.bind(settings["shortcuts"]["maximize"], minimize)

def minimize(event):
	root.attributes("-fullscreen", False)
	root.bind(settings["shortcuts"]["maximize"], maximize)

def show_menu(event):
	bottom_bar.pack(fill=X)
	root.config(menu=menu)
	root.bind(settings["shortcuts"]["menu_hider"], hide_menu)

def hide_menu(event):
	bottom_bar.pack_forget()
	root.config(menu='')
	root.bind(settings["shortcuts"]["menu_hider"], show_menu)

def pause(event):
	music.pause()
	root.bind(settings["shortcuts"]["un_pause"], unpause)

def unpause(event):
	music.unpause()
	root.bind(settings["shortcuts"]["un_pause"], pause)

def leave(event=None):
	if messagebox.askyesno(lang['leave'], choice(lang["quit_msg"]), icon='warning'):
		root.quit()

'''def add_tab():
	tab = Frame(notebook)
	notebook.add(tab, text=f'hi {len(tab_list)}')
	tab_list.append(tab)
	txt = Text(tab)'''

root = Tk()
root.title(lang['untitled'] + " - " + settings['title'])
root.iconbitmap(settings["icon"])
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

root.geometry(
	'+'.join([settings['size'], 
	str(screen_width//2), 
	str(screen_height//2)])
)
root.minsize(
	width=settings['minsize'][0], 
	height=settings['minsize'][1]
)
root.protocol('WM_DELETE_WINDOW', leave)

textbox = TextBox(
	root, 
	background=scheme['background'], 
	foreground=scheme['text_color'], 
	insertbackground=scheme['insert_color'], 
	selectforeground=scheme["selectforeground"], 
	selectbackground=scheme["selectbackground"], 
	insertwidth=settings['insert_width'], 
	insertofftime=settings["insertofftime"], 
	insertontime=settings["insertontime"]
	#tabs=tkfont.Font(font=txt_font).measure(' ' * 4) #overcomplicate?
	)

bottom_bar = Frame(root)
text_stats = Label(bottom_bar, textvariable=textbox.stats)
init() # pygame mixer init

menu = Menu(root)
file_menu = Menu(menu, tearoff=False)
edit_menu = Menu(menu, tearoff=False)
options_menu = Menu(menu, tearoff=False)
font_menu = Menu(menu, tearoff=False)
font_size_menu = Menu(menu, tearoff=False)
style_menu = Menu(menu, tearoff=False)
syntax_menu = Menu(menu, tearoff=False)
help_menu = Menu(menu, tearoff=False)
music_menu = Menu(menu, tearoff=False)
favorites_menu = Menu(menu, tearoff=False)

menu.add_cascade(label=lang['menu'][0], menu=file_menu)
menu.add_cascade(label=lang['menu'][1], menu=edit_menu)
menu.add_cascade(label=lang['menu'][2], menu=options_menu)
menu.add_separator()
menu.add_cascade(label=lang['menu'][3], menu=help_menu)

file_menu.add_command(label=lang['file'][0], command=textbox.delete_all)
file_menu.add_command(label=lang['file'][1], command=textbox.open_file)
file_menu.add_command(label=lang['file'][2], command=textbox.save)
file_menu.add_command(label=lang['file'][3], command=textbox.saveas)
file_menu.add_command(label=lang['file'][4], command=textbox.rename)
file_menu.add_separator()
file_menu.add_command(label=lang['file'][5], command=leave)

edit_menu.add_command(label=lang['edit'][0], command=lambda: textbox.event_generate("<<Paste>>"))
edit_menu.add_command(label=lang['edit'][1], command=lambda: textbox.event_generate("<<Copy>>"))
edit_menu.add_command(label=lang['edit'][2], command=lambda: textbox.event_generate("<<Cut>>"))
edit_menu.add_command(label=lang['edit'][3], command=lambda: textbox.event_generate("<<Undo>>"))
edit_menu.add_command(label=lang['edit'][4], command=lambda: textbox.event_generate("<<Redo>>"))
edit_menu.add_separator()
edit_menu.add_command(label=lang['edit'][5], command=textbox.find_text)
edit_menu.add_command(label=lang['edit'][6], command=textbox.replacer)
edit_menu.add_command(label=lang['edit'][7], command=textbox.clear_highlights)

options_menu.add_cascade(label=lang['options'][0], menu=font_menu)
options_menu.add_cascade(label=lang['options'][1], menu=font_size_menu)
options_menu.add_cascade(label=lang['options'][2], menu=style_menu)
options_menu.add_cascade(label=lang['options'][3], menu=syntax_menu)
options_menu.add_cascade(label=lang['options'][4], menu=music_menu)
options_menu.add_separator()
options_menu.add_command(label=lang['options'][5], command=textbox.scrap_page)
options_menu.add_command(label=lang['options'][6], command=textbox.highlight_all)

style_menu.add_command(label=lang['style'][0], command=lambda: textbox.tagger('bold'))
style_menu.add_command(label=lang['style'][1], command=lambda: textbox.tagger('italic'))
style_menu.add_command(label=lang['style'][2], command=lambda: textbox.tagger('underline'))

syntax_menu.add_command(label='Python 3', command=lambda: textbox.set_lexer(Python3Lexer()))
syntax_menu.add_command(label='C/C++', command=lambda: textbox.set_lexer(CppLexer()))
syntax_menu.add_command(label='C#', command=lambda: textbox.set_lexer(CSharpLexer()))
syntax_menu.add_command(label='Java', command=lambda: textbox.set_lexer(JavaLexer()))
syntax_menu.add_command(label='Rust', command=lambda: textbox.set_lexer(RustLexer()))
syntax_menu.add_command(label='Go', command=lambda: textbox.set_lexer(GoLexer()))
syntax_menu.add_command(label='HTML', command=lambda: textbox.set_lexer(HtmlLexer()))
syntax_menu.add_command(label='CSS', command=lambda: textbox.set_lexer(CssLexer()))
syntax_menu.add_command(label='Javascript', command=lambda: textbox.set_lexer(JavascriptLexer()))
syntax_menu.add_command(label='PHP', command=lambda: textbox.set_lexer(PhpLexer()))
syntax_menu.add_command(label='SQL', command=lambda: textbox.set_lexer(SqlLexer()))
syntax_menu.add_command(label='Batch', command=lambda: textbox.set_lexer(BatchLexer()))
syntax_menu.add_command(label='Bash', command=lambda: textbox.set_lexer(BashLexer()))
syntax_menu.add_command(label='Markdown', command=lambda: textbox.set_lexer(MarkdownLexer()))

for font_name in settings["fonts"]:
	font_menu.add_command(label=font_name, command=lambda font_name=font_name: textbox.change_font(font_name, 0))

for size in range(settings["min_font_size"], 
	settings["max_font_size"] + settings["font_size_interval"], 
	settings["font_size_interval"]):
	font_size_menu.add_command(label=size, command=lambda size=size: textbox.change_font(size, 1))

for song in os.listdir('sound'):
	favorites_menu.add_command(label=song, command=lambda song=song: play_song(f'sound/{song}'))

music_menu.add_command(label=lang['music'][0], command=open_audio)
music_menu.add_cascade(label=lang['music'][1], menu=favorites_menu)
music_menu.add_separator()
music_menu.add_command(label=lang['music'][2], command=music.pause)
music_menu.add_command(label=lang['music'][3], command=music.unpause)

help_menu.add_command(label=lang['about'][0], command=about)

if __name__ == '__main__':
	textbox.pack(expand=True, fill=BOTH)
	bottom_bar.pack(fill=X)
	text_stats.pack(side=LEFT)
	root.config(menu=menu)
	root.mainloop()