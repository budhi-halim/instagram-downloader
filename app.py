# Imports
import instaloader
import sys
import os
import json
import glob
import shutil
import piexif
from mutagen.mp4 import MP4
from pathlib import Path
from datetime import datetime

# Class
class File:
    def __init__(self, default_name, current_name, directory, file_type=None):
        self.default_name = default_name
        self.current_name = current_name
        self.directory = directory
        self.file_type = file_type
    
    @property
    def formatted_default_name(self):
        formatted = self.default_name.split('.')[0]
        formatted = formatted.replace('-', '').replace('_', '')
        return formatted
    
    @property
    def post_time(self):
        return self.formatted_default_name.split('UTC')[0]
    
    @property
    def post_order(self):
        order = self.formatted_default_name.split('UTC')[1]
        return '1' if order == '' or order == 'profilepic' else order
    
    def __eq__(self, other):
        return self.default_name == other.default_name if isinstance(other, File) else False
    
    def __lt__(self, other):
        return self.default_name < other.default_name if isinstance(other, File) else NotImplemented
    
    def __hash__(self):
        return hash(self.default_name)
    
    def __str__(self):
        return self.default_name

# Functions
def clear_screen():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def get_targets(file_name):
    with open(file_name, 'r') as file:
        return [(target.split(':')[0].strip(), target.split(':')[1].strip()) for target in file]

def download_profiles(username, tries=10):
    counter = 0
    while counter < tries:
        try:
            loader = instaloader.Instaloader()
            loader.login('silverwolf12345678', 'ZAY7pjnWhq')
            loader.download_profile(username)
        except:
            continue
        return True
    return False

def filter_files(folder_directory):
    unwanted_files = [file for file in glob.glob(os.path.join(folder_directory, '*')) if not (file.endswith('.jpg') or file.endswith('.mp4'))]
    for file in unwanted_files:
        os.remove(file)

def get_metadata(file_type, file_directory):
    if file_type == 'Photo':
        metadata = piexif.load(file_directory)['Exif'].get(37510)
        metadata = metadata.decode('utf-8', errors='ignore').replace('\x00', '')
        metadata = json.loads(metadata)
        return metadata
    
    if file_type == 'Video':
        metadata = MP4(file_directory).tags.get('\xa9cmt')[0]
        metadata = json.loads(metadata)
        return metadata

def set_metadata(file_object_list):
    for file_object in file_object_list:
        metadata = {
            'default_name': file_object.default_name,
            'current_name': file_object.current_name,
            'directory': file_object.directory,
            'file_type': file_object.file_type,
            'post_time': file_object.post_time,
            'post_order': file_object.post_order
        }

        if file_object.file_type == 'Photo':
            metadata = json.dumps(metadata).encode('utf-8')
            exif = piexif.load(file_object.directory)
            exif['Exif'][piexif.ExifIFD.UserComment] = metadata
            exif_bytes = piexif.dump(exif)
            piexif.insert(exif_bytes, file_object.directory)
    
        if file_object.file_type == 'Video':
            metadata = json.dumps(metadata)
            video = MP4(file_object.directory)
            video['\xa9cmt'] = metadata
            video.save()

def initialize_file_objects(folder_directory, mode=None):
    file_names = os.listdir(folder_directory)
    if mode == 'metadata':
        file_type = list(Path(folder_directory).parts)[1][:-1]
        files = []

        for file_name in file_names:
            file_directory = os.path.join(folder_directory, file_name)
            metadata = get_metadata(file_type, file_directory)
            default_file_name = metadata['default_name']
            current_file_name = metadata['current_name']
            file_object = File(default_file_name, current_file_name, file_directory, file_type)
            files.append(file_object)
        
        return files

    elif mode == 'split':
        photo = [File(file_name, file_name, os.path.join(folder_directory, file_name), 'Photo') for file_name in file_names if file_name.endswith('.jpg')]
        video = [File(file_name, file_name, os.path.join(folder_directory, file_name), 'Video') for file_name in file_names if file_name.endswith('.mp4')]
        return photo, video
    
    else:
        files = [File(file_name, file_name, os.path.join(folder_directory, file_name)) for file_name in file_names]
        return files

def merge_file_object_lists(list_1, list_2):
    merged = list(set(list_1) | set(list_2))
    merged.sort()
    return merged

def arrange_files(file_object_list):
    arranged_post = []
    current_post_time = None
    current_post_group = []

    for file in file_object_list:
        if current_post_time is None:
            current_post_time = file.post_time
            current_post_group.append(file)
        
        elif current_post_time == file.post_time:
            current_post_group.append(file)
        
        else:
            current_post_time = None
            current_post_group.reverse()
            arranged_post += current_post_group
            current_post_group = []

            current_post_time = file.post_time
            current_post_group.append(file)
    
    current_post_group.reverse()
    arranged_post += current_post_group
    arranged_post.reverse()

    return arranged_post

