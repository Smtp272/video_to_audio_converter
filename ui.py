import moviepy.editor as mp
from tkinter import filedialog, Menu, Frame, END, scrolledtext, Toplevel, messagebox, HORIZONTAL, WORD, StringVar, LEFT
from tkinter.ttk import Progressbar
from customtkinter import CTkButton, CTkLabel, CTk
from os import listdir
from os.path import isfile, join
import os
import ntpath
import time
from threading import Thread, Event
from functions import calc_time

bg_color = 'white'


class VideoToAudio:
    def __init__(self):
        # CONSTS
        self.acceptable_file_list = ["MP4", "MOV",
                                     "WMV", "AVI", "FLV", "MKV", "WEBM"]
        self.acceptable_file_types = [
            ".MP4", ".MOV", ".WMV", ".AVI", ".FLV", ".MKV", ".WEBM"]
        self.file_types = ", ".join(self.acceptable_file_list).lower()
        self.file_list = " ".join(self.acceptable_file_list).lower()
        self.mp = mp
        self.app_icon = 'icon.ico'
        self.grey = "#E5E5E5"
        self.blue = "#7F7FFF"

        # VARIABLES
        self.conversion_list = []
        self.conversion_file_text = ""
        self.file_save_directory = None

        # Thread man
        self.event = Event()

        # /********ROOT**********/
        # self.root = tkinter.Tk()
        self.root = CTk()
        self.root.title("Text to speech")
        self.root.iconbitmap(self.app_icon)
        self.root.geometry(f"{800}x{600}")
        self.root.minsize(800, 600)
        self.root.maxsize(800, 600)
        self.root.config(padx=50, pady=50)

        self.rx = self.root.winfo_x()
        self.ry = self.root.winfo_y()

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

        self.main_label = CTkLabel(
            self.home_frame, text="Audiofyyy!", text_font=("Montserrat", 30, "bold"))
        self.main_label.grid(row=0, column=0, columnspan=2)
        self.description_label = CTkLabel(self.home_frame,
                                          text=f"Convert your {self.file_types} files to audio (.mp3) files",
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
        if len(self.conversion_list) == 0:
            messagebox.showerror("No files", "No files selected to convert")
            return
        save_location_window = Toplevel()
        save_location_window.wm_transient(self.root)
        save_location_window.title("Save Location")
        save_location_window.geometry(
            "+%d+%d" % (self.rx + 400, self.ry + 300))
        save_location_window.iconbitmap(self.app_icon)
        save_query_label = CTkLabel(
            save_location_window, text="Where do you wish to save your file(s)?")
        save_query_label.grid(row=0, column=0, columnspan=2)
        current_btn = CTkButton(save_location_window, text="Save in current folder", fg_color=self.blue,
                                command=lambda: self._convert_files("current", save_location_window))
        current_btn.grid(row=1, column=0, pady=15, padx=15)
        different_btn = CTkButton(master=save_location_window, text="Save in different folder", fg_color=self.blue,
                                  command=lambda: self._convert_files("different",
                                                                      save_location_window))
        different_btn.grid(row=1, column=1, padx=15)

    def _upload_files(self):
        files = filedialog.askopenfiles(
            mode="r", filetypes=[("video files", self.file_list)])
        if files == "":
            return
        self.conversion_list = [i.name for i in files]
        self._render_file_names()

    def _upload_folder(self):

        directory = filedialog.askdirectory()
        if directory == "":
            return
        self.file_save_directory = directory
        directory_list = listdir(directory)
        self.conversion_list = [join(directory, f) for f in directory_list if
                                isfile(join(directory, f)) and os.path.splitext(f)[
                                    -1].upper() in self.acceptable_file_types]
        if len(self.conversion_list) == 0:
            messagebox.showerror(
                "Error", "No video files found in selected folder")
            return
        self._render_file_names()

    def _render_file_names(self):
        """renders page content to bottom text box"""
        self.file_save_directory = ntpath.dirname(self.conversion_list[0])
        self.conversion_file_text = ""
        for i in self.conversion_list:
            self.conversion_file_text += f"• {ntpath.basename(i)}\n"
        self._format_file_selection()

    def _format_file_selection(self):
        self.files_textbox.configure(state='normal')
        self.files_textbox.delete(1.0, "end")
        self.files_textbox.insert(END, self.conversion_file_text)
        self.files_textbox.config(wrap=WORD)
        self.files_textbox.configure(state='disabled')

    def _clear_file_selection(self):
        self._reset_variables()
        self._format_file_selection()

    def _reset_variables(self):
        self.conversion_list = []
        self.conversion_file_text = "SELECTED FILES WILL BE SHOWN HERE"

    def _convert_single_file(self, video_path):
        # retrieve file name and join with save directory
        x = ntpath.basename(video_path)
        file_name = f"{os.path.splitext(x)[0]}.mp3"
        audio_path = ntpath.join(self.file_save_directory, file_name)
        # todo get the progress of the conversion and update it to file progressbar
        time.sleep(0.2)
        # convert file
        video = self.mp.VideoFileClip(video_path)
        video.audio.write_audiofile(audio_path)

    def _convert_files(self, m, window):
        window.destroy()
        event = Event()
        t = Thread(target=self.run_threading, args=(m, event))
        t.start()

    @calc_time
    def run_threading(self, m, event):
        self.file_save_directory = filedialog.askdirectory(
        ) if m == "different" else self.file_save_directory
        # Bars
        main_progress_frame = Toplevel(takefocus=True)
        main_progress_frame.wm_transient(self.root)
        main_progress_frame.configure(bg=self.grey)
        main_progress_frame.maxsize(width=500, height=200)
        main_progress_frame.minsize(width=500, height=200)
        # main_progress_frame.title(self.percentage)
        main_progress_frame.title(
            "Converting ....")  # todo make the progress window title dynamic to show percentage completion
        main_progress_frame.geometry("+%d+%d" % (self.rx + 650, self.ry + 450))

        main_progress_frame.iconbitmap(self.app_icon)
        main_progressbar = Progressbar(
            main_progress_frame, orient=HORIZONTAL, length=400, maximum=10)
        main_progressbar.pack(pady=10)

        main_progressbar_label = CTkLabel(main_progress_frame,
                                          textvariable=self.files_completed, bg_color=self.grey,)
        main_progressbar_label.pack()

        # todo activate bar after getting progress of convertion
        # file_progressbar = Progressbar(main_progress_frame, orient=HORIZONTAL, length=400)
        # file_progressbar.grid(row=2,column=0,pady=20)

        file_progressbar_label = CTkLabel(main_progress_frame, textvariable=self.current_file, bg_color=self.grey, text_font=("Montserrat", 7), anchor="w"
                                          )
        file_progressbar_label.pack(pady=10,fill="both")

        cancel_Button = CTkButton(
            main_progress_frame, text="Cancel conversion", command=event.set)
        cancel_Button.pack()

        def update_delay(n):
            self.files_completed.set(n)
            time.sleep(2)

        def finish():
            main_progress_frame.destroy()
            self._clear_file_selection()
        update_delay("Preparing your files...")
        update_delay("Initializing conversion engine...")

        x = len(self.conversion_list)

        for i in range(x):
            if not event.is_set():
                current = self.conversion_list[i]
                filename = ntpath.basename(current)
                self.files_completed.set(f"{i}/{x} file(s) completed")
                self.percentage.set(f"{int((i / x) * 100)} progress completed")
                self.current_file.set(f"Audiofying {filename}...")
                self._convert_single_file(current)
                main_progressbar["value"] += (10 / x)
                self.root.update_idletasks()
            else:
                finish()
                messagebox.showerror(
                    "Conversion canceled", f"Conversion canceled.Only {i}/{x} files were converted")
                return

        finish()
        messagebox.showinfo("Conversion complete",
                            "All your files have been converted.")
