from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any

@dataclass
class Item:
    id: str
    date: str
    item_name: str
    description: str
    search_keywords: str
    list_price: str
    draft_price: str
    mercari_url: str
    amazon_url: str
    yodobashi_url: str
    draft_title: str
    draft_description: str
    image_path: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Item':
        return cls(
            id=data.get('id', ''),
            date=data.get('date', ''),
            item_name=data.get('item_name', ''),
            description=data.get('description', ''),
            search_keywords=data.get('search_keywords', ''),
            list_price=data.get('list_price', ''),
            draft_price=data.get('draft_price', ''),
            mercari_url=data.get('mercari_url', ''),
            amazon_url=data.get('amazon_url', ''),
            yodobashi_url=data.get('yodobashi_url', ''),
            draft_title=data.get('draft_title', ''),
            draft_description=data.get('draft_description', ''),
            image_path=data.get('image_path', '')
        )
