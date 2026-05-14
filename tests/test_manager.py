import os
import json
import pytest
from src.database.manager import InventoryManager
from src.models.item import Item

@pytest.fixture
def temp_manager(tmp_path):
    data_file = tmp_path / "inventory.json"
    image_dir = tmp_path / "images"
    return InventoryManager(data_file=str(data_file), image_dir=str(image_dir))

def test_update_item(temp_manager):
    # 初期アイテムの保存
    item_data = {
        "item_name": "Test Item",
        "draft_title": "Old Title",
        "draft_description": "Old Description",
        "draft_price": "1000"
    }
    item_id = temp_manager.save_item(item_data)
    
    # 更新データの準備
    updated_data = {
        "draft_title": "New Title",
        "draft_price": "2000"
    }
    
    # 更新の実行
    success = temp_manager.update_item(item_id, updated_data)
    assert success is True
    
    # 更新内容の確認
    items = temp_manager.load_items()
    updated_item = next(item for item in items if item.id == item_id)
    assert updated_item.draft_title == "New Title"
    assert updated_item.draft_price == 2000
    assert updated_item.draft_description == "Old Description" # 更新していない箇所は維持される

def test_update_item_not_found(temp_manager):
    success = temp_manager.update_item("non-existent-id", {"draft_title": "New"})
    assert success is False
