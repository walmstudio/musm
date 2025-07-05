import mpv
import os
from customtkinter import *
import xdialog
import filebase
from PIL.ImageTk import PhotoImage
from PIL import Image
import io
from base64 import b64decode
import musinfo
import sys

FontManager.init_font_manager()
FontManager.load_font('lucon.ttf')

des = CTk()
des.geometry('500x645')
des.title('WALM MUSM')
des.resizable(width=False,height=False)

player = mpv.MPV()

progress_duration = 0
com_manager = ''
isec = 0

repeat_mode = False
mus_repeat_path = ''
mus_button_list = []
mus_button_list.append('placeba')
mus_list = 0
mus_numbers = 0
redux = False

def hidehead():
    header.place_forget()
    close_header.place_forget()
    main.place(x=10, y=15)
    music_playlist.place(x=10, y=340)
    music_playlist.configure(height=270)

def volume_regular(value):
    player.volume = value
    volumer.configure(text=f'{int(player.volume)}')

def nexttrack():
    global mus_numbers

    if mus_numbers == mus_list:
        mus_button_list[mus_numbers]()
    else:
        mus_numbers +=1
        mus_button_list[mus_numbers]()

def fasttrack():
    global mus_numbers

    if mus_numbers == 0:
        mus_numbers = 1
    else:
        pass

    try:
        mus_button_list[mus_numbers]()
    except:
        pass

def backtrack():
    global mus_numbers

    if mus_numbers == 1:
        mus_button_list[mus_numbers]()
    elif mus_numbers == 0:
        pass
    elif mus_numbers > 1:
        mus_numbers -=1
        mus_button_list[mus_numbers]()

def repeat_manager():
    global repeat_mode

    if repeat_mode == False:
        repeat.configure(fg_color='grey', hover_color='grey', text='repeat ON')
        repeat_mode = True
    elif repeat_mode == True:
        repeat.configure(text='repeat list')
        repeat_mode = 'list'
    elif repeat_mode == 'list':
        repeat.configure(fg_color='#1c1c1c', text='repeat', hover_color='#2e2e2e')
        repeat_mode = False

def mus_position(value):
    player.time_pos = value

def play_manager():
    global com_manager, progress_duration, isec, progress_step
    if play._text == 'play':
        fasttrack()
    elif play._text == 'pause':
        com_manager = 'pause'
        player.pause = True
        play.configure(text='unpause')
    elif play._text == 'unpause':
        player.pause = False
        com_manager == 'playing'
        play.configure(text='pause')

def seek_duration(mus_duration):
    global isec, redux

    isec = mus_duration

    if redux == False:
        redux = True
        des.update()
        des.after(200,lambda: seek_duration(isec))

    try:
        if play._text == 'pause':
            if int(player.time_pos) == int(mus_duration) or player.time_pos == None:
                if repeat_mode == False:
                    play.configure(text='play')
                    music_progress.configure(state='disabled')
                    music_progress.set(0)
                    timing.place_forget()
                    des.update()
                elif repeat_mode == True:
                    player.play(mus_repeat_path)
                    des.update()
                    des.after(200,lambda: seek_duration(isec))
                elif repeat_mode == 'list':
                    nexttrack()
            else:
                try:
                    timing.place(x=60,y=172)
                    timing.configure(text=f'{musinfo.format_duration(player.time_pos)} - {musinfo.format_duration(isec)}')
                    music_progress.set(player.time_pos)
                except:
                    pass
                des.update()
                des.after(200,lambda: seek_duration(isec))
        else:
            des.update()
            des.after(200,lambda: seek_duration(isec)) 
    except:
        des.update()
        des.after(200,lambda: seek_duration(isec)) 

