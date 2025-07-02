# Central Storage System Python SDK

A comprehensive Python client library for interacting with the Central Storage System API.

## Features

- 🔐 **Authentication** - JWT token-based authentication
- 🏢 **Laboratory Management** - Create, read, update, delete laboratories
- 📦 **Storage Device Management** - Manage storage devices (cabinets, containers)
- 📋 **Section Management** - Handle storage sections (drawers, compartments)
- 📝 **Item Management** - Full CRUD operations for items with inventory tracking
- 👥 **User Management** - User administration (admin only)
- 📊 **Movement Tracking** - Track item movements and inventory changes
- 🔍 **Search & Filtering** - Advanced search and filtering capabilities
- 📄 **Pagination** - Efficient handling of large datasets
- ⚡ **Batch Operations** - Efficient bulk operations
- 🧪 **Test Data Generation** - Built-in test data generators

## Installation

```bash
pip install central-storage-sdk
```

Or install from source:

```bash
cd python_sdk
pip install -e .
```

## Quick Start

```python
from central_storage_sdk import CentralStorageClient

# Initialize client
client = CentralStorageClient(base_url="http://localhost:8080")

# Login
response = client.login("admin", "admin123")
print(f"Logged in successfully: {response}")

# Get laboratories
labs = client.get_laboratories()
print(f"Found {labs.total} laboratories")

# Create a new laboratory
new_lab = client.create_laboratory({
    "code": "LAB001",
    "name": "Chemistry Lab",
    "location": "Building A, Floor 2",
    "description": "Main chemistry laboratory",
    "security_level": 2
})
print(f"Created laboratory: {new_lab.name}")
```

## Batch Operations

The SDK includes powerful batch operations for efficient data management:

```python
from central_storage_sdk import CentralStorageClient
from central_storage_sdk.batch import BatchOperations

# Initialize
client = CentralStorageClient("http://localhost:8080")
client.login("admin", "admin123")

# Create batch operations handler
batch = BatchOperations(client)

# Set up complete test environment
result = batch.setup_test_environment(
    lab_count=5,           # Create 5 laboratories
    storage_per_lab=3,     # 3 storage devices per lab
    section_per_storage=5, # 5 sections per storage
    item_per_section=3     # 3 items per section
)

print(f"Created {len(result['laboratories'])} labs, "
      f"{len(result['storages'])} storages, "
      f"{len(result['sections'])} sections, "
      f"{len(result['items'])} items")
```

## API Reference

### Authentication

```python
# Login
client.login("username", "password")

# Get current user profile
profile = client.get_profile()

# Update profile
client.update_profile({"real_name": "John Doe", "department": "Chemistry"})
```

### Laboratory Management

```python
# Get all laboratories with pagination
labs = client.get_laboratories(params=PaginationParams(page=1, page_size=20))

# Get laboratory by ID
lab = client.get_laboratory(1)

# Create laboratory
new_lab = client.create_laboratory({
    "code": "LAB001",
    "name": "Physics Lab",
    "location": "Building B",
    "security_level": 3
})

# Update laboratory
updated_lab = client.update_laboratory(1, {"name": "Updated Physics Lab"})

# Delete laboratory
client.delete_laboratory(1)
```

### Storage Device Management

```python
# Get storage devices
storages = client.get_storages()

# Get storages by laboratory
lab_storages = client.get_storages_by_lab(lab_id=1)

# Create storage device
storage = client.create_storage({
    "code": "STG001",
    "name": "Chemical Storage Cabinet",
    "type": "试剂柜",
    "lab_id": 1,
    "capacity": 100,
    "security_level": 2
})
```

### Section Management

```python
# Get sections
sections = client.get_sections()

# Get sections by storage
storage_sections = client.get_sections_by_storage(storage_id=1)

# Create section
section = client.create_section({
    "code": "SEC001",
    "name": "Top Shelf",
    "position": "Row 1, Column 1",
    "storage_id": 1,
    "capacity": 50
})

# Batch create sections for a storage
batch_sections = batch.create_sections_for_storage(storage_id=1, count=10)
```

### Item Management

```python
# Get items with filtering
items = client.get_items(category="化学试剂", status="available")

# Create item
item = client.create_item({
    "code": "ITM001",
    "name": "Sodium Chloride",
    "category": "化学试剂",
    "quantity": 100,
    "unit": "g",
    "section_id": 1,
    "properties": {
        "purity": "99.9%",
        "cas_number": "7647-14-5"
    }
})

# Update item quantity
client.update_item_quantity(item_id=1, quantity=150)

# Get low stock items
low_stock = client.get_low_stock_items()

# Get expiring items
expiring = client.get_expiring_items()
```

### Advanced Features

```python
# Get complete inventory overview
inventory = batch.get_full_inventory()

# Migrate sections between storages
batch.migrate_sections_to_storage([1, 2, 3], target_storage_id=5)

# Bulk update item quantities
updates = [
    {"item_id": 1, "quantity": 100},
    {"item_id": 2, "quantity": 250},
    {"item_id": 3, "quantity": 50}
]
batch.bulk_update_item_quantities(updates)

# Export movements to CSV
csv_data = client.export_movements_csv(
    start_date="2024-01-01",
    end_date="2024-12-31"
)
```

## Data Models

The SDK provides strongly-typed data models:

```python
from central_storage_sdk.models import Laboratory, Storage, Section, Item

# Models include validation and type hints
lab = Laboratory(
    code="LAB001",
    name="Chemistry Lab",
    security_level=2
)
```

## Error Handling

```python
from central_storage_sdk.exceptions import (
    APIError, AuthenticationError, PermissionError,
    NotFoundError, ValidationError
)

try:
    client.get_laboratory(999)
except NotFoundError:
    print("Laboratory not found")
except PermissionError:
    print("Access denied")
except APIError as e:
    print(f"API error: {e}")
```

## Configuration

```python
# Custom configuration
client = CentralStorageClient(
    base_url="https://your-api-server.com",
    token="your-jwt-token"
)

# Set token later
client.set_token("new-token")
```

## Requirements

- Python 3.7+
- requests >= 2.25.0

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

For support, please open an issue on GitHub or contact the development team.
