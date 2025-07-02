#!/usr/bin/env python3
"""
Section Batch Generator - 批量分区生成工具

This script provides an easy way to batch generate sections for storage devices.
用于批量生成存储设备分区的工具。
"""

import sys
from pathlib import Path

# Add the SDK to Python path
sdk_path = Path(__file__).parent / "central_storage_sdk"
sys.path.insert(0, str(sdk_path.parent))

from central_storage_sdk import CentralStorageClient
from central_storage_sdk.batch import BatchOperations
from central_storage_sdk.models import PaginationParams
from central_storage_sdk.utils import generate_code


def main():
    print("📋 Section Batch Generator - 批量分区生成工具")
    print("=" * 60)
    
    # Configuration
    BASE_URL = "http://localhost:8080"
    USERNAME = "admin"
    PASSWORD = "admin123"  # Change to your admin password
    
    try:
        # Initialize and login
        client = CentralStorageClient(base_url=BASE_URL)
        client.login(USERNAME, PASSWORD)
        print(f"✅ Logged in as {USERNAME}")
        
        batch = BatchOperations(client)
        
        while True:
            print("\n" + "=" * 60)
            print("📋 Section Generation Options:")
            print("1. 🏗️  Generate Sections for Specific Storage")
            print("2. 🔄 Generate Sections for All Storages")
            print("3. 🎯 Custom Section Generation")
            print("4. 📊 View Current Sections")
            print("5. 🗂️  Generate Standard Lab Sections")
            print("6. ❌ Exit")
            
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == "1":
                generate_for_specific_storage(client, batch)
            elif choice == "2":
                generate_for_all_storages(client, batch)
            elif choice == "3":
                custom_section_generation(client, batch)
            elif choice == "4":
                view_current_sections(client)
            elif choice == "5":
                generate_standard_lab_sections(client, batch)
            elif choice == "6":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please try again.")
    
    except Exception as e:
        print(f"❌ Error: {e}")


def generate_for_specific_storage(client, batch):
    """Generate sections for a specific storage device"""
    print("\n🏗️ Generate Sections for Specific Storage")
    print("-" * 50)
    
    # Get available storage devices
    storages = client.get_storages(params=PaginationParams(page_size=100))
    if not storages.data:
        print("❌ No storage devices found.")
        return
    
    print("Available Storage Devices:")
    for i, storage in enumerate(storages.data):
        lab_name = storage.laboratory.name if storage.laboratory else "Unknown Lab"
        print(f"  {i+1:2d}. {storage.name} ({storage.code}) - {lab_name}")
    
    try:
        storage_index = int(input(f"\nSelect storage (1-{len(storages.data)}): ")) - 1
        if storage_index < 0 or storage_index >= len(storages.data):
            print("❌ Invalid selection.")
            return
        
        storage = storages.data[storage_index]
        count = int(input("Number of sections to create (default 10): ") or "10")
        
        print(f"\n🚀 Creating {count} sections for '{storage.name}'...")
        sections = batch.create_sections_for_storage(storage.id, count=count)
        
        print(f"✅ Successfully created {len(sections)} sections:")
        for i, section in enumerate(sections[:5]):  # Show first 5
            print(f"   {i+1}. {section.name} ({section.code}) - {section.position}")
        if len(sections) > 5:
            print(f"   ... and {len(sections) - 5} more sections")
    
    except ValueError:
        print("❌ Invalid input.")
    except Exception as e:
        print(f"❌ Error: {e}")


