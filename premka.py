# -*- coding: utf-8 -*-

from optparse import OptionParser
from itertools import chain, islice

import requests

import parser
import tasks


class Premka:
    ADD_FILES_URL = 'http://www.premka.net/index.php/generuj/rezultat'
    GET_FILES_URL = 'http://www.premka.net/index.php/linki'

    def __init__(self, key):
        self.key = key
        self.parser = parser.Parser

    def add_files(self, files_url):
        files = '\n'.join(files_url)
        data = {'kod': self.key,
                'linki': files,
                'wyslano': 1}
        response = requests.post(self.ADD_FILES_URL, data=data)
        response = self.__set_encoding(response)
        self.parser.check_response(response)
        return response

    def delete_files(self, links):
        for link in links:
            response = requests.get(link)


    def get_downloads_links(self):
        response = self.__download()
        links = self.parser.download_links(response.text)
        return links

    def get_delete_links(self):
        response = self.__download()
        links = self.parser.delete_links(response.text)
        return links

    def __download(self):
        data = {'kod': self.key,
                'wyslano': 1}
        response = requests.post(self.GET_FILES_URL, data=data)
        response = self.__set_encoding(response)
        self.parser.check_response(response)
        return response

    @staticmethod
    def __set_encoding(response, encoding='UTF-8'):
        response.encoding = encoding
        return response


def chunks(n, iterable):
   iterable = iter(iterable)
   while True:
       yield chain([next(iterable)], islice(iterable, n-1))


def option():
    usage = "usage: %prog [options] arg"
    parser = OptionParser(usage)

    parser.add_option("-f", "--file", dest="filename", help="file with download links")
    parser.add_option("-t", "--thread", dest="thread_number", help="How much files download in one time",  default=2)
    parser.add_option("-k", "--key", dest="key", help="Key for premka")
    parser.add_option("-d", "--no-delete", action="store_false", dest="no_delete", help="Dont delete exists links on premka", default=True)
    (options, args) = parser.parse_args()
    if not options.filename:
        parser.error('File name option is required')
    if not options.key:
        parser.error('Premka key is required')
    return options


if __name__ == '__main__':
    options = option()

    pre = Premka(options.key)

    if options.no_delete:
        print("Delete existing links ...")
        delete_links = pre.get_delete_links()
        pre.delete_files(delete_links)

    links = [line.strip() for line in open(options.filename, 'r')]
    print("Add files to permka")
    actual = 0
    total = len(links)
    for split_link in chunks(5, links):
        split_link = list(split_link)
        actual += len(split_link)
        print("{0}/{1}".format(actual, total))
        pre.add_files(list(split_link))
    print(pre.get_downloads_links())
    tasks.download_files(pre.get_downloads_links(), int(options.thread_number))

