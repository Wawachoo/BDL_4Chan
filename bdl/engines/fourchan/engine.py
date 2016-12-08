import os
import urllib
import requests
import re
from lxml import etree as etree
from bdl.item import Item
from bdl.exceptions import *
import bdl.downloaders
import bdl.engine


class Engine(bdl.engine.Engine):

    # =========================================================================
    # BDL ENGINE API
    # =========================================================================

    @staticmethod
    def get_repo_name(url, **kwargs):
        paths = urllib.parse.urlparse(url).path[1:].split('/')
        name = len(paths) > 3 and paths[3] or None
        # 1 - Try to get the name from the URL.
        if name is not None:
            return name
        # 2 - Try to get the name from the repository source.
        rep = requests.get(url)
        if not rep.ok:
            raise EngineNetworkError(__name__, "{}".format(rep.reason))
        tree = etree.fromstring(rep.text, etree.HTMLParser())
        # 2.1 - Try to get the name from the <subject> element.
        node_subject = tree.find((".//*[@id='pi{}']/span[1]")
                                 .format(paths[2]))
        if node_subject is not None and node_subject.text is not None:
            return node_subject.text
        # 2.2 - Try to get the name from the title element.
        # The <title> format looks like "/SECTION/ - NAME - ... - 4chan"
        node_title = tree.find("./head/title")
        if node_title is not None:
            return node_title.text.split('-')[1].rstrip().lstrip()
        return None

    @staticmethod
    def is_reachable(url, **kwargs):
        return requests.head(url).ok

    def __init__(self, url, config, progress):
        super().__init__(url, config, progress)

    def pre_connect(self, **kwargs):
        paths = urllib.parse.urlparse(self.url).path[1:].split('/')
        self.config["section"] = paths[0]
        self.config["identifier"] = paths[2]
        self.config["name"] = self.get_repo_name(self.url, **kwargs)

    def pre_update(self, **kwargs):
        pass

    def count_all(self, **kwargs):
        return len(self.list_files(self.url))

    def count_new(self, last_item, last_position, **kwargs):
        return len(self.list_files(self.url)[last_position:])

    def update_all(self, **kwargs):
        for item in self.update_new(None, 0, **kwargs):
            self.set_item_metadata(item)
            yield item

    def update_new(self, last_item, last_position, **kwargs):
        urls = self.list_files(self.url)[last_position:]
        self.progress.remains = len(urls)
        if len(urls) > 0:
            for item in bdl.downloaders.generic(urls, progress=self.progress):
                self.set_item_metadata(item)
                yield item

    def update_selection(self, urls, **kwargs):
        self.progress.remains = len(urls)
        for item in bdl.downloaders.generic(urls, progress=self.progress):
            self.set_item_metadata(item)
            yield item

    # =========================================================================
    # ENGINE-SPECIFIC
    # =========================================================================

    def set_item_metadata(self, item):
        """Set an item's metadata.
        """
        item.set_metadata({"thread_section": self.config["section"],
                           "thread_name": self.config["name"],
                           "thread_id": self.config["identifier"]})

    def list_files(self, url):
        """Returns the files URL.
        """
        rep = requests.get(url)
        if not rep.ok:
            raise EngineNetworkError(
                self.name, "{}: {}".format(rep.status_code, rep.reason))
        tree = etree.fromstring(rep.text, etree.HTMLParser())
        return [("http:" + elem.attrib["href"])
                for elem
                in tree.findall(".//*[@class='fileText']/a")]
