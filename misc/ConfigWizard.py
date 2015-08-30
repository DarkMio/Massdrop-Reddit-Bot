# coding=utf-8
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Combobox
from configparser import ConfigParser, NoOptionError


"""This ConfigWizard is for editing and creating bot configs quickly. It looks ugly and it could certainly written
   way, way better, but accept it as what it is. A little ugly piece of code generating a nice little UI."""


class ConfigSelector(Frame):
    parent = None
    frame_box = None
    frame_output = None
    frame_action = None
    text = None
    sections = None
    listbox_configs = None
    label_text = None
    button_edit = None
    button_new = None
    config_parser = None

    def __init__(self, parent, config_path):
        Frame.__init__(self, parent, background="white")
        self.parent = parent
        self.config_parser = cp = ConfigParser()
        cp.read(config_path)
        self.sections = cp.sections()
        self.config_path = config_path
        self.init_ui('Config Editor', self.sections)

    def button_action_click(self):
        list_select = self.listbox_configs.curselection()
        item_select = list_select[0]
        name_select = self.listbox_configs.get(item_select)

        def window_destroy():
            window.destroy()
            parent.deiconify()
        parent = self.parent
        parent.iconify()

        window = Toplevel(self)
        new_dialog = ConfigDialog(window, self.config_parser, edit=True, section=name_select)
        window.bind('<Destroy>', lambda x: root.deiconify)
        window.protocol("WM_DELETE_WINDOW", window_destroy)

    def new_dialog(self):
        def window_destroy():
            window.destroy()
            parent.deiconify()
            populate_list(self.config_parser.sections())

        populate_list = self.populate_list
        parent = self.parent
        parent.iconify()

        window = Toplevel(self)
        new_dialog = ConfigDialog(window, self.config_parser)
        window.bind('<Destroy>', lambda x: root.deiconify)
        window.protocol("WM_DELETE_WINDOW", window_destroy)

    def init_ui(self, title, sections):
        parent = self.parent
        parent.title(title)

        self.frame_box = Frame(master=parent, bg='#FFCFC9')
        self.frame_box.place(x=5, y=5, width=290, height=420)

        self.frame_output = Frame(master=parent, bg='#D5E88F')
        self.frame_output.place(x=5, y=430, width=290, height=30)

        self.frame_action = Frame(master=parent, bg='#FBD975')
        self.frame_action.place(x=5, y=465, width=290, height=30)

        self.text = StringVar()

        self.listbox_configs = Listbox(master=self.frame_box, selectmode='browse', relief=FLAT)
        self.populate_list(sections)
        self.listbox_configs.place(x=5, y=5, width=280, height=410)
        self.listbox_configs.bind('<FocusIn>', self.add_list(self.config_parser.sections()[-1]))
        self.listbox_configs.bind('<FocusOut>', self.add_list(self.config_parser.sections()[-1]))

        self.label_text = Label(master=self.frame_output, bg='white')
        self.label_text.place(x=5, y=5, width=280, height=20)

        self.button_edit = Button(master=self.frame_action, text='edit', command=self.button_action_click, relief=FLAT)
        self.button_edit.place(x=5, y=5, width=100, height=20)

        self.button_new = Button(master=self.frame_action, text='new', command=self.new_dialog, relief=FLAT)
        self.button_new.place(x=290 - 100 - 5, y=5, width=100, height=20)

    def populate_list(self, sections):
        self.listbox_configs.delete(0, 'end')
        for section in sections:
            self.listbox_configs.insert('end', section)

    def add_list(self, section):
        self.config_parser.read(self.config_path)
        if section not in self.listbox_configs.get(0, 'end'):
            self.listbox_configs.insert('end', section)


