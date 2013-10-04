#!/usr/bin/env python

"""
Organize movies and folders by putting them in the right folder

Torrents get downloaded into one folder. If a file has a naming pattern
which includes something along the lines of "S3E11" then we declare it
as a TV show. If it does not, it is a movie. Based upon the rest of the filname
we figure out which subdirectory it belongs in while creating folders
along the way if they don't exist
"""

import re

from shutil import move
from os import listdir, mkdir
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
        """
        The limit is the max amount of characters allowed for it to be
        allowed as a token. Only if we can't find a TV show directory do we
        set the limit to 0 just so we can figure out what to name the folder
        """

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
        """
        Check if file is a movie or TV show
        """

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
        """
        Only for TV shows. Break file into tokens and then see which TV show
        folder has the highest matches of tokens to figure out which show
        the file is associated with. If no match found, create the folders
        """

        best_match = None
        most_tokens = 0

        for folder in tv_show_folders:
            folder_tokens = folder.lower().split(' ')

            # Get the count of common tokens and words within folders.
            common_tokens = len(
                set(self.tokens).intersection(set(folder_tokens))
            )

            if common_tokens > most_tokens:
                most_tokens = common_tokens
                best_match = folder
                self.tv_show_name = folder

        # There was no folder found. Only get the filename up to where the
        # season and epsisode declaration is and assign it as self.cut_name.
        # cut_name is what we then use to re-tokenize and name a show folder.
        if not best_match:
            name = self.name
            self.cut_name = name[:name.index(self.match)-1]
            self.get_tokens(limit=0, look_at='cut_name')
            self.tv_show_name = ' '.join(self.tokens).title()

        self.place_in_folder()

    def place_in_folder(self):
        """
        Move file from the downloads directory to it appropriete folder
        """

        if self.tv_show:
            new_path = "{0}/Season {1}".format(self.tv_show_name, self.season)
            tv_show_path = join(TV_PATH, self.tv_show_name)
            season_path = join(TV_PATH, new_path)

            # Create new folder if the TV shows folder name does not exist.
            if not exists(tv_show_path):
                mkdir(tv_show_path)

            # Create season folder within shows folder if it does not exist.
            if not exists(season_path):
                mkdir(season_path)

            # Move the TV show file
            move(self.name, season_path)

        elif self.movie:
            # Move file into movies directory...that was a lot easier.
            move(self.name, MOVIE_PATH)


# Don't bother looking at files in the directory that end in these extensions.
ignore_files = ('.py', '.pyc', '.swp', '.swn', '.swo', '.part', '.nfo')


def process_files(recs):
    """
    Go through each file in the downloads directory.
    """

    for rec in recs:

        # Not yet ready to handle directories...maybe. Not tested.
        if isdir(rec):
            continue
            rec_files = listdir(rec)
            process_files(rec_files)

        elif isfile(rec):

            if rec.lower().endswith(ignore_files):
                continue

            download = NewFile(rec)

        # See if it is a TV show or movie to determine what to do next.
        if download.tv_show:
            download.get_best_match()
        elif download.movie:
            download.place_in_folder()


process_files(recs)
