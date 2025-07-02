#!/usr/bin/env python3
"""
Simple example script showing basic SDK usage
"""

import sys
from pathlib import Path

# Add the SDK to Python path
sdk_path = Path(__file__).parent / "central_storage_sdk"
sys.path.insert(0, str(sdk_path.parent))

from central_storage_sdk import CentralStorageClient
from central_storage_sdk.batch import BatchOperations
from central_storage_sdk.models import Laboratory, Storage, Section, Item


def main():
    # Initialize client
    client = CentralStorageClient("http://localhost:8080")
    
    # Login
    client.login("admin", "admin123")
    print("✅ Logged in successfully")
    
    # Create a laboratory
    lab = client.create_laboratory({
        "code": "DEMO001",
        "name": "Demo Laboratory",
        "location": "Building A, Room 101",
        "description": "Demonstration laboratory for SDK testing",
        "security_level": 2
    })
    print(f"✅ Created laboratory: {lab.name} (ID: {lab.id})")
    
    # Create a storage device
    storage = client.create_storage({
        "code": "STG001",
        "name": "Demo Storage Cabinet",
        "type": "试剂柜",
        "location": "Corner A1",
        "lab_id": lab.id,
        "capacity": 100,
        "security_level": 2,
        "properties": {
            "material": "Stainless Steel",
            "ventilation": "Yes",
            "lock_type": "Electronic"
        }
    })
    print(f"✅ Created storage: {storage.name} (ID: {storage.id})")
    
    # Create sections
    sections = []
    for i in range(3):
        section = client.create_section({
            "code": f"SEC{i+1:03d}",
            "name": f"Shelf {i+1}",
            "position": f"Row 1, Column {i+1}",
            "storage_id": storage.id,
            "capacity": 20,
            "properties": {
                "size": "Medium",
                "temperature_control": "Room Temperature"
            }
        })
        sections.append(section)
        print(f"✅ Created section: {section.name} (ID: {section.id})")
    
    # Create items
    items_data = [
        {
            "code": "ITEM001",
            "name": "Sodium Chloride",
            "category": "化学试剂",
            "quantity": 500,
            "unit": "g",
            "price": 25.50,
            "supplier": "Chemical Supply Co.",
            "section_id": sections[0].id,
            "properties": {
                "purity": "99.9%",
                "cas_number": "7647-14-5",
                "formula": "NaCl"
            }
        },
        {
            "code": "ITEM002", 
            "name": "Glass Beaker Set",
            "category": "实验器材",
            "quantity": 10,
            "unit": "套",
            "price": 45.00,
            "supplier": "Lab Equipment Ltd.",
            "section_id": sections[1].id,
            "properties": {
                "material": "Borosilicate Glass",
                "sizes": "50ml, 100ml, 250ml, 500ml"
            }
        }
    ]
    
    for item_data in items_data:
        item = client.create_item(item_data)
        print(f"✅ Created item: {item.name} (ID: {item.id}) - Qty: {item.quantity} {item.unit}")
    
    # Demonstrate batch operations
    print("\n🚚 Batch Operations Demo:")
    batch = BatchOperations(client)
    
    # Create multiple sections at once
    more_sections = batch.create_sections_for_storage(storage.id, count=5)
    print(f"✅ Batch created {len(more_sections)} additional sections")
    
    # Get inventory overview
    print("\n📊 Final Inventory Overview:")
    inventory = batch.get_full_inventory()
    print(f"Laboratories: {inventory['laboratories']['count']}")
    print(f"Storage Devices: {inventory['storages']['count']}")
    print(f"Sections: {inventory['sections']['count']}")
    print(f"Items: {inventory['items']['count']}")
    
    print("\n🎉 Demo completed successfully!")


if __name__ == "__main__":
    main()
