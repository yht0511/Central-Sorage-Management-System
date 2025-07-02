#!/usr/bin/env python3
"""
Central Storage System - Data Generation Test Script

This script demonstrates the Python SDK capabilities by creating a complete
test environment with laboratories, storage devices, sections, and items.
"""

import sys
import time
from pathlib import Path

# Add the SDK to Python path
sdk_path = Path(__file__).parent / "central_storage_sdk"
sys.path.insert(0, str(sdk_path.parent))

from central_storage_sdk import CentralStorageClient
from central_storage_sdk.batch import BatchOperations
from central_storage_sdk.models import PaginationParams
from central_storage_sdk.exceptions import APIError, AuthenticationError


def main():
    print("🧪 Central Storage System - Test Data Generation")
    print("=" * 60)
    
    # Configuration
    BASE_URL = "http://localhost:8080"
    USERNAME = "admin"
    PASSWORD = "yht050511"  # Change this to your admin password
    
    try:
        # Initialize client
        print("🔌 Connecting to API...")
        client = CentralStorageClient(base_url=BASE_URL)
        
        # Test health check
        health = client.health_check()
        print(f"✅ API Health: {health}")
        
        # Login
        print(f"🔐 Logging in as {USERNAME}...")
        login_response = client.login(USERNAME, PASSWORD)
        print(f"✅ Login successful: {login_response.get('message', 'OK')}")
        
        # Get user profile
        profile = client.get_profile()
        print(f"👤 Logged in as: {profile.real_name or profile.username} ({profile.role})")
        
        # Initialize batch operations
        batch = BatchOperations(client)
        
        # Menu system
        while True:
            print("\n" + "=" * 60)
            print("📋 Menu Options:")
            print("1. 🏗️  Create Complete Test Environment")
            print("2. 🏢 Create Test Laboratories Only")
            print("3. 📦 Create Test Storage Devices")
            print("4. 📋 Create Test Sections")
            print("5. 📝 Create Test Items")
            print("6. 📊 View Inventory Overview")
            print("7. 🔍 Search and Filter Demo")
            print("8. 🚚 Batch Operations Demo")
            print("9. ⚠️  Delete All Data (DANGEROUS)")
            print("10. ❌ Exit")
            
            choice = input("\nEnter your choice (1-10): ").strip()
            
            if choice == "1":
                create_complete_environment(batch)
            elif choice == "2":
                create_test_laboratories(batch)
            elif choice == "3":
                create_test_storages(batch, client)
            elif choice == "4":
                create_test_sections(batch, client)
            elif choice == "5":
                create_test_items(batch, client)
            elif choice == "6":
                view_inventory_overview(batch)
            elif choice == "7":
                search_and_filter_demo(client)
            elif choice == "8":
                batch_operations_demo(batch, client)
            elif choice == "9":
                delete_all_data(batch)
            elif choice == "10":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please try again.")
    
    except AuthenticationError:
        print("❌ Authentication failed. Please check your credentials.")
    except APIError as e:
        print(f"❌ API Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


def create_complete_environment(batch):
    """Create a complete test environment"""
    print("\n🏗️ Creating Complete Test Environment")
    print("-" * 40)
    
    # Get parameters from user
    try:
        lab_count = int(input("Number of laboratories (default 5): ") or "5")
        storage_per_lab = int(input("Storage devices per lab (default 3): ") or "3")
        section_per_storage = int(input("Sections per storage (default 5): ") or "5")
        item_per_section = int(input("Items per section (default 3): ") or "3")
    except ValueError:
        print("❌ Invalid input. Using default values.")
        lab_count, storage_per_lab, section_per_storage, item_per_section = 5, 3, 5, 3
    
    start_time = time.time()
    
    result = batch.setup_test_environment(
        lab_count=lab_count,
        storage_per_lab=storage_per_lab,
        section_per_storage=section_per_storage,
        item_per_section=item_per_section
    )
    
    elapsed = time.time() - start_time
    
    print(f"\n🎉 Environment created successfully in {elapsed:.2f} seconds!")
    print(f"📊 Summary:")
    print(f"   - 🏢 Laboratories: {len(result['laboratories'])}")
    print(f"   - 📦 Storage Devices: {len(result['storages'])}")
    print(f"   - 📋 Sections: {len(result['sections'])}")
    print(f"   - 📝 Items: {len(result['items'])}")


def create_test_laboratories(batch):
    """Create test laboratories only"""
    print("\n🏢 Creating Test Laboratories")
    print("-" * 40)
    
    try:
        count = int(input("Number of laboratories to create (default 5): ") or "5")
    except ValueError:
        count = 5
    
    from central_storage_sdk.utils import generate_test_laboratories
    
    lab_data = generate_test_laboratories(count)
    laboratories = batch.create_laboratories_batch(lab_data)
    
    print(f"\n✅ Created {len(laboratories)} laboratories:")
    for lab in laboratories[:3]:  # Show first 3
        print(f"   - {lab.name} ({lab.code}) - Security Level {lab.security_level}")
    if len(laboratories) > 3:
        print(f"   ... and {len(laboratories) - 3} more")


def create_test_storages(batch, client):
    """Create test storage devices"""
    print("\n📦 Creating Test Storage Devices")
    print("-" * 40)
    
    # Get existing laboratories
    labs = client.get_laboratories(PaginationParams(page_size=100))
    if not labs.data:
        print("❌ No laboratories found. Please create laboratories first.")
        return
    
    print(f"Found {len(labs.data)} laboratories:")
    for i, lab in enumerate(labs.data[:5]):
        print(f"   {i+1}. {lab.name} (ID: {lab.id})")
    
    try:
        count_per_lab = int(input("Storage devices per laboratory (default 3): ") or "3")
    except ValueError:
        count_per_lab = 3
    
    from central_storage_sdk.utils import generate_test_storages
    
    lab_ids = [lab.id for lab in labs.data if lab.id]
    storage_data = generate_test_storages(lab_ids, count_per_lab)
    storages = batch.create_storages_batch(storage_data)
    
    print(f"\n✅ Created {len(storages)} storage devices")


def create_test_sections(batch, client):
    """Create test sections"""
    print("\n📋 Creating Test Sections")
    print("-" * 40)
    
    # Get existing storage devices
    storages = client.get_storages(PaginationParams(page_size=100))
    if not storages.data:
        print("❌ No storage devices found. Please create storage devices first.")
        return
    
    print(f"Found {len(storages.data)} storage devices")
    
    try:
        count_per_storage = int(input("Sections per storage device (default 5): ") or "5")
    except ValueError:
        count_per_storage = 5
    
    from central_storage_sdk.utils import generate_test_sections
    
    storage_ids = [storage.id for storage in storages.data if storage.id]
    section_data = generate_test_sections(storage_ids, count_per_storage)
    sections = batch.create_sections_batch(section_data)
    
    print(f"\n✅ Created {len(sections)} sections")


def create_test_items(batch, client):
    """Create test items"""
    print("\n📝 Creating Test Items")
    print("-" * 40)
    
    # Get existing sections
    sections = client.get_sections(PaginationParams(page_size=100))
    if not sections.data:
        print("❌ No sections found. Please create sections first.")
        return
    
    print(f"Found {len(sections.data)} sections")
    
    try:
        count_per_section = int(input("Items per section (default 3): ") or "3")
    except ValueError:
        count_per_section = 3
    
    from central_storage_sdk.utils import generate_test_items
    
    section_ids = [section.id for section in sections.data if section.id]
    item_data = generate_test_items(section_ids, count_per_section)
    items = batch.create_items_batch(item_data)
    
    print(f"\n✅ Created {len(items)} items")


def view_inventory_overview(batch):
    """View complete inventory overview"""
    print("\n📊 Inventory Overview")
    print("-" * 40)
    
    inventory = batch.get_full_inventory()
    
    print(f"🏢 Laboratories: {inventory['laboratories']['count']}")
    print(f"📦 Storage Devices: {inventory['storages']['count']}")
    print(f"📋 Sections: {inventory['sections']['count']}")
    print(f"📝 Items: {inventory['items']['count']}")
    
    if inventory['laboratories']['count'] > 0:
        print("\n🏢 Recent Laboratories:")
        for lab in inventory['laboratories']['data'][:3]:
            print(f"   - {lab.name} ({lab.code}) at {lab.location}")
    
    if inventory['items']['count'] > 0:
        print("\n📝 Recent Items:")
        for item in inventory['items']['data'][:3]:
            print(f"   - {item.name} ({item.code}) - Qty: {item.quantity} {item.unit}")


def search_and_filter_demo(client):
    """Demonstrate search and filtering capabilities"""
    print("\n🔍 Search and Filter Demo")
    print("-" * 40)
    
    # Search laboratories
    print("1. Searching laboratories with '化学' keyword...")
    labs = client.get_laboratories(params=PaginationParams(search="化学", page_size=5))
    print(f"   Found {labs.total} laboratories:")
    for lab in labs.data:
        print(f"   - {lab.name} at {lab.location}")
    
    # Filter by security level
    print("\n2. Filtering high-security laboratories (level 3+)...")
    high_sec_labs = client.get_laboratories(security_level=3)
    print(f"   Found {high_sec_labs.total} high-security laboratories")
    
    # Search items by category
    print("\n3. Searching items in '化学试剂' category...")
    chemical_items = client.get_items(category="化学试剂", params=PaginationParams(page_size=5))
    print(f"   Found {chemical_items.total} chemical reagents:")
    for item in chemical_items.data:
        print(f"   - {item.name} - Qty: {item.quantity} {item.unit}")
    
    # Get low stock items
    print("\n4. Finding low stock items...")
    low_stock = client.get_low_stock_items(params=PaginationParams(page_size=3))
    print(f"   Found {low_stock.total} low stock items:")
    for item in low_stock.data:
        print(f"   - {item.name} - Current: {item.quantity}, Min: {item.min_quantity}")


def batch_operations_demo(batch, client):
    """Demonstrate batch operations"""
    print("\n🚚 Batch Operations Demo")
    print("-" * 40)
    
    # Get a storage device to work with
    storages = client.get_storages(params=PaginationParams(page_size=1))
    if not storages.data:
        print("❌ No storage devices found.")
        return
    
    storage = storages.data[0]
    print(f"Using storage: {storage.name}")
    
    # Create sections in batch
    print("1. Creating 5 sections for this storage...")
    sections = batch.create_sections_for_storage(storage.id, count=5)
    print(f"   ✅ Created {len(sections)} sections")
    
    if sections:
        # Create items in batch
        print("2. Creating 3 items for the first section...")
        items = batch.create_items_for_section(sections[0].id, count=3)
        print(f"   ✅ Created {len(items)} items")
        
        # Bulk update quantities
        if items:
            print("3. Bulk updating item quantities...")
            updates = [
                {"item_id": item.id, "quantity": 100 + i * 10}
                for i, item in enumerate(items) if item.id
            ]
            updated_items = batch.bulk_update_item_quantities(updates)
            print(f"   ✅ Updated {len(updated_items)} item quantities")


def delete_all_data(batch):
    """Delete all data with confirmation"""
    print("\n⚠️  DELETE ALL DATA")
    print("-" * 40)
    print("🚨 WARNING: This will delete ALL data in the system!")
    print("This action cannot be undone.")
    
    confirm1 = input("Type 'DELETE' to confirm: ").strip()
    if confirm1 != "DELETE":
        print("❌ Deletion cancelled.")
        return
    
    confirm2 = input("Are you absolutely sure? Type 'YES': ").strip()
    if confirm2 != "YES":
        print("❌ Deletion cancelled.")
        return
    
    print("🗑️ Deleting all data...")
    success = batch.delete_all_data(confirm=True)
    
    if success:
        print("✅ All data deleted successfully.")
    else:
        print("❌ Failed to delete all data.")


if __name__ == "__main__":
    main()
