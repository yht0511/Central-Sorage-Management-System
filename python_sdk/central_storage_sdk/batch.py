"""
Batch operations for the Central Storage System SDK
"""

from typing import List, Dict, Any, Optional, Callable
from .client import CentralStorageClient
from .models import Laboratory, Storage, Section, Item, PaginationParams
from .utils import (
    generate_test_laboratories,
    generate_test_storages, 
    generate_test_sections,
    generate_test_items,
    batch_create_with_progress
)


class BatchOperations:
    """Batch operations for efficient data management"""
    
    def __init__(self, client: CentralStorageClient):
        self.client = client
    
    def create_laboratories_batch(self, lab_data_list: List[Dict[str, Any]]) -> List[Laboratory]:
        """Batch create laboratories"""
        return batch_create_with_progress(
            self.client,
            self.client.create_laboratory,
            lab_data_list,
            "Creating laboratories"
        )
    
    def create_storages_batch(self, storage_data_list: List[Dict[str, Any]]) -> List[Storage]:
        """Batch create storage devices"""
        return batch_create_with_progress(
            self.client,
            self.client.create_storage,
            storage_data_list,
            "Creating storage devices"
        )
    
    def create_sections_batch(self, section_data_list: List[Dict[str, Any]]) -> List[Section]:
        """Batch create sections"""
        return batch_create_with_progress(
            self.client,
            self.client.create_section,
            section_data_list,
            "Creating sections"
        )
    
    def create_items_batch(self, item_data_list: List[Dict[str, Any]]) -> List[Item]:
        """Batch create items"""
        return batch_create_with_progress(
            self.client,
            self.client.create_item,
            item_data_list,
            "Creating items"
        )
    
    def setup_test_environment(self, 
                             lab_count: int = 5,
                             storage_per_lab: int = 3,
                             section_per_storage: int = 5,
                             item_per_section: int = 3) -> Dict[str, List]:
        """Set up a complete test environment"""
        print("Setting up test environment...")
        
        # Create laboratories
        print(f"\n1. Creating {lab_count} laboratories...")
        lab_data = generate_test_laboratories(lab_count)
        laboratories = self.create_laboratories_batch(lab_data)
        lab_ids = [lab.id for lab in laboratories if lab.id]
        
        # Create storage devices
        print(f"\n2. Creating {len(lab_ids) * storage_per_lab} storage devices...")
        storage_data = generate_test_storages(lab_ids, storage_per_lab)
        storages = self.create_storages_batch(storage_data)
        storage_ids = [storage.id for storage in storages if storage.id]
        
        # Create sections
        print(f"\n3. Creating {len(storage_ids) * section_per_storage} sections...")
        section_data = generate_test_sections(storage_ids, section_per_storage)
        sections = self.create_sections_batch(section_data)
        section_ids = [section.id for section in sections if section.id]
        
        # Create items
        print(f"\n4. Creating {len(section_ids) * item_per_section} items...")
        item_data = generate_test_items(section_ids, item_per_section)
        items = self.create_items_batch(item_data)
        
        print("\n✅ Test environment setup complete!")
        print(f"Created: {len(laboratories)} labs, {len(storages)} storages, {len(sections)} sections, {len(items)} items")
        
        return {
            "laboratories": laboratories,
            "storages": storages,
            "sections": sections,
            "items": items
        }
    
    def delete_all_data(self, confirm: bool = False) -> bool:
        """Delete all data (USE WITH CAUTION!)"""
        if not confirm:
            print("This will delete ALL data! Call with confirm=True to proceed.")
            return False
        
        print("Deleting all data...")
        
        try:
            # Delete items first (foreign key constraints)
            print("Deleting items...")
            items = self.client.get_items(PaginationParams(page_size=100))
            for item in items.data:
                if item.id:
                    self.client.delete_item(item.id)
            
            # Delete sections
            print("Deleting sections...")
            sections = self.client.get_sections(PaginationParams(page_size=100))
            for section in sections.data:
                if section.id:
                    self.client.delete_section(section.id)
            
            # Delete storages
            print("Deleting storages...")
            storages = self.client.get_storages(PaginationParams(page_size=100))
            for storage in storages.data:
                if storage.id:
                    self.client.delete_storage(storage.id)
            
            # Delete laboratories
            print("Deleting laboratories...")
            labs = self.client.get_laboratories(PaginationParams(page_size=100))
            for lab in labs.data:
                if lab.id:
                    self.client.delete_laboratory(lab.id)
            
            print("All data deleted successfully!")
            return True
            
        except Exception as e:
            print(f"Error during deletion: {e}")
            return False
    
    def create_sections_for_storage(self, storage_id: int, count: int = 10) -> List[Section]:
        """Create multiple sections for a specific storage device"""
        section_data = generate_test_sections([storage_id], count)
        return self.create_sections_batch(section_data)
    
    def create_items_for_section(self, section_id: int, count: int = 10) -> List[Item]:
        """Create multiple items for a specific section"""
        item_data = generate_test_items([section_id], count)
        return self.create_items_batch(item_data)
    
    def get_full_inventory(self) -> Dict[str, Any]:
        """Get complete inventory overview"""
        print("Retrieving full inventory...")
        
        # Get all data
        labs = self.client.get_laboratories(PaginationParams(page_size=100))
        storages = self.client.get_storages(PaginationParams(page_size=100))
        sections = self.client.get_sections(PaginationParams(page_size=100))
        items = self.client.get_items(PaginationParams(page_size=100))
        
        inventory = {
            "laboratories": {
                "count": labs.total,
                "data": labs.data
            },
            "storages": {
                "count": storages.total,
                "data": storages.data
            },
            "sections": {
                "count": sections.total,
                "data": sections.data
            },
            "items": {
                "count": items.total,
                "data": items.data
            }
        }
        
        print(f"Inventory: {labs.total} labs, {storages.total} storages, {sections.total} sections, {items.total} items")
        return inventory
    
    def migrate_sections_to_storage(self, section_ids: List[int], target_storage_id: int) -> List[Section]:
        """Migrate sections to a different storage device"""
        migrated_sections = []
        
        for section_id in section_ids:
            try:
                section = self.client.get_section(section_id)
                updated_section = self.client.update_section(section_id, {"storage_id": target_storage_id})
                migrated_sections.append(updated_section)
                print(f"Migrated section {section.name} to storage {target_storage_id}")
            except Exception as e:
                print(f"Failed to migrate section {section_id}: {e}")
        
        return migrated_sections
    
    def bulk_update_item_quantities(self, item_updates: List[Dict[str, int]]) -> List[Item]:
        """Bulk update item quantities
        
        Args:
            item_updates: List of {"item_id": int, "quantity": int}
        """
        updated_items = []
        
        for update in item_updates:
            try:
                item = self.client.update_item_quantity(update["item_id"], update["quantity"])
                updated_items.append(item)
                print(f"Updated item {item.name} quantity to {update['quantity']}")
            except Exception as e:
                print(f"Failed to update item {update['item_id']}: {e}")
        
        return updated_items
