from __future__ import annotations
from typing import Callable
from anytree import NodeMixin
from typing import List


class CrumbNode(NodeMixin):
    
    def __init__(self, title:str, url:Callable, icon_class:str=None, html_classes:List[str]=None, parent:CrumbNode=None, siblings:List[CrumbNode]=None, is_active:bool=False) -> None:
        self.title = title
        self.url = url
        self.html_classes = html_classes if html_classes is not None else list()
        self.parent = parent
        self.icon_class = icon_class
        self.is_active = is_active
        self.siblings = siblings

    @property
    def icon_html(self) -> str:
        return f"<i class='{self.icon_class}'></i> " if self.icon_class is not None else ""

    @property
    def as_html(self) -> str:
        return f"<a href='{self.url}' class='{' '.join(self.html_classes)}'>{self.icon_html}{self.title}</a>"

    def __str__(self) -> str:
        return self.title