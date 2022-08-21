from tkinter import filedialog, Menu, Frame, Tk, Text, END, WORD, scrolledtext, Toplevel
from customtkinter import CTkButton, CTkLabel, CTk, CTkFrame
from os import listdir
from os.path import isfile, join
import ntpath

bg_color = 'white'
import moviepy.editor as mp
import imageio


class VideoToAudio:
    def __init__(self):
        # CONSTS
        self.acceptable_file_types = ["MP4", "MOV", "WMV", "AVI", "FLV", "MKV", "WEBM"]
        self.file_types = ", ".join(self.acceptable_file_types).lower()
        self.file_list = " ".join(self.acceptable_file_types).lower()
        self.mp = mp

        # VARIABLES
        self.conversion_list = []
        self.conversion_file_text = ""
        self.file_save_directory = None

        # /********ROOT**********/
        # self.root = tkinter.Tk()
        self.root = CTk()
        self.root.title("Text to speech")
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
        # self.file_menu = Menu(self.main_menu)

        # Home frame
        self.home_frame = Frame(self.root, bg="red")
        self.home_frame.pack(fill="both")

        self.main_label = CTkLabel(self.home_frame, text="Audiofyyy!", text_font=("Montserrat", 30, "bold"))
        self.main_label.grid(row=0, column=0, columnspan=2)
        self.description_label = CTkLabel(self.home_frame, text=f"Convert your {self.file_types} files to audio",
                                          text_font=("Montserrat", 15, "italic"))
        self.description_label.grid(row=1, column=0, columnspan=2)

        self.select_files_btn = CTkButton(self.home_frame, text="Select Files(s)", command=self._upload_files)
        self.select_files_btn.grid(row=2, column=0, pady=10)

        self.select_files_btn = CTkButton(self.home_frame, text="Select Folder", command=self._upload_folder)
        self.select_files_btn.grid(row=2, column=1)

        self.clear_btn = CTkButton(self.home_frame, text="Clear Selection", command=self._clear_file_selection)
        self.clear_btn.grid(row=3, column=0, columnspan=2)
        self.convert_btn = CTkButton(self.home_frame, text="Convert selected files", command=self._convert_files)
        self.convert_btn.grid(row=4, column=0, columnspan=2, pady=10)

        self.files_textbox = scrolledtext.ScrolledText(self.home_frame, height=15, bg="lightgrey",
                                                       font=("Montserrat", 10), state='disabled', padx=30, pady=10)
        self.files_textbox.grid(column=0, row=5, columnspan=2, ipady=25)

        ##TOP LEVELS
        self.save_location_window = Toplevel(takefocus=True)
        self.save_query_label = CTkLabel(self.save_location_window, text="Where do you wish to save your file(s)?")
        self.save_query_label.pack()
        self.current_btn = CTkButton(self.save_location_window, text="Save in current folder",
                                     command=lambda m="current": self._convert_files(m))
        self.current_btn.pack()
        self.different_btn = CTkButton(self.save_location_window, text="Save in different folder",
                                       command=lambda m="different": self._convert_files(m))
        self.different_btn.pack()

        # self.
        # self.top
        # mainloo
        self._clear_file_selection()
        self.root.mainloop()

    def hide_all_frames(self):
        self.home_frame.pack_forget()

    def _upload_files(self):
        files = filedialog.askopenfiles(mode="r", filetypes=[("video files", self.file_list)])
        self.conversion_list = [i.name for i in files]
        self.file_save_directory = ntpath.dirname(self.conversion_list[0])
        self._render_file_names()

    def _upload_folder(self):
        directory = filedialog.askdirectory()
        self.file_save_directory = directory
        directory_list = listdir(directory)  # todo add option to select new save directory,default to current directory
        self.conversion_list = [join(directory, f) for f in directory_list if
                                isfile(join(directory, f)) and f.split(".")[-1].upper() in self.acceptable_file_types
                                ]
        self._render_file_names()

    def _render_file_names(self):
        """renders page content to bottom text box"""
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
        #retrieve file name and join with save directory
        print(video_path)
        file_name = f"{ntpath.basename(video_path).split('.')[:-1]}.mp3"
        audio_path = ntpath.join(self.file_save_directory, file_name)
        # print(audio_path)
        # video = self.mp.VideoFileClip(video_path)
        # video.audio.write_audiofile(audio_path)

    def _convert_files(self, m):
        self.file_save_directory = filedialog.askdirectory() if m == "different" else self.file_save_directory
        print(self.file_save_directory)
        for i in self.conversion_list:
            print(i)
            self._convert_single_file(i)
            pass


app = VideoToAudio()
