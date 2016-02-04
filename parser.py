import bs4

import errors
import premka


class Parser:
    NO_MONEY = u'Niestety nie masz już punktów na swoim koncie'
    BAD_KEY = u'Niestety nie ma takiego kodu w bazie ani w serwisie dotpay.'
    DOWNLOAD = u'Pobierz'
    DELETE = u'Usuń'
    GOD = 'Poprawnie wygenerowane linki'

    @classmethod
    def download_links(cls, html):
        links = cls.links(html)
        return [x.attrs['href'] for x in links if cls.DOWNLOAD in x.text]

    @classmethod
    def delete_links(cls, html):
        links = cls.links(html)
        return [x.attrs['href'] for x in links if cls.DELETE in x.text]

    @classmethod
    def check_response(cls, html):
        if Parser.NO_MONEY in html.text:
            raise errors.NoMoneyError
        if Parser.BAD_KEY in html.text:
            raise errors.BadKeyError
        if html.url == premka.Premka.ADD_FILES_URL and Parser.GOD not in html.text:
            raise errors.NoMoneyError

    @classmethod
    def links(cls, html):
        bs = bs4.BeautifulSoup(html, "html.parser")
        table = bs.find('table')
        links = table.findAll('a')
        return links