def play_file(mus_name, mus_artist, mus_album, mus_path, mus_image, final_duration):
    global com_manager, isec, mus_repeat_path, mus_numbers, redux

    if mus_image == None:
        music_preview_label.place_forget()
    else:
        img_decode = musinfo.process_base64_image(mus_image, (150,150),output_format='PNG')
        img_data = b64decode(img_decode[0])
        img = Image.open(io.BytesIO(img_data))
        music_preview_label.configure(image=PhotoImage(img))
        if img_decode[1] == True:
            music_preview_label.place(x=0,y=35)
        elif img_decode[1] == False:
            music_preview_label.place(x=0,y=0)

    final_name_mus = ''
    final_name_mus += f'{mus_path}'
    if mus_artist == None:
        pass
    else:
        final_name_mus += f'\n{mus_artist}'
    if mus_album == None:
        pass
    else:
        final_name_mus += f'\n{mus_album}'  
    name_music_label.configure(text=final_name_mus)

    print(f'Track {mus_name}: {mus_path}')

    for i in range(2):
        mus_repeat_path = mus_path
        player.play(mus_path)
        com_manager = 'playing'
        progress_var.set(final_duration)
        music_progress.configure(to=progress_var.get(), state='normal')
        des.after(1000,lambda: seek_duration(final_duration))
        name_music_label.place(x=1,y=1)
        player.pause = False
        redux = False
        play.configure(text='pause')

def add_music(mus_path):
    global mus_list, mus_button_list, mus_numbers
    try:
        #player.play(mus_path)
        #player.stop()

        music_info = []

        mus_numbers = 1

        metadata, cover = player_medatata.get_metadata(mus_path)

        music_info.append(mus_path)

        for key, value in metadata.items():
            if value == 'Unknown':
                music_info.append(None)
            else:
                if key.capitalize() == 'Duration':
                    final_duration = value
                    music_info.append(f"{key.capitalize()}: {int(value)}")
                else:
                    music_info.append(f"{key.capitalize()}: {value}")
            print(music_info)

        music_info.append(musinfo.get_cover_base64(mus_path))

        mus_list += 1

        play_button = CTkButton(music_playlist, text=f'{os.path.basename(mus_path)}', font=('Lucida Console', 16), width=450, border_width=1, fg_color='#1c1c1c', hover_color='#2e2e2e', border_color='white', command=lambda: play_file(mus_name=mus_list,mus_artist=music_info[2],mus_album=music_info[3], mus_path=music_info[0], mus_image=music_info[5], final_duration=final_duration))
        play_button.pack(pady=2)

        mus_button_list.append(lambda: play_file(mus_name=mus_list,mus_artist=music_info[2],mus_album=music_info[3], mus_path=music_info[0], mus_image=music_info[5], final_duration=final_duration))
    except:
        return False
    
    music_progress.set(0)
    timing.place_forget()
    play.configure(text='play')

def open_music_file():
    global isec
    file = xdialog.open_file('Change music file', [("mp3", "*.mp3"),
                                                   ("ogg", "*.ogg"),
                                                   ("wav", "*.wav"),
                                                   ("m4a", "*.m4a"),
                                                   ("flac", "*.flac")])

    if file == "":
        return False
    else:
        add_music(file)

    player.stop()
    music_progress.configure(state='disabled')
    music_progress.set(0)
    music_preview_label.place_forget()
    name_music_label.place_forget()

def open_music_folder():
    global isec
    file = xdialog.directory('Set music directory')

    if file == "":
        return False
    else:
        true_format = [".mp3", ".ogg", ".wav",".m4a", ".flac"]
        for i in os.listdir(file):
            if os.path.splitext(i)[1] in true_format:
                add_music(f'{file}/{i}')

    player.stop()
    music_progress.configure(state='disabled')
    music_progress.set(0)
    music_preview_label.place_forget()
    name_music_label.place_forget()
        
#----------------------------------------------
#root frame
background_image = PhotoImage(data=b64decode(filebase.background))
CTkLabel(des, image=background_image, text='').place(x=0,y=0)
header = CTkLabel(des, text='   MUSM\n    Music from MPV', font=('Lucida Console', 40), bg_color='black')
header.place(x=-15, y=15)
#----------------------------------------------


