import moviepy.editor as mp
import imageio
from os import listdir
from os.path import isfile, join
from functions import calc_time

video_path = "sample.MKV"
# video = mp.VideoFileClip(video_path)
directory = "E:\Gospel videos\Videos"
acceptable_file_types = ["MP4", "MOV", "WMV", "AVI", "FLV", "MKV", "WEBM"]


@calc_time
def rename_files(directory):
    directory_list = listdir(directory)#todo add option to select new save directory,default to current directory
    x = [join(directory, f) for f in directory_list if
         isfile(join(directory, f)) and f.split(".")[-1].upper() in acceptable_file_types
         ]

def convert_file(video_path):
    a = (lambda n: f'{"".join(n.split(".")[:-1])}.mp3')(video_path)
    print(a)
    # video = mp.VideoFileClip(video_path)
    # video.audio.write_audiofile(audio_name(video_path))
    # print(audio_name)


rename_files(directory)
convert_file(video_path)
# x = video.subclip(0, 7)
# x.ipython_display()
# myclip2 = video.subclip(10, 25)
# myclip2.write_gif("test.gif")
# audio = video.audio
# video.close()