class ConfigDialog(Frame):
    parent = None
    config_parser = None
    section = None
    frame_config = None
    frame_output = None
    frame_action = None
    section_field = None
    var_description = None
    is_logged_in_frame = None
    is_logged_in_var = None
    username_field = None
    oauth_field = None
    button_save = None
    edit = None

    def __init__(self, parent, config_parser, edit=False, section=None):
        Frame.__init__(self, parent, background="white")
        self.parent = parent
        self.config_parser = config_parser
        self.section = section
        self.edit = edit
        if edit:
            self.is_logged_in = config_parser.getboolean(section, 'is_logged_in')
            pass

        self.init_ui('Config Creator', self.section)

    def get(self, name):
        try:
            return self.config_parser.get(self.section, name)
        except NoOptionError:
            return ''

    def init_ui(self, title, section):
        select_section = lambda x, y: x if not self.section else y
        select = lambda x, y: x if not self.section else self.get(y)
        select_optional = lambda x, y: x if not self.get(y) else self.get(y)
        parent = self.parent
        parent.title(title)
        if not section:
            section = ''
        self.frame_config = Frame(master=parent, bg='#FFCFC9')
        self.frame_config.grid(row=0, padx=5, pady=5, ipady=2.5, rowspan=5)

        self.frame_output = Frame(master=parent, bg='#D5E88F')
        self.frame_output.grid(row=6, padx=5, pady=5)

        self.frame_action = Canvas(master=parent, bg='#FBD975', height=20, width=20)
        self.frame_action.grid(row=7)

        self.section_field = self.build_entry_field(select_section('Bot Section Name', self.section),
                                                    self.frame_config, 0, 0, 5)
        self.var_description = self.build_entry_field(select('Bot Description', 'description'),
                                                      self.frame_config, 1, 0)

        self.username_field = self.build_entry_field(select_optional('Username', 'username'),
                                                     self.frame_config, 4, 0)
        self.oauth_field = self.build_entry_field(select_optional('OAuth Filename', 'oauth_file'),
                                                  self.frame_config, 5, 0)

        self.is_logged_in_frame, self.is_logged_in_var = self.build_combobox_with_label(
            self.build_tuple_order(), self.frame_config, 3, 1, [self.username_field, self.oauth_field])

        self.button_save = Button(master=self.frame_action, text='save', command=self.save_action_click,
                                  relief=FLAT, bg='white', height=1)
        self.button_save.pack(expand=YES, fill=BOTH)

    def build_tuple_order(self):
        if self.edit and self.config_parser.get(self.section, 'is_logged_in') == 'True':
            return 'True', 'False'
        return 'False', 'True'

    @staticmethod
    def build_entry_field(text, master, row, col, pady=2.5):
        ef = Entry(master=master, relief=FLAT)
        ef.insert('end', text)
        ef.grid(row=row, column=col, pady=pady, columnspan=2, padx=5, sticky=W+E)
        ef.bind('<Enter>', lambda e: ef.delete(0, END) if ef.get() == text else None)
        ef.bind('<Leave>', lambda e: ef.insert('end', text) if ef.get() == '' and not ef.focus_get() == ef else None)
        ef.bind('<FocusOut>', lambda e: ef.insert('end', text) if ef.get() == '' else None)
        return ef

    @staticmethod
    def build_combobox_with_label(values, master, row, col, toggle_background_elements):
        def toggle_display():
            for element in toggle_background_elements:
                if var.get() == 'True':
                    element.configure(state='normal')
                elif var.get() == 'False':
                    element.configure(state='disabled')

        frame = Frame(master=master, bg='#FFCFC9')
        frame.grid(row=row, column=col, padx=5)
        label = Label(master=frame, text='Is logged in: ', justify=LEFT)
        label.config(justify='right', bg='white')
        label.grid(row=0, column=0, pady=2.5)
        var = StringVar(master=frame, value=values[0])
        cb = Combobox(master=frame, textvariable=var)
        cb['values'] = values
        cb.grid(row=0, column=1)
        cb.bind('<<ComboboxSelected>>', lambda x: (var.set(cb.get()), toggle_display()))
        if var.get() == 'False':
            for element in toggle_background_elements:
                element.configure(state='disabled')
        return frame, var

    def save_action_click(self):
        if self.save_check_if_complete():
            yesno = messagebox.askyesno('Save', 'Is your input correct?')
            if yesno:
                section = self.section_field.get()
                if section not in self.config_parser.sections():
                    self.config_parser.add_section(section)
                logged_in = self.is_logged_in_var.get()
                self.config_parser.set(section, 'description', self.var_description.get())
                self.config_parser.set(section, 'is_logged_in', logged_in)
                if logged_in == 'True':
                    self.config_parser.set(section, 'username', self.username_field.get())
                    self.config_parser.set(section, 'oauth_file', self.username_field.get())
                self.config_parser.write(open('../config/bot_config.ini', 'w'))
                self.parent.destroy()

    def save_check_if_complete(self):
        section, description, is_logged_in = (self.section_field.get(), self.var_description.get(),
                                              self.is_logged_in_var.get())
        if section == 'Bot Section Name' or description == 'Bot Description':
            if is_logged_in == 'True':
                username, oauth_file = self.username_field.get(), self.oauth_field.get()
                if not username == 'Username' or not oauth_file == 'OAuth Filename':
                    return True
            messagebox.showerror(message="Your config entries seem not to be complete.", title='Fields incomplete')
            return False
        return True


def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.destroy()

if __name__ == '__main__':
    root = Tk()
    root.geometry('300x500')
    root.resizable(width=FALSE, height=FALSE)
    app = ConfigSelector(root, '../config/bot_config.ini')
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
else:
    raise ImportError('This file is supposed to be run by itself, rather than imported.')
