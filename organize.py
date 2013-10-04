#!/usr/bin/env python

import re

from shutil import move
from os import listdir, chdir, mkdir
from os.path import abspath, dirname, isdir, isfile, join, exists

PATH = abspath(dirname(__file__))
TV_PATH = "/media/My Passport/TV Shows"
MOVIE_PATH = "/media/My Passport/Movies"

recs = listdir(PATH)
tv_show_folders = listdir(TV_PATH)


class NewFile(object):

    def __init__(self, name):

        self.name = name
        self.get_tokens()
        self.show_or_movie()

    def get_tokens(self, limit=2, look_at='name'):

        self.tokens = []
        tokens = [[]]

        for char in getattr(self, look_at).lower().strip():
            print char

            if char.isalpha():
                tokens[-1].append(char)
            elif tokens[-1]:
                tokens.append([])

        for token in tokens:
            token = ''.join(token)

            if len(token) > limit and token not in ('lol', 'hdtv', 'asap'):
                self.tokens.append(token)


    def show_or_movie(self):

        # Look for the standard S03E08 sort of format shows download in.
        tv_show = re.search(r'\w\d\d\w\d\d', self.name)

        if tv_show:
            match = tv_show.group()
            self.tv_show = True
            self.season = match[1:3].strip("0")
            self.episode = match[-2:].strip("0")
            self.match = match
        else:
            self.movie = True

    def get_best_match(self):
        best_match = None
        most_tokens = 0

        for folder in tv_show_folders:
            folder_tokens = folder.lower().split(' ')

            common_tokens = len(
                set(self.tokens).intersection(set(folder_tokens))
            )

            if common_tokens > most_tokens:
                most_tokens = common_tokens
                best_match = folder
                self.tv_show_name = folder

        if not best_match:
            name = self.name
            self.cut_name = name[:name.index(self.match)-1]
            self.get_tokens(limit=0, look_at='cut_name')
            self.tv_show_name = ' '.join(self.tokens).title()

        self.place_in_folder()


    def place_in_folder(self):
       if self.tv_show:
           new_path = "{0}/Season {1}".format(self.tv_show_name, self.season)
           tv_show_path = join(TV_PATH, self.tv_show_name)
           season_path = join(TV_PATH, new_path)

           if not exists(tv_show_path):
               mkdir(tv_show_path)

           if not exists(season_path):
               mkdir(season_path)


           move(self.name, season_path)

       elif self.movie:
           move(self.name, MOVIE_PATH)


ignore_files = ('.py', '.pyc', '.swp', '.swn', '.swo', '.part', '.nfo')

def process_files(recs):
    for rec in recs:

        if isdir(rec):
            continue
            rec_files = listdir(rec)
            process_files(rec_files)

        elif isfile(rec):

            if rec.lower().endswith(ignore_files):
                continue

            download = NewFile(rec)


        # See if it is a TV show
        if download.tv_show:
            best_folder = download.get_best_match()



process_files(recs)
