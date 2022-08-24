from tkinter import Toplevel,HORIZONTAL
from tkinter.ttk import Progressbar
from customtkinter import CTkButton, CTkLabel



def folder_select(btn_command, btn_colour, rx, ry, app_icon):
    save_location_window = Toplevel()
    save_location_window.title("Save Location")
    save_location_window.geometry(
        "+%d+%d" % (rx + 400, ry + 300))
    save_location_window.iconbitmap(app_icon)
    save_query_label = CTkLabel(
        save_location_window, text="Where do you wish to save your file(s)?")
    save_query_label.grid(row=0, column=0, columnspan=2)
    current_btn = CTkButton(save_location_window, text="Current folder", fg_color=btn_colour,
                            command=lambda: btn_command("current", save_location_window))
    current_btn.grid(row=1, column=0, pady=15, padx=15)
    current_btn.focus()
    different_btn = CTkButton(master=save_location_window, text="Choose different folder", fg_color=btn_colour,
                              command=lambda: btn_command("different", save_location_window))
    different_btn.grid(row=1, column=1, padx=15)


class DWindow:
    def __init__(self, event, c_cmd, bgcolor, rx, ry, app_icon, files_completed_var, time_left_var, finish_time_var,
                 current_file_var):
        self.main_progress_frame = Toplevel(takefocus=True)
        self.main_progress_frame.configure(bg=bgcolor)
        self.main_progress_frame.maxsize(width=700, height=300)
        self.main_progress_frame.minsize(width=700, height=300)
        self.main_progress_frame.title(
            "Converting ....")  # todo make the progress window title dynamic to show percentage completion
        self.main_progress_frame.geometry("+%d+%d" % (rx + 650, ry + 450))

        self.main_progress_frame.iconbitmap(app_icon)
        self.main_progressbar = Progressbar(
            self.main_progress_frame, orient=HORIZONTAL, length=500, maximum=10)
        self.main_progressbar.pack(pady=10)

        self.main_progressbar_label = CTkLabel(self.main_progress_frame,
                                               textvariable=files_completed_var, bg_color=bgcolor, )
        self.main_progressbar_label.pack()

        self.time_left_label = CTkLabel(self.main_progress_frame,
                                        textvariable=time_left_var, bg_color=bgcolor, text_font=("Arial", 8))
        self.time_left_label.pack()

        self.finishing_label = CTkLabel(self.main_progress_frame,
                                        textvariable=finish_time_var, bg_color=bgcolor, text_font=(
                "Arial", 8),
                                        anchor="w")
        self.finishing_label.pack()

        self.file_progressbar = Progressbar(
            self.main_progress_frame, orient=HORIZONTAL, length=500, mode="indeterminate")
        self.file_progressbar.pack(pady=10)

        self.file_progressbar_label = CTkLabel(self.main_progress_frame, textvariable=current_file_var,
                                               bg_color=bgcolor,
                                               text_font=("Montserrat", 7), wraplength=450, anchor="w"
                                               )
        self.file_progressbar_label.pack()
        self.cancel_Button = CTkButton(
            self.main_progress_frame, text="Cancel conversion", command=lambda: self._on_bar_close(c_cmd, event))
        self.cancel_Button.pack(pady=10)
        self.main_progress_frame.protocol("WM_DELETE_WINDOW", lambda: self._on_bar_close(c_cmd, event))

    def _on_bar_close(self, cmd, event):
        if cmd(): event.set()
        self.main_progress_frame.destroy()
