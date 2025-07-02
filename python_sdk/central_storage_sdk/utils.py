"""
Utility functions for the Central Storage System SDK
"""

from typing import List, Dict, Any
import random
import string
from datetime import datetime, timedelta

def generate_code(prefix: str = "", length: int = 8) -> str:
    """Generate a random code with optional prefix"""
    chars = string.ascii_uppercase + string.digits
    code = ''.join(random.choices(chars, k=length))
    return f"{prefix}{code}" if prefix else code

def generate_test_laboratories(count: int = 5) -> List[Dict[str, Any]]:
    """Generate test laboratory data"""
    labs = []
    lab_types = ["化学", "生物", "物理", "材料", "电子"]
    buildings = ["A楼", "B楼", "C楼", "D楼", "实验楼"]
    
    for i in range(count):
        lab_type = random.choice(lab_types)
        building = random.choice(buildings)
        floor = random.randint(1, 5)
        room = random.randint(101, 599)
        
        lab = {
            "code": generate_code("LAB", 4),
            "name": f"{lab_type}实验室{i+1:02d}",
            "location": f"{building}{floor}F-{room}",
            "description": f"专业的{lab_type}实验室，配备先进的实验设备和安全防护设施",
            "security_level": random.randint(1, 4)
        }
        labs.append(lab)
    
    return labs

def generate_test_storages(lab_ids: List[int], count_per_lab: int = 3) -> List[Dict[str, Any]]:
    """Generate test storage device data"""
    storages = []
    storage_types = ["试剂柜", "器材柜", "样品柜", "工具柜", "文件柜"]
    statuses = ["运行中", "维护中", "停用"]
    
    for lab_id in lab_ids:
        for i in range(count_per_lab):
            storage_type = random.choice(storage_types)
            
            storage = {
                "code": generate_code("STG", 4),
                "name": f"{storage_type}-{generate_code('', 3)}",
                "type": storage_type,
                "location": f"位置{chr(65 + i)}{random.randint(1, 10)}",
                "description": f"标准{storage_type}，用于存放实验相关物品",
                "status": random.choices(statuses, weights=[80, 15, 5])[0],
                "capacity": random.randint(50, 500),
                "security_level": random.randint(1, 3),
                "lab_id": lab_id,
                "properties": {
                    "material": random.choice(["不锈钢", "塑料", "木质", "金属"]),
                    "ventilation": random.choice(["有", "无"]),
                    "lock_type": random.choice(["机械锁", "电子锁", "密码锁"])
                }
            }
            storages.append(storage)
    
    return storages

def generate_test_sections(storage_ids: List[int], count_per_storage: int = 5) -> List[Dict[str, Any]]:
    """Generate test section data"""
    sections = []
    statuses = ["可用", "已满", "维护中", "停用"]
    
    for storage_id in storage_ids:
        for i in range(count_per_storage):
            row = random.randint(1, 5)
            col = random.randint(1, 8)
            
            section = {
                "code": generate_code("SEC", 4),
                "name": f"分区{chr(65 + i)}{i+1:02d}",
                "position": f"第{row}行第{col}列",
                "description": f"标准存储分区，编号{i+1:02d}",
                "status": random.choices(statuses, weights=[70, 15, 10, 5])[0],
                "security_level": random.randint(1, 3),
                "capacity": random.randint(20, 100),
                "used_capacity": 0,  # 初始为空
                "storage_id": storage_id,
                "properties": {
                    "size": random.choice(["小", "中", "大"]),
                    "temperature_control": random.choice(["常温", "低温", "恒温"]),
                    "humidity_control": random.choice(["有", "无"])
                }
            }
            sections.append(section)
    
    return sections

def generate_test_items(section_ids: List[int], count_per_section: int = 3) -> List[Dict[str, Any]]:
    """Generate test item data"""
    items = []
    categories = ["化学试剂", "电子元件", "实验器材", "耗材", "标准样品"]
    units = ["个", "瓶", "包", "盒", "套", "ml", "g", "kg"]
    suppliers = ["科学仪器公司", "化学试剂供应商", "实验设备厂", "标准物质中心"]
    
    for section_id in section_ids:
        for i in range(count_per_section):
            category = random.choice(categories)
            unit = random.choice(units)
            quantity = random.randint(1, 50)
            
            # Generate purchase and expiry dates
            purchase_date = datetime.now() - timedelta(days=random.randint(1, 365))
            expiry_date = purchase_date + timedelta(days=random.randint(365, 1095))
            
            item = {
                "code": generate_code("ITM", 6),
                "name": f"{category}样品{i+1:03d}",
                "description": f"标准{category}，用于实验研究",
                "category": category,
                "price": round(random.uniform(10, 1000), 2),
                "quantity": quantity,
                "min_quantity": max(1, quantity // 4),
                "unit": unit,
                "supplier": random.choice(suppliers),
                "purchase_date": purchase_date.strftime("%Y-%m-%d"),
                "expiry_date": expiry_date.strftime("%Y-%m-%d"),
                "section_id": section_id,
                "properties": {
                    "batch_number": generate_code("BATCH", 6),
                    "purity": f"{random.randint(95, 99)}.{random.randint(0, 9)}%",
                    "storage_condition": random.choice(["常温", "冷藏", "冷冻", "避光"]),
                    "hazard_level": random.choice(["无害", "低毒", "中毒", "高毒"])
                }
            }
            items.append(item)
    
    return items

def batch_create_with_progress(client, create_func, data_list: List[Dict], description: str = "Creating"):
    """Batch create items with progress indication"""
    created_items = []
    total = len(data_list)
    
    print(f"{description} {total} items...")
    
    for i, data in enumerate(data_list, 1):
        try:
            item = create_func(data)
            created_items.append(item)
            
            # Progress indication
            if i % 10 == 0 or i == total:
                print(f"Progress: {i}/{total} ({i/total*100:.1f}%)")
                
        except Exception as e:
            print(f"Failed to create item {i}: {e}")
            continue
    
    print(f"Successfully created {len(created_items)} out of {total} items")
    return created_items
