import ntpath
import os
import time
from os import listdir
from os.path import isfile, join
from threading import Thread, Event
from tkinter import filedialog, Menu, Frame, END, scrolledtext, messagebox,WORD, StringVar
import tkinter

import func_timeout
import moviepy.editor as mp
from customtkinter import CTkButton, CTkLabel, CTk
from windows import DWindow, folder_select

from functions import convert_time, get_file_duration, calc_time_left

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
        self.textbox_file_text = ""
        self.file_save_directory = None
        self.completed = 0
        self.failed = 0
        self.duplicates = 0
        self.aborted = 0
        self.duplicates_list = []
        self.failed_list = []
        self.aborted_list = []
        self.last_f_skipped = False
        self.prev_end = 0
        self.prev_start = 0
        self.conversion_start = None

        # Thread man
        self.threads = []
        self.event = Event()

        # /********ROOT**********/
        # self.root = tkinter.Tk()
        self.root = CTk()
        self.root.title("Text to speech")
        self.root.iconbitmap(self.app_icon)
        self.root.geometry(f"{800}x{600}")
        self.root.minsize(800, 600)
        self.root.maxsize(800, 600)
        self.root.config(  # padx=50, pady=50,
            bg=self.blue)

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
        self.home_frame.pack(fill="both", expand=True, padx=30, pady=(10, 10))

        # PROGRESSBAR VARIABLES
        self.time_left_label_var = StringVar()
        self.percentage_text_var = StringVar()
        self.finish_time_var = StringVar()
        self.time_left_var = StringVar()
        self.current_file_var = StringVar()
        self.files_completed_var = StringVar()

        self.main_label = CTkLabel(
            self.home_frame, text="Audiofyyy!", text_font=("Montserrat", 30, "bold"))
        self.main_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        self.description_label = CTkLabel(self.home_frame,
                                          text=f"Convert your {self.file_types} files to audio (.mp3) files",
                                          text_font=("Montserrat", 15), wraplength=900)
        self.description_label.grid(row=1, column=0, columnspan=2)

        self.select_files_btn = CTkButton(self.home_frame, text="Select Files(s)", fg_color=self.grey,
                                          command=lambda: self._manage_btn("select_files"))
        self.select_files_btn.grid(row=2, column=0, pady=5)

        self.select_files_btn = CTkButton(self.home_frame, text="Select Folder", fg_color=self.grey,
                                          command=lambda: self._manage_btn("select_folder"))
        self.select_files_btn.grid(row=2, column=1)

        self.clear_btn = CTkButton(self.home_frame, text="Clear Selection",
                                   command=lambda: self._manage_btn(
                                       "clear_selection"),
                                   fg_color=self.grey)
        self.clear_btn.grid(row=3, column=0, columnspan=2, pady=5)

        self.convert_btn = CTkButton(self.home_frame, text="Convert selected files", fg_color="orange3", state="normal",
                                     command=lambda: self._manage_btn("convert_selection"))
        self.convert_btn.grid(row=4, column=0, columnspan=2)

        self.progress_frame = Frame(self.home_frame)
        self.progress_frame.grid(row=5, column=0, columnspan=2, pady=10)
        self.percentage_text_label = CTkLabel(self.progress_frame, bg_color=self.blue,
                                              textvariable=self.percentage_text_var)
        self.percentage_text_label.grid(row=0, column=0, sticky="w")
        self.time_left_label = CTkLabel(self.progress_frame, bg_color=self.blue, textvariable=self.time_left_label_var)
        self.time_left_label.grid(row=0, column=1)

        self.scroll_frame = Frame(self.home_frame)
        self.scroll_frame.grid(row=6, column=0, columnspan=2, padx=(10, 10))
        self.files_textbox = scrolledtext.ScrolledText(self.scroll_frame, height=15, bg=self.grey,
                                                       font=("Montserrat", 10))
        self.files_textbox.pack(fill="both")
        self.files_textbox.tag_add("top_highlight", "1.0", "1.end+1c")

        # mainloop
        self._render_file_names(self.conversion_list)
        self._reset_variables()

        self.root.mainloop()

    def _directory_popup(self):
        if len(self.conversion_list) == 0:
            messagebox.showerror("No files", "No files selected to convert")
            return
        folder_select(self._convert_files, self.blue, self.rx, self.ry, self.app_icon)

    def _cancel_conversion(self):
        return messagebox.askokcancel("Stop conversion", "Cancel ongoing conversion?")

    def _end_of_conversion(self):
        self._render_file_names([], final=True)
        self.convert_btn.configure(
            state=tkinter.NORMAL, text="Convert selected files")
        self.clear_btn.configure(state=tkinter.NORMAL, text="Clear Selection",
                                 command=lambda: self._manage_btn("clear_selection"))
        time_taken = convert_time(self.prev_end - self.conversion_start)
        feedback = f"\n{self.completed} files converted.\n{self.duplicates} duplicates found.\n{self.failed + self.aborted} failed conversions.\n{len(self.conversion_list)} total files.\nTime taken = {time_taken}"
        if not self.event.is_set():
            messagebox.showinfo("Conversion complete",
                                f"All Done.\n{feedback}")
        else:
            messagebox.showerror(
                "Conversion canceled", f"Conversion canceled.\n{feedback}")
        self._reset_variables()

    def _manage_btn(self, btn):
        if btn == "end_current_conversion":
            self.event.set() if self._cancel_conversion() else None
        elif self.convert_btn.state == tkinter.DISABLED:
            messagebox.showerror("Conversion in Progress",
                                 "There is an ongoing conversion process. End it to select other files")
            return
        else:
            if btn == "select_files":
                self._upload_files()
            elif btn == "select_folder":
                self._upload_folder()
            elif btn == "clear_selection":
                self._reset_variables()
                self._render_file_names([])
            elif btn == "convert_selection":
                self._directory_popup()

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
        directory_list = listdir(directory)
        self.conversion_list = [join(directory, f) for f in directory_list if
                                isfile(join(directory, f)) and os.path.splitext(f)[
                                    -1].upper() in self.acceptable_file_types]
        if len(self.conversion_list) == 0:
            messagebox.showerror(
                "Error", "No video files found in selected folder")
            return
        self.file_save_directory = directory
        self._render_file_names(self.conversion_list)

    def _reset_variables(self):
        self.conversion_list = []
        self.completed = 0
        self.failed = 0
        self.duplicates = 0
        self.aborted = 0
        self.duplicates_list = []
        self.failed_list = []
        self.aborted_list = []
        self.file_save_directory = None
        self.event = Event()
        self.finish_time_var.set("")
        self.time_left_var.set("")
        self.current_file_var.set("")
        self.files_completed_var.set("")
        self.time_left_label_var.set("")
        self.percentage_text_var.set("")
        self.last_f_skipped = False
        self.prev_end = 0
        self.prev_start = 0
        self.conversion_start = None

    def _convert_single_file(self, video_path):
        def convert_file(path):
            """convert file to mp3"""
            clip = mp.VideoFileClip(video_path)
            clip.audio.write_audiofile(path)
            clip.close()

        basename = ntpath.basename(video_path)
        new_filename = f"{os.path.splitext(basename)[0]}.mp3"
        audio_path = ntpath.join(self.file_save_directory, new_filename)
        skipped_status = True
        self.prev_start = time.time()
        try:
            # check if file already exists
            if os.path.exists(audio_path):
                raise FileExistsError("")
            time_out = get_file_duration(video_path) // 20
            func_timeout.func_timeout(time_out, convert_file, (audio_path,))
            self.completed += 1
            skipped_status = False
        except FileExistsError:
            self.duplicates += 1
            self.duplicates_list.append(new_filename)
        except func_timeout.FunctionTimedOut:
            # handle long conversions
            self.aborted += 1
            self.aborted_list.append(basename)
        except:
            # catch all other fails
            self.failed += 1
            self.failed_list.append(basename)
        finally:
            self.last_f_skipped = skipped_status
            self.prev_end = time.time()

    def _convert_files(self, m, window):
        self.file_save_directory = filedialog.askdirectory(
        ) if m == "different" else self.file_save_directory
        t1 = Thread(target=self.run_threading)
        window.destroy()
        t1.start()

    def run_threading(self):
        # Bars
        max_iter = len(self.conversion_list)
        render_list = self.conversion_list.copy()
        self.conversion_start = time.time()
        y = 0
        self.convert_btn.configure(
            state=tkinter.DISABLED, text="Converting files...")
        self.clear_btn.configure(text="Cancel current conversion",
                                 command=lambda: self._manage_btn("end_current_conversion"))

        d_window = DWindow(self.event, self._cancel_conversion, self.grey, self.rx, self.ry, self.app_icon,
                           self.files_completed_var, self.time_left_var, self.finish_time_var,
                           self.current_file_var)
        self.files_completed_var.set("Parsing your files,please wait...")
        time.sleep(1)
        d_window.file_progressbar.start(10)
        self.files_completed_var.set("Initializing conversion engine...")

        # change to while for loop
        while not self.event.is_set() and y < max_iter:
            current = self.conversion_list[y]
            filename = ntpath.basename(current)
            t = calc_time_left(render_list, y, max_iter, self.conversion_start, self.completed, self.prev_start,
                               self.prev_end,
                               self.last_f_skipped)
            percent = (y / max_iter) * 100
            p = f"{int(percent)}%, {max_iter - y} of {max_iter} files remaining"
            time_text = f"{t[0]} left"
            self.percentage_text_var.set(p)
            self.time_left_label_var.set(time_text)
            # Bar updates
            self.files_completed_var.set(
                f"{p}\n\nEstimated completion time: {t[1]}")
            self.time_left_var.set(time_text)
            self.finish_time_var.set(
                f"{self.completed} converted, {self.duplicates} duplicates found, {self.failed + self.aborted} aborted\nConverting file {y + 1} of {max_iter}  ")
            self.current_file_var.set(f"Audiofying {filename}...")
            self._render_file_names(render_list, converting=True)
            self._convert_single_file(current)
            try:
                d_window.main_progressbar["value"] += (10 / max_iter)
            except:
                pass
            self.root.update_idletasks()
            render_list.remove(current)
            y += 1

        if d_window.main_progress_frame.winfo_exists():
            d_window.main_progress_frame.destroy()
        self._end_of_conversion()

    def _render_file_names(self, list_to_render, converting=False, final=False):
        """renders page content to bottom text box"""
        tag_font = ("Montserrat", 10, "bold")
        text = ""

        if final:
            dup_info = f"DUPLICATE FILES FOUND - ({self.duplicates})"
            abort_info = f"CONVERSIONS ABORTED/TIMED OUT - ({self.aborted})"
            failed_info = f"CONVERSIONS FAILED - ({self.failed})"
            top_text = f"{failed_info}, {abort_info}, {dup_info}\n\n"
            dup_len, abort_len, fail_len, = len(
                self.duplicates_list), len(self.aborted_list), len(self.failed_list)
            for i in self.duplicates_list:
                dup_info += f"\n• {i}"
            for i in self.failed_list:
                failed_info += f"\n• {i}"
            for i in self.aborted_list:
                abort_info += f"\n• {i}"
            # render options
            successful = "ALL FILES WERE SUCCESSFULLY CONVERTED"
            f1 = f"{failed_info}\n\n{abort_info}\n\n{dup_info}"
            f2 = f"{failed_info}\n\n{abort_info}"
            f3 = f"{failed_info}\n\n{dup_info}"
            f4 = f"{failed_info}"
            f5 = f"{abort_info}\n\n{dup_info}"
            f6 = f"{abort_info}"
            f7 = f"{dup_info}"
            if dup_len == fail_len == abort_len == 0:
                self.textbox_file_text = successful
            else:
                self.textbox_file_text = top_text
                if fail_len > 0:
                    if dup_len == 0:
                        if abort_len > 0:
                            self.textbox_file_text += f2
                        else:
                            self.textbox_file_text += f4
                    elif dup_len > 0 and abort_len == 0:
                        self.textbox_file_text += f3
                    else:
                        self.textbox_file_text += f1
                elif fail_len == 0:
                    if abort_len > 0 and dup_len > 0:
                        self.textbox_file_text += f5
                    elif abort_len == 0 and dup_len > 0:
                        self.textbox_file_text += f7
                    else:
                        self.textbox_file_text += f6
        else:
            if len(list_to_render) == 0:
                text = "SELECTED FILES WILL BE DISPLAYED HERE"
            else:
                for i in list_to_render:
                    text += f"• {ntpath.basename(i)}\n"
            self.textbox_file_text = text

        self.files_textbox.config(state="normal")
        self.files_textbox.delete(1.0, "end")
        self.files_textbox.insert(END, self.textbox_file_text)
        if converting or final:
            self.files_textbox.tag_add("top_highlight", "1.0", "1.end+1c")
            if converting:
                self.files_textbox.tag_config(
                    "top_highlight", font=tag_font, foreground="orange3")
            else:
                self.files_textbox.tag_config(
                    "top_highlight", font=tag_font, foreground="red")
        else:
            self.files_textbox.tag_remove("top_highlight", "1.0", "1.end+1c")
        self.files_textbox.config(wrap=WORD, state="disabled")
