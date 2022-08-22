from tkinter import filedialog, Menu, Frame, END, scrolledtext, Toplevel, messagebox, HORIZONTAL, \
    StringVar
from tkinter.ttk import Progressbar
from customtkinter import CTkButton, CTkLabel, CTk
from os import listdir
from os.path import isfile, join
import ntpath
import time

bg_color = 'white'
import moviepy.editor as mp


class VideoToAudio:
    def __init__(self):
        # CONSTS
        self.acceptable_file_types = ["MP4", "MOV", "WMV", "AVI", "FLV", "MKV", "WEBM"]
        self.file_types = ", ".join(self.acceptable_file_types).lower()
        self.file_list = " ".join(self.acceptable_file_types).lower()
        self.mp = mp
        self.app_icon = 'icon.ico'
        self.grey = "#E5E5E5"
        self.blue = "#7F7FFF"

        # VARIABLES
        self.conversion_list = []
        self.conversion_file_text = ""
        self.file_save_directory = None

        # /********ROOT**********/
        # self.root = tkinter.Tk()
        self.root = CTk()
        self.root.title("Text to speech")
        self.root.iconbitmap(self.app_icon)
        self.root.geometry(f"{800}x{600}")
        self.root.minsize(800, 600)
        self.root.maxsize(800, 600)
        self.root.config(padx=50, pady=50)

        # MAIN MENU
        self.main_menu = Menu(self.root)
        self.root.configure(menu=self.main_menu)
        # /**********MENUS**********/
        # File menu
        self.file_menu = Menu(self.main_menu)
        self.main_menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="New")
        self.file_menu.add_command(label="Exit", command=self.root.quit)

        self.options_menu = Menu(self.main_menu)
        self.main_menu.add_cascade(label="Options", menu=self.file_menu)
        self.options_menu.add_command(label="New", command=None)

        # Home frame
        self.home_frame = Frame(self.root, bg=self.blue)
        self.home_frame.pack(fill="both")

        self.main_label = CTkLabel(self.home_frame, text="Audiofyyy!", text_font=("Montserrat", 30, "bold"))
        self.main_label.grid(row=0, column=0, columnspan=2)
        self.description_label = CTkLabel(self.home_frame, text=f"Convert your {self.file_types} files to audio (.mp3) files",
                                          text_font=("Montserrat", 15, "italic"))
        self.description_label.grid(row=1, column=0, columnspan=2)

        self.select_files_btn = CTkButton(self.home_frame, text="Select Files(s)", fg_color=self.grey,
                                          command=self._upload_files)
        self.select_files_btn.grid(row=2, column=0, pady=10)

        self.select_files_btn = CTkButton(self.home_frame, text="Select Folder", fg_color=self.grey,
                                          command=self._upload_folder)
        self.select_files_btn.grid(row=2, column=1)

        self.clear_btn = CTkButton(self.home_frame, text="Clear Selection", command=self._clear_file_selection,
                                   fg_color=self.grey)
        self.clear_btn.grid(row=3, column=0, columnspan=2)

        self.convert_btn = CTkButton(self.home_frame, text="Convert selected files", fg_color="orange3",
                                     command=self._directory_popup)
        self.convert_btn.grid(row=4, column=0, columnspan=2, pady=10)

        self.files_textbox = scrolledtext.ScrolledText(self.home_frame, height=15, bg=self.grey,
                                                       font=("Montserrat", 10), state='disabled', padx=30, pady=10)
        self.files_textbox.grid(column=0, row=5, columnspan=2, ipady=25)

        # PROGRESSBAR VARIABLES
        self.percentage = StringVar()
        self.current_file = StringVar()
        self.files_completed = StringVar()

        # mainloop
        self._clear_file_selection()
        self.root.mainloop()

    def _directory_popup(self):
        save_location_window = Toplevel(takefocus=True)
        save_location_window.title("Save Location")
        save_location_window.iconbitmap(self.app_icon)
        save_query_label = CTkLabel(save_location_window, text="Where do you wish to save your file(s)?")
        save_query_label.grid(row=0, column=0, columnspan=2)
        current_btn = CTkButton(save_location_window, text="Save in current folder", fg_color=self.blue,
                                command=lambda m="current", window=save_location_window: self._convert_files(m, window))
        current_btn.grid(row=1, column=0, pady=15, padx=15)
        different_btn = CTkButton(save_location_window, text="Save in different folder",fg_color=self.blue,
                                  command=lambda m="different", window=save_location_window: self._convert_files(m,
                                                                                                                 window))
        different_btn.grid(row=1, column=1, padx=15)

    def _upload_files(self):
        files = filedialog.askopenfiles(mode="r", filetypes=[("video files", self.file_list)])
        if files == "":
            return
        self.conversion_list = [i.name for i in files]
        self._render_file_names()

    def _upload_folder(self):
        directory = filedialog.askdirectory()
        if directory == "":
            return
        self.file_save_directory = directory
        directory_list = listdir(directory)  # todo add option to select new save directory,default to current directory
        self.conversion_list = [join(directory, f) for f in directory_list if
                                isfile(join(directory, f)) and f.split(".")[-1].upper() in self.acceptable_file_types
                                ]
        if len(self.conversion_list) == 0:
            messagebox.showerror("Error", "No video files found in selected folder")
            return
        self._render_file_names()

    def _render_file_names(self):
        """renders page content to bottom text box"""

        self.file_save_directory = ntpath.dirname(self.conversion_list[0])
        self.conversion_file_text = ""
        for i in self.conversion_list:
            self.conversion_file_text += f"• {ntpath.basename(i)}\n"
        self.files_textbox.configure(state='normal')
        self._format_file_selection()
        # self._reset_variables()

    def _format_file_selection(self):
        self.files_textbox.configure(state='normal')
        self.files_textbox.delete(1.0, "end")
        self.files_textbox.insert(END, self.conversion_file_text)
        self.files_textbox.configure(state='disabled')

    def _clear_file_selection(self):
        self._reset_variables()
        self._format_file_selection()

    def _reset_variables(self):
        self.conversion_list = []
        self.conversion_file_text = "SELECTED FILES WILL BE SHOWN HERE"

        # @staticmethod

    def _convert_single_file(self, video_path):
        # retrieve file name and join with save directory
        file_name = f"{ntpath.basename(video_path).split('.')[:-1]}.mp3"
        audio_path = ntpath.join(self.file_save_directory, file_name)
        time.sleep(1)
        ## todo get the progress of the conversion and update it to file progressbar

        # convert file
        # video = self.mp.VideoFileClip(video_path)
        # video.audio.write_audiofile(audio_path)

    def _convert_files(self, m, window):
        window.destroy()
        self.file_save_directory = filedialog.askdirectory() if m == "different" else self.file_save_directory
        x = len(self.conversion_list)
        if x == 0:
            messagebox.showerror("No files", "No files selected to convert")
            return
        # Bars
        main_progress_frame = Toplevel(takefocus=True)
        main_progress_frame.maxsize(width=500, height=300)
        main_progress_frame.minsize(width=500, height=300)
        main_progress_frame.title(self.percentage)

        main_progress_frame.iconbitmap(self.app_icon)
        main_progressbar = Progressbar(main_progress_frame, orient=HORIZONTAL, length=400)
        main_progressbar.pack()
        main_progressbar_label = CTkLabel(main_progress_frame,
                                          textvariable=self.files_completed)
        main_progressbar_label.pack()

        ## file progress bar
        ## todo activate bar after getting progress of convertion
        # file_progressbar = Progressbar(main_progress_frame, orient=HORIZONTAL, length=400)
        # file_progressbar.pack()
        file_progressbar_label = CTkLabel(main_progress_frame, textvariable=self.current_file)
        file_progressbar_label.pack()

        for i in range(x):
            main_progressbar["value"] += (10 / x)
            current = self.conversion_list[i]
            filename = ntpath.basename(current)
            self._convert_single_file(current)
            self.files_completed.set(f"{i + 1}/{x} files completed")
            self.percentage.set(f"{int((i / x) * 100)} progress completed")
            self.current_file.set(f"Audiofying {filename}...")
            self.root.update_idletasks()
        main_progress_frame.destroy()
        messagebox.showinfo("Conversion complete", "All your files have been converted.")
        filedialog.Open(self.file_save_directory)


app = VideoToAudio()