#----------------------------------------------
#main frame
main = CTkFrame(des, width=480, height=320, bg_color='black', border_width=1, border_color='white')
#----------------------------------------------
music_preview = CTkFrame(main, width=150, height=150, border_width=1, border_color='white')
music_preview_label = CTkLabel(music_preview, text='')
music_preview.place(x=20,y=20)
#----------------------------------------------


#----------------------------------------------
name_music = CTkFrame(main, width=280, height=150, border_width=1, border_color='white')
name_music_label = CTkLabel(name_music, width=278, height=148, text='', font=('Lucida Console', 14), wraplength=275)
name_music_label.place(x=1,y=1)
name_music.place(x=180, y=20)
#----------------------------------------------

progress_var = IntVar(main, value=0)

open_file = CTkButton(main, text='open file', font=('Lucida Console', 16), border_width=1, fg_color='#1c1c1c', hover_color='#2e2e2e', border_color='white', command=open_music_file)
open_file.place(x=20, y=228)

open_folder = CTkButton(main, text='open folder', font=('Lucida Console', 16), border_width=1, fg_color='#1c1c1c', hover_color='#2e2e2e', border_color='white', command=open_music_folder)
open_folder.place(x=320, y=228)

music_progress = CTkSlider(main, width=440, border_width=1, height=10, button_color="white", button_hover_color='grey', border_color='white', state='disabled', progress_color='white', command=mus_position)
music_progress.place(x=20, y=200)

rewind_bottom = CTkButton(main, text='< back', font=('Lucida Console', 16), border_width=1, fg_color='#1c1c1c', hover_color='#2e2e2e', border_color='white', command=backtrack)
rewind_bottom.place(x=20, y=278)

play = CTkButton(main, text='play', font=('Lucida Console', 16), border_width=1, fg_color='#1c1c1c', hover_color='#2e2e2e', border_color='white', command=play_manager)
play.place(x=170, y=278)

repeat = CTkButton(main, text='repeat', font=('Lucida Console', 16), border_width=1, fg_color='#1c1c1c', text_color='white', hover_color='#2e2e2e', border_color='white', command=repeat_manager)
repeat.place(x=170, y=228)

rewind_up = CTkButton(main, text='next >', font=('Lucida Console', 16), border_width=1, fg_color='#1c1c1c', hover_color='#2e2e2e', border_color='white', command=nexttrack)
rewind_up.place(x=320, y=278)

timing = CTkLabel(main, text='--------------', font=('Lucida Console', 16))

volume_progress = CTkSlider(main, width=175, border_width=1, height=10, button_color="white", button_hover_color='grey', border_color='white', from_=0.0, to=200.0, progress_color='white', command=volume_regular)
volume_progress.place(x=235, y=180)
volume_progress.set(100)

volumer = CTkLabel(main, text=f'{int(player.volume)}', font=('Lucida Console', 14))
volumer.place(x=420,y=172)

main.place(x=10, y=100)
#----------------------------------------------

#----------------------------------------------
music_playlist = CTkScrollableFrame(des, width=458, border_width=1, border_color='white')
music_playlist.place(x=10, y=425)
#----------------------------------------------

player_medatata = musinfo.MPVMetadataExtractor()

close_header = CTkButton(des, text='hide', font=('Lucida Console', 16), width=50, border_width=1, fg_color='#1c1c1c', hover_color='#2e2e2e', border_color='white', command=hidehead)
close_header.place(x=425, y=62)

try:
    musarg = sys.argv[1]
    print(musarg)
    if os.path.isfile(musarg) == True:
        add_music(musarg)
        fasttrack()
    elif os.path.isdir(musarg) == True:
        true_format = [".mp3", ".ogg", ".wav",".m4a", ".flac"]
        for i in os.listdir(musarg):
            if os.path.splitext(i)[1] in true_format:
                add_music(f'{musarg}/{i}')
        fasttrack()
    else:
        pass
except:
    pass


icon = PhotoImage(data=b64decode(filebase.logo))
des.iconphoto(False, icon)

des.protocol('WM_DELETE_WINDOW', lambda: os._exit(2))

des.mainloop()