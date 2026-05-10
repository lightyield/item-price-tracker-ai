import json
import os
import uuid
from datetime import datetime
from PIL import Image
from typing import List, Optional
from models.item import Item

class InventoryManager:
    def __init__(self, data_file="data/inventory.json", image_dir="data/images"):
        self.data_file = data_file
        self.image_dir = image_dir
        self._ensure_directories()

    def _ensure_directories(self):
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        os.makedirs(self.image_dir, exist_ok=True)
        if not os.path.exists(self.data_file):
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump([], f)

    def load_items(self) -> List[Item]:
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [Item.from_dict(item_dict) for item_dict in data]
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_item(self, item_data: dict, pil_image: Optional[Image.Image] = None) -> str:
        items = self.load_items()
        
        item_id = str(uuid.uuid4())
        image_path = ""
        
        if pil_image:
            image_filename = f"{item_id}.png"
            image_path = os.path.join(self.image_dir, image_filename)
            pil_image.save(image_path, "PNG")

        new_item = Item(
            id=item_id,
            date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            item_name=item_data.get("item_name", ""),
            description=item_data.get("description", ""),
            search_keywords=item_data.get("search_keywords", ""),
            list_price=item_data.get("list_price", ""),
            draft_price=item_data.get("draft_price", ""),
            mercari_url=item_data.get("mercari_url", ""),
            amazon_url=item_data.get("amazon_url", ""),
            yodobashi_url=item_data.get("yodobashi_url", ""),
            draft_title=item_data.get("draft_title", ""),
            draft_description=item_data.get("draft_description", ""),
            image_path=image_path
        )
        
        items.insert(0, new_item)  # 最新を先頭に
        self._save_all(items)
        
        return item_id

    def update_item(self, item_id: str, updated_data: dict) -> bool:
        items = self.load_items()
        for i, item in enumerate(items):
            if item.id == item_id:
                # 既存のデータを更新
                item_dict = item.to_dict()
                item_dict.update(updated_data)
                items[i] = Item.from_dict(item_dict)
                self._save_all(items)
                return True
        return False

    def delete_item(self, item_id: str) -> bool:
        items = self.load_items()
        item_to_delete = next((item for item in items if item.id == item_id), None)
        
        if item_to_delete:
            # 画像も削除
            if item_to_delete.image_path and os.path.exists(item_to_delete.image_path):
                os.remove(item_to_delete.image_path)
            
            items = [item for item in items if item.id != item_id]
            self._save_all(items)
            return True
        return False

    def _save_all(self, items: List[Item]):
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump([item.to_dict() for item in items], f, ensure_ascii=False, indent=2)
