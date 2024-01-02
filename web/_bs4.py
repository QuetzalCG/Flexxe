from typing import Iterator, Mapping
from bs4 import BeautifulSoup, Tag as bs4_Tag # type: ignore
from cached_property import cached_property # type: ignore
from ._common import BaseWebPage, BaseTag

class Tag(BaseTag):
    def __init__(self, name: str, attributes: Mapping[str, str], soup: bs4_Tag) -> None:
        super().__init__(name, attributes)
        self._soup = soup
    


    @cached_property
    def inner_html(self) -> str:
        return self._soup.decode_contents()





class WebPage(BaseWebPage):
    def _parse_html(self):
        """
        Parse the HTML with BeautifulSoup to find <script> and <meta> tags.
        """
        self._parsed_html = soup = BeautifulSoup(self.html, 'lxml')
        self.scripts.extend(script['src'] for script in soup.findAll('script', src=True))
        self.meta = {meta['name'].lower(): meta['content'] for meta in soup.findAll('meta', attrs=dict(name=True, content=True))}
    

    
    def select(self, selector: str) -> Iterator[Tag]:
        """Execute a CSS select and returns results as Tag objects."""
        for item in self._parsed_html.select(selector):
            yield Tag(item.name, item.attrs, item)