def generate_for_all_storages(client, batch):
    """Generate sections for all storage devices"""
    print("\n🔄 Generate Sections for All Storages")
    print("-" * 50)
    
    storages = client.get_storages(params=PaginationParams(page_size=100))
    if not storages.data:
        print("❌ No storage devices found.")
        return
    
    print(f"Found {len(storages.data)} storage devices")
    
    try:
        count_per_storage = int(input("Sections per storage device (default 5): ") or "5")
        
        confirm = input(f"Create {count_per_storage} sections for each of {len(storages.data)} storages? (y/N): ")
        if confirm.lower() != 'y':
            print("❌ Operation cancelled.")
            return
        
        total_created = 0
        for i, storage in enumerate(storages.data, 1):
            print(f"📦 Processing storage {i}/{len(storages.data)}: {storage.name}")
            sections = batch.create_sections_for_storage(storage.id, count=count_per_storage)
            total_created += len(sections)
            print(f"   ✅ Created {len(sections)} sections")
        
        print(f"\n🎉 Total created: {total_created} sections across {len(storages.data)} storage devices")
    
    except ValueError:
        print("❌ Invalid input.")
    except Exception as e:
        print(f"❌ Error: {e}")


def custom_section_generation(client, batch):
    """Custom section generation with user-defined parameters"""
    print("\n🎯 Custom Section Generation")
    print("-" * 50)
    
    # Get storage device
    storages = client.get_storages(params=PaginationParams(page_size=100))
    if not storages.data:
        print("❌ No storage devices found.")
        return
    
    print("Available Storage Devices:")
    for i, storage in enumerate(storages.data):
        print(f"  {i+1:2d}. {storage.name} ({storage.code})")
    
    try:
        storage_index = int(input(f"\nSelect storage (1-{len(storages.data)}): ")) - 1
        storage = storages.data[storage_index]
        
        print(f"\n📝 Custom Section Configuration for '{storage.name}':")
        
        # Get custom parameters
        name_prefix = input("Section name prefix (default 'Section'): ") or "Section"
        code_prefix = input("Section code prefix (default 'SEC'): ") or "SEC"
        rows = int(input("Number of rows (default 3): ") or "3")
        cols = int(input("Number of columns (default 4): ") or "4")
        capacity = int(input("Capacity per section (default 50): ") or "50")
        
        # Generate custom sections
        sections_data = []
        section_count = 0
        
        for row in range(1, rows + 1):
            for col in range(1, cols + 1):
                section_count += 1
                section_data = {
                    "code": f"{code_prefix}{section_count:03d}",
                    "name": f"{name_prefix} R{row}C{col}",
                    "position": f"Row {row}, Column {col}",
                    "description": f"Custom section at row {row}, column {col}",
                    "capacity": capacity,
                    "storage_id": storage.id,
                    "properties": {
                        "row": row,
                        "column": col,
                        "custom_generated": True
                    }
                }
                sections_data.append(section_data)
        
        print(f"\n🚀 Creating {len(sections_data)} custom sections...")
        sections = batch.create_sections_batch(sections_data)
        
        print(f"✅ Successfully created {len(sections)} custom sections!")
        print("\nLayout preview:")
        for row in range(1, rows + 1):
            row_sections = [s for s in sections if s.properties.get("row") == row]
            row_names = [s.name for s in row_sections]
            print(f"  Row {row}: {' | '.join(row_names)}")
    
    except ValueError:
        print("❌ Invalid input.")
    except Exception as e:
        print(f"❌ Error: {e}")


def view_current_sections(client):
    """View current sections"""
    print("\n📊 Current Sections Overview")
    print("-" * 50)
    
    sections = client.get_sections(params=PaginationParams(page_size=100))
    
    if not sections.data:
        print("❌ No sections found.")
        return
    
    print(f"Total sections: {sections.total}")
    
    # Group by storage
    storage_sections = {}
    for section in sections.data:
        storage_id = section.storage_id
        if storage_id not in storage_sections:
            storage_sections[storage_id] = []
        storage_sections[storage_id].append(section)
    
    print(f"\nSections grouped by storage device:")
    for storage_id, section_list in storage_sections.items():
        # Get storage name
        try:
            storage = client.get_storage(storage_id)
            storage_name = storage.name
        except:
            storage_name = f"Storage ID {storage_id}"
        
        print(f"\n📦 {storage_name} ({len(section_list)} sections):")
        for section in section_list[:5]:  # Show first 5
            status_emoji = "✅" if section.status == "可用" else "⚠️"
            print(f"   {status_emoji} {section.name} ({section.code}) - {section.position}")
        if len(section_list) > 5:
            print(f"   ... and {len(section_list) - 5} more sections")


