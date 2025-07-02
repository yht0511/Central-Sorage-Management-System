"""
Data models for the Central Storage System SDK
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime

@dataclass
class BaseModel:
    """Base model with common fields"""
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class User(BaseModel):
    """User model"""
    username: str = ""
    email: str = ""
    role: str = "user"  # admin, user
    active: bool = True
    real_name: str = ""
    phone: str = ""
    department: str = ""
    bio: str = ""
    last_login: Optional[datetime] = None

@dataclass
class Laboratory(BaseModel):
    """Laboratory model"""
    code: str = ""
    name: str = ""
    location: str = ""
    description: str = ""
    security_level: int = 1  # 1-5
    storages: List['Storage'] = field(default_factory=list)

@dataclass
class Storage(BaseModel):
    """Storage device model"""
    code: str = ""
    name: str = ""
    type: str = ""
    location: str = ""
    description: str = ""
    status: str = "运行中"  # 运行中、维护中、停用
    capacity: int = 0
    security_level: int = 1  # 1-5
    properties: Dict[str, Any] = field(default_factory=dict)
    lab_id: Optional[int] = None
    laboratory: Optional[Laboratory] = None
    sections: List['Section'] = field(default_factory=list)

@dataclass
class Section(BaseModel):
    """Section model"""
    code: str = ""
    name: str = ""
    position: str = ""
    description: str = ""
    status: str = "可用"  # 可用、已满、维护中、停用
    security_level: int = 1  # 1-5
    capacity: int = 100
    used_capacity: int = 0
    properties: Dict[str, Any] = field(default_factory=dict)
    storage_id: Optional[int] = None
    storage: Optional[Storage] = None
    items: List['Item'] = field(default_factory=list)

@dataclass
class Item(BaseModel):
    """Item model"""
    code: str = ""
    name: str = ""
    description: str = ""
    category: str = ""
    properties: Dict[str, Any] = field(default_factory=dict)
    price: float = 0.0
    quantity: int = 0
    min_quantity: int = 0
    unit: str = ""
    supplier: str = ""
    purchase_date: Optional[str] = None  # Format: YYYY-MM-DD
    expiry_date: Optional[str] = None    # Format: YYYY-MM-DD
    section_id: Optional[int] = None
    section: Optional[Section] = None

@dataclass
class Movement(BaseModel):
    """Movement record model"""
    item_id: int = 0
    item: Optional[Item] = None
    movement_type: str = ""  # 入库、出库、转移、盘点、损坏、报废
    from_location: str = ""
    to_location: str = ""
    quantity: int = 0
    reason: str = ""
    notes: str = ""
    user_id: int = 0
    user: Optional[User] = None

@dataclass
class PaginationParams:
    """Pagination parameters"""
    page: int = 1
    page_size: int = 20
    search: str = ""
    sort_by: str = ""
    sort_desc: bool = False

@dataclass
class PaginationResponse:
    """Pagination response"""
    data: List[Any] = field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 20
    total_pages: int = 0
    has_next: bool = False
    has_prev: bool = False
