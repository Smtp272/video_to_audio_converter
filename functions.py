import time
import datetime
import func_timeout
from cv2 import cv2
import subprocess
import webbrowser

personal_site = "https://github.com/Smtp272"

def open_webpage(e):
    webbrowser.open_new(personal_site)

def calc_time(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__} took {end - start} seconds")
        return result

    return wrapper


def convert_time(seconds_to_convert):
    mins, secs = divmod(seconds_to_convert, 60)
    hours, mins = divmod(mins, 60)
    days, hours = divmod(hours, 24)
    days = int(days)
    hours = int(hours)
    mins = int(mins)
    secs = int(secs)
    d_f = f"{hours} days" if days != 1 else f"{hours} days"
    h_f = f"{hours} hours" if hours != 1 else f"{hours} hour"
    m_f = f"{mins} minutes" if mins != 1 else f"{mins} minute"
    s_f = f"{secs} seconds" if secs != 1 else f"{secs} second"

    if days > 0:
        return f"{d_f} {h_f}"
    elif hours > 0:
        return f"{h_f} {m_f}"
    elif mins > 0:
        return f"{m_f} {s_f}"
    else:
        return f"{s_f}"


def get_file_duration(video_path):
    def cv_timeout():
        try:
            try:
                return ffprobe_len(video_path)
            except:
                return opencv_len(video_path)
        except:
            return 600
    t = 0
    try:
        t = func_timeout.func_timeout(0.5, cv_timeout)
    except Exception:
        t = 600
    finally:
        return t


def opencv_len(file):
    video = cv2.VideoCapture(file)
    x = video.get(cv2.CAP_PROP_POS_MSEC)
    video.release()
    return 600 if x <= 100 else x


def ffprobe_len(file):
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1',
         file], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return float(result.stdout)


def generate_total_file_time(remaining_list):
    # very inefficient #todo modify this to be workable
    total_file_time = 0
    for i in remaining_list:
        total_file_time += get_file_duration(i)
    return total_file_time


def calc_time_left(remaining_files, curr_iter, max_iter, t_start, completed, prev_start, prev_end, skipped):
    f_time = 0
    t_left = 0
    try:
        if len(remaining_files) > 10:
            raise FileExistsError("Too many files to approximate")
        total = func_timeout.func_timeout(
            5, generate_total_file_time, args=(remaining_files,))
        t_left = total // 30
        f_time = time.time() + t_left

    except (func_timeout.FunctionTimedOut, FileExistsError):
        t_elapsed = time.time() - t_start
        t_per_file = prev_end - prev_start

        if skipped:
            t_per_file = t_elapsed / completed if completed > 0 else 10

        t_left = t_per_file * (max_iter - (curr_iter + 1))
        f_time = time.time() + t_left

    finally:
        f_time = datetime.datetime.fromtimestamp(f_time).strftime("%c")
        return convert_time(t_left), f_time
