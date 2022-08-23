import datetime
import ntpath
import os
import time
from functools import reduce
from os import listdir
from os.path import isfile, join
from threading import Thread, Event
from tkinter import filedialog, Menu, Frame, END, scrolledtext, Toplevel, messagebox, HORIZONTAL, WORD, StringVar
from tkinter.ttk import Progressbar

import func_timeout
import moviepy.editor as mp
from customtkinter import CTkButton, CTkLabel, CTk

from functions import calc_time
from cv2 import cv2

bg_color = 'white'


class FileExistsError(Exception):
    pass


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
        self.files_textbox.tag_add("top_highlight", "1.0", "1.end+1c")

        # PROGRESSBAR VARIABLES
        self.finish_time_var = StringVar()
        self.time_left_var = StringVar()
        self.current_file_var = StringVar()
        self.files_completed_var = StringVar()

        # mainloop
        self._render_file_names(self.conversion_list, False)
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
        current_btn = CTkButton(save_location_window, text="Current folder", fg_color=self.blue,
                                command=lambda: self._convert_files("current", save_location_window))
        current_btn.grid(row=1, column=0, pady=15, padx=15)
        different_btn = CTkButton(master=save_location_window, text="Choose different folder", fg_color=self.blue,
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
        self._render_file_names(self.conversion_list, False)

    def _upload_folder(self):
        directory = filedialog.askdirectory()
        if directory == "":
            return
        directory_list = listdir(directory)
        self.conversion_list = [join(directory, f) for f in directory_list if
                                isfile(join(directory, f)) and os.path.splitext(f)[
                                    -1].upper() in self.acceptable_file_types]
        if len(self.conversion_list) == 0:
            messagebox.showerror(
                "Error", "No video files found in selected folder")
            return
        self.file_save_directory = directory
        self._render_file_names(self.conversion_list, False)

    def _reset_variables(self):
        self.conversion_list = []
        self.conversion_file_text = "SELECTED FILES WILL BE SHOWN HERE"
        self.completed = 0
        self.incompleted = 0
        self.duplicates = 0
        self.file_save_directory = None

    def _convert_single_file(self, video_path):
        def audio_path():
            x = ntpath.basename(video_path)
            file_name = f"{os.path.splitext(x)[0]}.mp3"
            return ntpath.join(self.file_save_directory, file_name)

        def convert_file():
            """convert file to mp3"""
            clip = mp.VideoFileClip(video_path)
            clip.audio.write_audiofile(audio_path)
            clip.close()
            self._monitor_completed(1, 0, 0)

        try:
            audio_path = audio_path()
            # check if file already exists
            if os.path.exists(audio_path):
                raise FileExistsError("")
            time_out = VideoToAudio._get_file_duration(video_path) // 30
            func_timeout.func_timeout(time_out, convert_file)
        except Exception as e:
            if type(e) == FileExistsError:
                self._monitor_completed(0, 0, 1)
            else:
                # handle none types and long conversions
                self._monitor_completed(0, 1, 0)
        finally:
            return

    @staticmethod
    def _get_file_duration(video_path):
        t = 0

        def cv_timeout():
            video = cv2.VideoCapture(video_path)
            frames = video.get(cv2.CAP_PROP_FRAME_COUNT)
            fps = video.get(cv2.CAP_PROP_FPS)
            return int(frames / fps)

        try:
            t = func_timeout.func_timeout(0.5, cv_timeout)
        except Exception as e:
            t = 600
        finally:
            return t

    def _monitor_completed(self, x, y, z):
        """keep track of files"""
        self.completed += x
        self.incompleted += y
        self.duplicates += z

    def _convert_files(self, m, window):
        self.file_save_directory = filedialog.askdirectory(
        ) if m == "different" else self.file_save_directory
        window.destroy()
        event = Event()
        t = Thread(target=self.run_threading, args=(event,))
        t.start()
        # t.join()

    @calc_time
    def run_threading(self, event):
        # Bars
        x = len(self.conversion_list)
        render_list = self.conversion_list.copy()
        start_time = time.time()
        y = 0

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
                                          textvariable=self.files_completed_var, bg_color=self.grey, )
        main_progressbar_label.pack()

        time_left_label = CTkLabel(main_progress_frame,
                                   textvariable=self.time_left_var, bg_color=self.grey, text_font=("Arial", 8))
        time_left_label.pack()

        finishing_label = CTkLabel(main_progress_frame,
                                   textvariable=self.finish_time_var, bg_color=self.grey, text_font=(
                "Arial", 8),
                                   anchor="w")
        finishing_label.pack()

        file_progressbar = Progressbar(
            main_progress_frame, orient=HORIZONTAL, length=500, mode="indeterminate")
        file_progressbar.pack(pady=10)

        file_progressbar_label = CTkLabel(main_progress_frame, textvariable=self.current_file_var, bg_color=self.grey,
                                          text_font=("Montserrat", 7), wraplength=450, anchor="w"
                                          )
        file_progressbar_label.pack()

        cancel_Button = CTkButton(
            main_progress_frame, text="Cancel conversion", command=lambda: event.set())
        cancel_Button.pack(pady=10)

        # THREAD NESTED FUNCTIONS
        def convert_time(seconds_to_convert):
            mins, secs = divmod(seconds_to_convert, 60)
            hours, mins = divmod(mins, 60)
            hours = int(hours)
            mins = int(mins)
            secs = int(secs)
            h_f = f"{hours} hours" if hours != 1 else f"{hours} hour"
            m_f = f"{mins} minutes" if mins != 1 else f"{mins} minute"
            s_f = f"{secs} seconds" if secs != 1 else f"{secs} second"
            if hours > 0:
                return f"{h_f} {m_f}"
            elif mins > 0:
                return f"{m_f} {s_f}"
            else:
                return f"{s_f}"

        def _generate_total_file_time(remaining_list):
            # very inefficient #todo modify this to be workable
            total_file_time = 0
            for i in remaining_list:
                total_file_time += VideoToAudio._get_file_duration(i)
            return total_file_time

        def calc_time_left(remaining_files, t_start, curr_iter, max_iter):
            f_time = 0
            t_left = 0
            try:
                if len(remaining_files) > 10:
                    raise FileExistsError("Too many files to approximate")

                total = func_timeout.func_timeout(2, _generate_total_file_time, args=(remaining_files,))
                t_left = total // 30
                f_time = time.time() + t_left

            except (func_timeout.FunctionTimedOut, FileExistsError):
                t_elapsed = time.time() - t_start
                if curr_iter == 0:
                    t_elapsed += 10
                t_est = (t_elapsed / ((self.completed + 1) if self.completed == 0 else self.completed)) * max_iter
                t_left = t_est - t_elapsed
                f_time = t_start + t_est
            finally:
                f_time = datetime.datetime.fromtimestamp(
                    # f_time).strftime("%I:%M:%S %p, ")
                    f_time).strftime("%c")
                return convert_time(t_left), f_time

        def end_of_conversion(state, list_length, start, end):
            self._render_file_names([], False)
            main_progress_frame.destroy()
            time_taken = convert_time(end - start)
            feedback = f"\nConverted files = {self.completed}\nDuplicates found = {self.duplicates}\nFailed/aborted conversions = {self.incompleted}\nTotal files = {list_length}\nTime taken = {time_taken}"
            if not state:
                messagebox.showinfo("Conversion complete",
                                    f"All Done.\n{feedback}")
            else:
                messagebox.showerror(
                    "Conversion canceled", f"Conversion canceled.\n{feedback}")
            self._reset_variables()

        self.files_completed_var.set("Parsing your files,please wait...")
        time.sleep(1)
        file_progressbar.start(10)
        self.files_completed_var.set("Initializing conversion engine...")

        # change to while for loop
        while not event.is_set() and y < x:
            current = self.conversion_list[y]
            filename = ntpath.basename(current)
            t = calc_time_left(render_list, start_time, y, x)
            # t = calc_time_left(render_list)
            self.files_completed_var.set(
                f"{int((y / x) * 100)}% complete.\n\nEstimated completion time: {t[1]}")
            self.time_left_var.set(f"{t[0]} left")
            self.finish_time_var.set(
                f"{self.completed} files converted, {self.duplicates} duplicates found {self.incompleted} files skipped\nConverting file {y} of {x}")
            self.current_file_var.set(f"Audiofying {filename}...")
            self._render_file_names(render_list, True)
            self._convert_single_file(current)
            main_progressbar["value"] += (10 / x)
            self.root.update_idletasks()

            render_list.remove(current)
            y += 1
        end_time = time.time()
        end_of_conversion(event.is_set(), x, start_time, end_time)

    def _render_file_names(self, list_to_render, converting):
        """renders page content to bottom text box"""
        tag_font = ("Montserrat", 10)
        text = ""
        for i in list_to_render:
            text += f"• {ntpath.basename(i)}\n"
        self.conversion_file_text = "SELECTED FILES WILL BE SHOWN HERE" if len(
            list_to_render) == 0 else text
        self.files_textbox.delete(1.0, "end")
        self.files_textbox.insert(END, self.conversion_file_text)
        if converting:
            self.files_textbox.tag_add("top_highlight", "1.0", "1.end+1c")
            self.files_textbox.tag_config(
                "top_highlight", font=tag_font, foreground="red")
        else:
            self.files_textbox.tag_remove("top_highlight", "1.0", "1.end+1c")
        self.files_textbox.config(wrap=WORD)
