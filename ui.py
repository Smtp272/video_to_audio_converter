import moviepy.editor as mp
from tkinter import filedialog, Menu, Frame, END, scrolledtext, Toplevel, messagebox, HORIZONTAL, WORD, StringVar
from tkinter.ttk import Progressbar
from customtkinter import CTkButton, CTkLabel, CTk
from os import listdir
from os.path import isfile, join
import os
import ntpath
import time
import datetime
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
        self.completed = 0
        self.incompleted = 0
        self.duplicates = 0

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

        self.clear_btn = CTkButton(self.home_frame, text="Clear Selection", command=self._reset_variables,
                                   fg_color=self.grey)
        self.clear_btn.grid(row=3, column=0, columnspan=2)

        self.convert_btn = CTkButton(self.home_frame, text="Convert selected files", fg_color="orange3",
                                     command=self._directory_popup)
        self.convert_btn.grid(row=4, column=0, columnspan=2, pady=10)

        self.files_textbox = scrolledtext.ScrolledText(self.home_frame, height=15, bg=self.grey,
                                                       font=("Montserrat", 10), padx=30, pady=10)
        self.files_textbox.grid(column=0, row=5, columnspan=2, ipady=25)

        # PROGRESSBAR VARIABLES
        self.finish_time = StringVar()
        self.time_left = StringVar()
        self.current_file = StringVar()
        self.files_completed = StringVar()

        # mainloop
        self._reset_variables()
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
        self.file_save_directory = ntpath.dirname(self.conversion_list[0])
        self._render_file_names(self.conversion_list)

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
        self._render_file_names(self.conversion_list)

    def _reset_variables(self):
        self.conversion_list = []
        self.conversion_file_text = "SELECTED FILES WILL BE SHOWN HERE"
        self.completed = 0
        self.incompleted = 0
        self.duplicates = 0
        self._render_file_names(self.conversion_list)

    def _convert_single_file(self, video_path):
        # retrieve file name and join with save directory
        try:
            x = ntpath.basename(video_path)
            file_name = f"{os.path.splitext(x)[0]}.mp3"
            audio_path = ntpath.join(self.file_save_directory, file_name)

            # handle duplicates
            if os.path.exists(audio_path):
                self._monitor_completed(0, 0, 1)
                return

            # convert file
            video = mp.VideoFileClip(video_path)
            video.audio.write_audiofile(audio_path)
            self._monitor_completed(1, 0, 0)
        except Exception as e:
            # handle none types
            self._monitor_completed(0, 1, 0)
            return

    def _monitor_completed(self, x, y, z):
        """keep track of files"""
        self.completed += x
        self.incompleted += y
        self.duplicates += z

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
        main_progress_frame.maxsize(width=700, height=300)
        main_progress_frame.minsize(width=700, height=300)
        main_progress_frame.title(
            "Converting ....")  # todo make the progress window title dynamic to show percentage completion
        main_progress_frame.geometry("+%d+%d" % (self.rx + 650, self.ry + 450))

        main_progress_frame.iconbitmap(self.app_icon)
        main_progressbar = Progressbar(
            main_progress_frame, orient=HORIZONTAL, length=500, maximum=10)
        main_progressbar.pack(pady=10)

        main_progressbar_label = CTkLabel(main_progress_frame,
                                          textvariable=self.files_completed, bg_color=self.grey,)
        main_progressbar_label.pack()

        time_left_label = CTkLabel(main_progress_frame,
                                   textvariable=self.time_left, bg_color=self.grey, text_font=("Arial", 8), anchor="w")
        time_left_label.pack()

        finishing_label = CTkLabel(main_progress_frame,
                                   textvariable=self.finish_time, bg_color=self.grey, text_font=("Arial", 8), anchor="w")
        finishing_label.pack()

        file_progressbar = Progressbar(
            main_progress_frame, orient=HORIZONTAL, length=500, mode="indeterminate")
        file_progressbar.pack(pady=10)

        file_progressbar_label = CTkLabel(main_progress_frame, textvariable=self.current_file, bg_color=self.grey, text_font=("Montserrat", 7),wraplength=450,anchor="w"
                                          )
        file_progressbar_label.pack()

        cancel_Button = CTkButton(
            main_progress_frame, text="Cancel conversion", command=event.set)
        cancel_Button.pack(pady=10)

        # THREAD NESTED FUNCTIONS
        def update_delay(n):
            self.files_completed.set(n)
            time.sleep(1)

        def end_of_conversion(state, list_length):
            main_progress_frame.destroy()
            feedback = f"Converted files = {self.completed}\nDuplicates found = {self.duplicates}\nTotal files = {list_length}"
            if not state:
                messagebox.showinfo("Conversion complete",
                                    f"All Done.\n{feedback}")
            else:
                messagebox.showerror(
                    "Conversion canceled", f"Conversion canceled.\n{feedback}")
            self._reset_variables()

        def convert_time(seconds_to_convert):
            mins, secs = divmod(seconds_to_convert, 60)
            hours, mins = divmod(mins, 60)
            hours = int(hours)
            mins = int(mins)
            secs = int(secs)
            if hours > 0:
                return f"{hours} hours and {mins} minutes left"
            elif mins > 0:
                return f'{mins} mins and {secs} seconds left'
            else:
                return f'{secs} seconds left'

        def calc_time_left(t_start, curr_iter, max_iters):
            t_elapsed = time.time() - t_start
            if curr_iter == 1:
                t_elapsed += 10
            t_est = (t_elapsed/curr_iter)*max_iters
            t_left = t_est - t_elapsed

            f_time = t_start + t_est
            f_time = datetime.datetime.fromtimestamp(
                f_time).strftime("%H:%M:%S")

            return convert_time(t_left),f_time

        update_delay("Preparing your files...")
        update_delay("Initializing conversion engine...")

        x = len(self.conversion_list)
        render_list = self.conversion_list.copy()
        file_progressbar.start(10)
        start_time = time.time()
        y = 0

        # change to while for loop
        while not event.is_set() and y < x:
            current = self.conversion_list[y]
            filename = ntpath.basename(current)
            t = calc_time_left(start_time, y+1, x)
            self.files_completed.set(f"{y}/{x} file(s) completed, ")
            self.time_left.set(f"Time left: {t[0]}")
            self.finish_time.set(f"End time: {t[1]}")
            self.current_file.set(f"Audiofying {filename}...")
            self._convert_single_file(current)
            main_progressbar["value"] += (10 / x)

            # update textbox after conversion
            render_list.remove(current)
            self._render_file_names(render_list)
            self.root.update_idletasks()
            y += 1

        end_of_conversion(event.is_set(), x)

    def _render_file_names(self, list_to_render):
        """renders page content to bottom text box"""
        text = ""
        for i in list_to_render:
            text += f"• {ntpath.basename(i)}\n"
        self.conversion_file_text = "SELECTED FILES WILL BE SHOWN HERE" if len(
            list_to_render) == 0 else text
        self.files_textbox.delete(1.0, "end")
        self.files_textbox.insert(END, self.conversion_file_text)
        self.files_textbox.config(wrap=WORD)
