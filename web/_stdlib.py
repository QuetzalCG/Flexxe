from typing import Iterable, Mapping, Optional
from html.parser import HTMLParser
from xml.dom import minidom
from cached_property import cached_property # type: ignore
from ._common import BaseWebPage, BaseTag
from dom_query import select_all # type: ignore



class Tag(BaseTag):

    def __init__(self, name: str, attributes: Mapping[str, str], elem: minidom.Element) -> None:
        super().__init__(name, attributes)
        self._elem = elem
    


    @cached_property
    def inner_html(self) -> str:
        return ''.join(d.toxml() for d in self._elem.childNodes)





class ScriptMetaParser(HTMLParser):

    def __init__(self):
        super().__init__()
        self.script_src = []
        self.meta_info = {}



    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == 'script':
            if attributes.get('src'):
                self.script_src.append(attributes.get('src'))
        if tag == 'meta':
            if attributes.get('name'):
                self.meta_info.update({attributes.get('name').lower(): attributes.get('content')})

class WebPage(BaseWebPage):
    def _parseBody(self):
        """
        Parse the HTML with HTMLParser to find <script> and <meta> tags.
        """
        script_meta_parser = ScriptMetaParser()
        script_meta_parser.feed(self.html)
        self.scripts.extend(script_meta_parser.script_src)
        self.meta = script_meta_parser.meta_info
    


    @cached_property
    def _dom(self) -> Optional[minidom.Document]:
        try:
            dom = minidom.parseString(self.html)
        except Exception as e:
            dom = None
        return dom



    def select(self, selector: str) -> Iterable[Tag]:
        """Execute a CSS select and returns results as Tag objects."""
        dom = self._dom
        if not dom:
            return ()
        for item in select_all(dom, selector):
            yield Tag(item.tagName, dict(item._get_attributes().items()), item)