def organize(folder_directory, file_object_list):
    photo_directory = os.path.join(folder_directory, 'Photos')
    video_directory = os.path.join(folder_directory, 'Videos')

    os.makedirs(photo_directory, exist_ok=True)
    os.makedirs(video_directory, exist_ok=True)

    for file_name, file_object in zip(os.listdir(folder_directory), file_object_list):
        if file_name.endswith('.jpg'):
            old_file_directory = os.path.join(folder_directory, file_name)
            new_file_directory = os.path.join(photo_directory, file_name)
            os.rename(old_file_directory, new_file_directory)

            file_object.directory = new_file_directory
            file_object.file_type = 'Photo'
        
        if file_name.endswith('.mp4'):
            old_file_directory = os.path.join(folder_directory, file_name)
            new_file_directory = os.path.join(video_directory, file_name)
            os.rename(old_file_directory, new_file_directory)

            file_object.directory = new_file_directory
            file_object.file_type = 'Video'

def rename_files(arranged_photo_object_list, arranged_video_object_list, proper_name, parent_folder_directory):
    os.makedirs(os.path.join(parent_folder_directory, 'Photos'), exist_ok=True)
    os.makedirs(os.path.join(parent_folder_directory, 'Videos'), exist_ok=True)

    for file_type_folder in [enumerate(arranged_photo_object_list, start=1), enumerate(arranged_video_object_list, start=1)]:
        for index, file_object in file_type_folder:
            file_type = file_object.file_type
            file_extension = {'Photo': 'jpg', 'Video': 'mp4'}[file_type]
            file_name = f'{proper_name} {index}.{file_extension}'

            old_file_directory = file_object.directory
            new_file_directory = os.path.join(parent_folder_directory, f'{file_object.file_type}s', file_name)
            os.rename(old_file_directory, new_file_directory)
                
            file_object.current_name = file_name
            file_object.directory = os.path.join(proper_name, f'{file_object.file_type}s', file_name)

def process(username, proper_name):
    download_profiles(username)
    filter_files(username)

    if os.path.exists(proper_name) and os.path.isdir(proper_name):
        photo_object_list, video_object_list = initialize_file_objects(username, mode='split')
        existing_photo_object_list = initialize_file_objects(os.path.join(proper_name, 'Photos'), mode='metadata')
        existing_video_object_list = initialize_file_objects(os.path.join(proper_name, 'Videos'), mode='metadata')

        merged_photo_object_list = merge_file_object_lists(photo_object_list, existing_photo_object_list)
        merged_video_object_list = merge_file_object_lists(video_object_list, existing_video_object_list)

        arranged_photo_object_list = arrange_files(merged_photo_object_list)
        arranged_video_object_list = arrange_files(merged_video_object_list)

        rename_files(arranged_photo_object_list, arranged_video_object_list, proper_name, 'temp')

        shutil.rmtree(username)
        shutil.rmtree(proper_name)
        os.rename('temp', proper_name)

        set_metadata(arranged_photo_object_list)
        set_metadata(arranged_video_object_list)
        
    else:
        file_object_list = initialize_file_objects(username)
        organize(username, file_object_list)

        photo_object_list = [file_object for file_object in file_object_list if file_object.file_type == 'Photo']
        video_object_list = [file_object for file_object in file_object_list if file_object.file_type == 'Video']

        arranged_photo_object_list = arrange_files(photo_object_list)
        arranged_video_object_list = arrange_files(video_object_list)

        rename_files(arranged_photo_object_list, arranged_video_object_list, proper_name, proper_name)

        shutil.rmtree(username)

        set_metadata(arranged_photo_object_list)
        set_metadata(arranged_video_object_list)

def log(start_time, finish_time, source_file, log_file_name):
    time_format = r'%Y-%m-%d %H:%M:%S'
    start_formatted = start_time.strftime(time_format)
    finish_formatted = finish_time.strftime(time_format)
    
    duration = (finish_time - start_time)
    hours, remainder = divmod(duration.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    duration_formatted = f'{int(hours)}h {int(minutes)}m {int(seconds)}s'

    log_message = f'{start_formatted} Starting download for {source_file}\n{finish_formatted} Download completed ({duration_formatted})\n\n'

    with open(log_file_name, 'a') as log_file:
        log_file.write(log_message)

def main():
    start_time = datetime.now()

    source_file = sys.argv[1]
    targets = get_targets(source_file)

    for proper_name, username in targets:
        process(username, proper_name)
    
    finish_time = datetime.now()

    log(start_time, finish_time, source_file, 'log.txt')

if __name__ == '__main__':
    main()