def generate_standard_lab_sections(client, batch):
    """Generate standard laboratory sections"""
    print("\n🗂️ Generate Standard Lab Sections")
    print("-" * 50)
    
    # Predefined section templates
    templates = {
        "试剂柜": {
            "sections": [
                {"name": "有机试剂区", "capacity": 30, "properties": {"chemical_type": "organic"}},
                {"name": "无机试剂区", "capacity": 40, "properties": {"chemical_type": "inorganic"}},
                {"name": "酸碱区", "capacity": 20, "properties": {"chemical_type": "acid_base", "ventilation": True}},
                {"name": "易燃品区", "capacity": 15, "properties": {"chemical_type": "flammable", "safety_level": "high"}},
            ]
        },
        "器材柜": {
            "sections": [
                {"name": "玻璃器皿区", "capacity": 50, "properties": {"item_type": "glassware"}},
                {"name": "金属工具区", "capacity": 30, "properties": {"item_type": "metal_tools"}},
                {"name": "电子设备区", "capacity": 20, "properties": {"item_type": "electronics"}},
                {"name": "消耗品区", "capacity": 100, "properties": {"item_type": "consumables"}},
            ]
        },
        "样品柜": {
            "sections": [
                {"name": "标准样品区", "capacity": 25, "properties": {"sample_type": "standard"}},
                {"name": "实验样品区", "capacity": 35, "properties": {"sample_type": "experimental"}},
                {"name": "冷藏样品区", "capacity": 20, "properties": {"sample_type": "refrigerated", "temperature": "4°C"}},
                {"name": "长期存储区", "capacity": 40, "properties": {"sample_type": "long_term"}},
            ]
        }
    }
    
    # Get storage devices and their types
    storages = client.get_storages(params=PaginationParams(page_size=100))
    if not storages.data:
        print("❌ No storage devices found.")
        return
    
    # Filter storages by type
    storage_by_type = {}
    for storage in storages.data:
        storage_type = storage.type
        if storage_type in templates:
            if storage_type not in storage_by_type:
                storage_by_type[storage_type] = []
            storage_by_type[storage_type].append(storage)
    
    if not storage_by_type:
        print("❌ No storage devices with supported types found.")
        print(f"Supported types: {', '.join(templates.keys())}")
        return
    
    print("Available storage devices by type:")
    for storage_type, storage_list in storage_by_type.items():
        print(f"\n📦 {storage_type} ({len(storage_list)} devices):")
        for storage in storage_list:
            print(f"   - {storage.name} ({storage.code})")
    
    # Generate sections for each type
    total_created = 0
    for storage_type, storage_list in storage_by_type.items():
        template = templates[storage_type]
        
        confirm = input(f"\nGenerate standard sections for {len(storage_list)} {storage_type} devices? (y/N): ")
        if confirm.lower() != 'y':
            continue
        
        for storage in storage_list:
            print(f"📦 Generating sections for {storage.name}...")
            sections_data = []
            
            for i, section_template in enumerate(template["sections"], 1):
                section_data = {
                    "code": generate_code("STD", 4),
                    "name": section_template["name"],
                    "position": f"Standard Position {i}",
                    "description": f"标准{section_template['name']}分区",
                    "capacity": section_template["capacity"],
                    "storage_id": storage.id,
                    "properties": {
                        **section_template["properties"],
                        "template_generated": True,
                        "template_type": storage_type
                    }
                }
                sections_data.append(section_data)
            
            sections = batch.create_sections_batch(sections_data)
            total_created += len(sections)
            print(f"   ✅ Created {len(sections)} standard sections")
    
    print(f"\n🎉 Total created: {total_created} standard sections")


if __name__ == "__main__":
    main()
