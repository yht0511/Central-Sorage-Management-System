"""
Main client for the Central Storage System API
"""

import requests
import json
from typing import List, Dict, Any, Optional, Union
from urllib.parse import urljoin, urlencode

from .models import *
from .exceptions import *


class CentralStorageClient:
    """Main client for interacting with the Central Storage System API"""
    
    def __init__(self, base_url: str = "http://localhost:8080", token: str = None):
        """
        Initialize the client
        
        Args:
            base_url: Base URL of the API server
            token: Authentication token (JWT)
        """
        self.base_url = base_url.rstrip('/')
        self.api_base = f"{self.base_url}/api"
        self.session = requests.Session()
        
        if token:
            self.set_token(token)
    
    def set_token(self, token: str):
        """Set authentication token"""
        self.session.headers.update({'Authorization': f'Bearer {token}'})
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with error handling"""
        url = urljoin(self.api_base + '/', endpoint.lstrip('/'))
        
        try:
            response = self.session.request(method, url, **kwargs)
            
            # Handle different HTTP status codes
            if response.status_code == 401:
                raise AuthenticationError("Authentication failed", response.status_code, response)
            elif response.status_code == 403:
                raise PermissionError("Permission denied", response.status_code, response)
            elif response.status_code == 404:
                raise NotFoundError("Resource not found", response.status_code, response)
            elif response.status_code == 400:
                raise ValidationError("Request validation failed", response.status_code, response)
            elif response.status_code >= 500:
                raise APIError("Server error", response.status_code, response)
            
            response.raise_for_status()
            
            # Return JSON response or empty dict
            try:
                return response.json()
            except json.JSONDecodeError:
                return {}
                
        except requests.RequestException as e:
            raise APIError(f"Request failed: {str(e)}")
    
    def _get(self, endpoint: str, params: Dict = None) -> Dict[str, Any]:
        """Make GET request"""
        return self._request('GET', endpoint, params=params)
    
    def _post(self, endpoint: str, data: Dict = None, json_data: Dict = None) -> Dict[str, Any]:
        """Make POST request"""
        return self._request('POST', endpoint, data=data, json=json_data)
    
    def _put(self, endpoint: str, data: Dict = None, json_data: Dict = None) -> Dict[str, Any]:
        """Make PUT request"""
        return self._request('PUT', endpoint, data=data, json=json_data)
    
    def _delete(self, endpoint: str) -> Dict[str, Any]:
        """Make DELETE request"""
        return self._request('DELETE', endpoint)
    
    # Authentication methods
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Login and get authentication token"""
        data = {"username": username, "password": password}
        response = self._post("/login", json_data=data)
        
        if "token" in response:
            self.set_token(response["token"])
        
        return response
    
    def get_profile(self) -> User:
        """Get current user profile"""
        response = self._get("/profile")
        return User(**response.get("user", {}))
    
    def update_profile(self, user_data: Dict[str, Any]) -> User:
        """Update user profile"""
        response = self._put("/profile", json_data=user_data)
        return User(**response.get("user", {}))
    
    # Laboratory methods
    def get_laboratories(self, params: Optional[PaginationParams] = None, **filters) -> PaginationResponse:
        """Get laboratories with optional filtering and pagination"""
        query_params = {}
        
        if params:
            query_params.update({
                'page': params.page,
                'page_size': params.page_size,
                'search': params.search,
                'sort_by': params.sort_by,
                'sort_desc': params.sort_desc
            })
        
        # Add additional filters
        query_params.update(filters)
        
        # Remove empty parameters
        query_params = {k: v for k, v in query_params.items() if v}
        
        response = self._get("/laboratories", params=query_params)
        
        # Parse response data into Laboratory objects
        labs = [Laboratory(**lab) for lab in response.get("data", [])]
        
        return PaginationResponse(
            data=labs,
            total=response.get("total", 0),
            page=response.get("page", 1),
            page_size=response.get("page_size", 20),
            total_pages=response.get("total_pages", 0),
            has_next=response.get("has_next", False),
            has_prev=response.get("has_prev", False)
        )
    
    def get_laboratory(self, lab_id: int) -> Laboratory:
        """Get laboratory by ID"""
        response = self._get(f"/laboratories/{lab_id}")
        return Laboratory(**response.get("laboratory", {}))
    
    def create_laboratory(self, lab_data: Union[Laboratory, Dict[str, Any]]) -> Laboratory:
        """Create new laboratory"""
        if isinstance(lab_data, Laboratory):
            # Convert dataclass to dict, excluding None values
            data = {k: v for k, v in lab_data.__dict__.items() 
                   if v is not None and k not in ['id', 'created_at', 'updated_at', 'storages']}
        else:
            data = lab_data
        
        response = self._post("/admin/laboratories", json_data=data)
        return Laboratory(**response.get("laboratory", {}))
    
    def update_laboratory(self, lab_id: int, lab_data: Union[Laboratory, Dict[str, Any]]) -> Laboratory:
        """Update laboratory"""
        if isinstance(lab_data, Laboratory):
            data = {k: v for k, v in lab_data.__dict__.items() 
                   if v is not None and k not in ['id', 'created_at', 'updated_at', 'storages']}
        else:
            data = lab_data
        
        response = self._put(f"/admin/laboratories/{lab_id}", json_data=data)
        return Laboratory(**response.get("laboratory", {}))
    
    def delete_laboratory(self, lab_id: int) -> bool:
        """Delete laboratory"""
        self._delete(f"/admin/laboratories/{lab_id}")
        return True
    
    # Storage methods
    def get_storages(self, params: Optional[PaginationParams] = None, **filters) -> PaginationResponse:
        """Get storage devices with optional filtering and pagination"""
        query_params = {}
        
        if params:
            query_params.update({
                'page': params.page,
                'page_size': params.page_size,
                'search': params.search,
                'sort_by': params.sort_by,
                'sort_desc': params.sort_desc
            })
        
        query_params.update(filters)
        query_params = {k: v for k, v in query_params.items() if v}
        
        response = self._get("/storages", params=query_params)
        
        storages = [Storage(**storage) for storage in response.get("data", [])]
        
        return PaginationResponse(
            data=storages,
            total=response.get("total", 0),
            page=response.get("page", 1),
            page_size=response.get("page_size", 20),
            total_pages=response.get("total_pages", 0),
            has_next=response.get("has_next", False),
            has_prev=response.get("has_prev", False)
        )
    
    def get_storage(self, storage_id: int) -> Storage:
        """Get storage device by ID"""
        response = self._get(f"/storages/{storage_id}")
        return Storage(**response.get("storage", {}))
    
    def create_storage(self, storage_data: Union[Storage, Dict[str, Any]]) -> Storage:
        """Create new storage device"""
        if isinstance(storage_data, Storage):
            data = {k: v for k, v in storage_data.__dict__.items() 
                   if v is not None and k not in ['id', 'created_at', 'updated_at', 'laboratory', 'sections']}
        else:
            data = storage_data
        
        response = self._post("/admin/storages", json_data=data)
        return Storage(**response.get("storage", {}))
    
    def update_storage(self, storage_id: int, storage_data: Union[Storage, Dict[str, Any]]) -> Storage:
        """Update storage device"""
        if isinstance(storage_data, Storage):
            data = {k: v for k, v in storage_data.__dict__.items() 
                   if v is not None and k not in ['id', 'created_at', 'updated_at', 'laboratory', 'sections']}
        else:
            data = storage_data
        
        response = self._put(f"/admin/storages/{storage_id}", json_data=data)
        return Storage(**response.get("storage", {}))
    
    def delete_storage(self, storage_id: int) -> bool:
        """Delete storage device"""
        self._delete(f"/admin/storages/{storage_id}")
        return True
    
    def get_storages_by_lab(self, lab_id: int, params: Optional[PaginationParams] = None) -> PaginationResponse:
        """Get storage devices by laboratory ID"""
        query_params = {}
        if params:
            query_params.update({
                'page': params.page,
                'page_size': params.page_size,
                'search': params.search,
                'sort_by': params.sort_by,
                'sort_desc': params.sort_desc
            })
        
        query_params = {k: v for k, v in query_params.items() if v}
        
        response = self._get(f"/labs/{lab_id}/storages", params=query_params)
        
        storages = [Storage(**storage) for storage in response.get("data", [])]
        
        return PaginationResponse(
            data=storages,
            total=response.get("total", 0),
            page=response.get("page", 1),
            page_size=response.get("page_size", 20),
            total_pages=response.get("total_pages", 0),
            has_next=response.get("has_next", False),
            has_prev=response.get("has_prev", False)
        )
    
    # Section methods
    def get_sections(self, params: Optional[PaginationParams] = None, **filters) -> PaginationResponse:
        """Get sections with optional filtering and pagination"""
        query_params = {}
        
        if params:
            query_params.update({
                'page': params.page,
                'page_size': params.page_size,
                'search': params.search,
                'sort_by': params.sort_by,
                'sort_desc': params.sort_desc
            })
        
        query_params.update(filters)
        query_params = {k: v for k, v in query_params.items() if v}
        
        response = self._get("/sections", params=query_params)
        
        sections = [Section(**section) for section in response.get("data", [])]
        
        return PaginationResponse(
            data=sections,
            total=response.get("total", 0),
            page=response.get("page", 1),
            page_size=response.get("page_size", 20),
            total_pages=response.get("total_pages", 0),
            has_next=response.get("has_next", False),
            has_prev=response.get("has_prev", False)
        )
    
    def get_section(self, section_id: int) -> Section:
        """Get section by ID"""
        response = self._get(f"/sections/{section_id}")
        return Section(**response.get("section", {}))
    
    def create_section(self, section_data: Union[Section, Dict[str, Any]]) -> Section:
        """Create new section"""
        if isinstance(section_data, Section):
            data = {k: v for k, v in section_data.__dict__.items() 
                   if v is not None and k not in ['id', 'created_at', 'updated_at', 'storage', 'items']}
        else:
            data = section_data
        
        response = self._post("/admin/sections", json_data=data)
        return Section(**response.get("section", {}))
    
    def update_section(self, section_id: int, section_data: Union[Section, Dict[str, Any]]) -> Section:
        """Update section"""
        if isinstance(section_data, Section):
            data = {k: v for k, v in section_data.__dict__.items() 
                   if v is not None and k not in ['id', 'created_at', 'updated_at', 'storage', 'items']}
        else:
            data = section_data
        
        response = self._put(f"/admin/sections/{section_id}", json_data=data)
        return Section(**response.get("section", {}))
    
    def delete_section(self, section_id: int) -> bool:
        """Delete section"""
        self._delete(f"/admin/sections/{section_id}")
        return True
    
    def get_sections_by_storage(self, storage_id: int, params: Optional[PaginationParams] = None) -> PaginationResponse:
        """Get sections by storage ID"""
        query_params = {}
        if params:
            query_params.update({
                'page': params.page,
                'page_size': params.page_size,
                'search': params.search,
                'sort_by': params.sort_by,
                'sort_desc': params.sort_desc
            })
        query_params = {k: v for k, v in query_params.items() if v}
        
        response = self._get(f"/stores/{storage_id}/sections", params=query_params)
        
        sections = [Section(**section) for section in response.get("sections", [])]
        
        return PaginationResponse(
            data=sections,
            total=response.get("total", 0),
            page=response.get("page", 1),
            page_size=response.get("page_size", 20),
            total_pages=response.get("total_pages", 0),
            has_next=response.get("has_next", False),
            has_prev=response.get("has_prev", False)
        )
    
    # Item methods
    def get_items(self, params: Optional[PaginationParams] = None, **filters) -> PaginationResponse:
        """Get items with optional filtering and pagination"""
        query_params = {}
        
        if params:
            query_params.update({
                'page': params.page,
                'page_size': params.page_size,
                'search': params.search,
                'sort_by': params.sort_by,
                'sort_desc': params.sort_desc
            })
        
        query_params.update(filters)
        query_params = {k: v for k, v in query_params.items() if v}
        
        response = self._get("/items", params=query_params)
        items = [Item(**item["item"]) for item in response["data"]]
        
        return PaginationResponse(
            data=items,
            total=response.get("total", 0),
            page=response.get("page", 1),
            page_size=response.get("page_size", 20),
            total_pages=response.get("total_pages", 0),
            has_next=response.get("has_next", False),
            has_prev=response.get("has_prev", False)
        )
    
    def get_item(self, item_id: int) -> Item:
        """Get item by ID"""
        response = self._get(f"/items/{item_id}")
        return Item(**response.get("item", {}))
    
    def create_item(self, item_data: Union[Item, Dict[str, Any]]) -> Item:
        """Create new item"""
        if isinstance(item_data, Item):
            data = {k: v for k, v in item_data.__dict__.items() 
                   if v is not None and k not in ['id', 'created_at', 'updated_at', 'section']}
        else:
            data = item_data
        
        response = self._post("/items", json_data=data)
        return Item(**response.get("item", {}))
    
    def update_item(self, item_id: int, item_data: Union[Item, Dict[str, Any]]) -> Item:
        """Update item"""
        if isinstance(item_data, Item):
            data = {k: v for k, v in item_data.__dict__.items() 
                   if v is not None and k not in ['id', 'created_at', 'updated_at', 'section']}
        else:
            data = item_data
        
        response = self._put(f"/items/{item_id}", json_data=data)
        return Item(**response.get("item", {}))
    
    def delete_item(self, item_id: int) -> bool:
        """Delete item"""
        self._delete(f"/items/{item_id}")
        return True
    
    def update_item_quantity(self, item_id: int, quantity: int) -> Item:
        """Update item quantity"""
        data = {"quantity": quantity}
        response = self._put(f"/items/{item_id}/quantity", json_data=data)
        return Item(**response.get("item", {}))
    
    def get_categories(self) -> List[str]:
        """Get all item categories"""
        response = self._get("/items/categories")
        return response.get("categories", [])
    
    def get_low_stock_items(self, params: Optional[PaginationParams] = None) -> PaginationResponse:
        """Get low stock items"""
        query_params = {}
        if params:
            query_params.update({
                'page': params.page,
                'page_size': params.page_size,
                'search': params.search,
                'sort_by': params.sort_by,
                'sort_desc': params.sort_desc
            })
        
        query_params = {k: v for k, v in query_params.items() if v}
        
        response = self._get("/items/low-stock", params=query_params)
        
        items = [Item(**item) for item in response.get("data", [])]
        
        return PaginationResponse(
            data=items,
            total=response.get("total", 0),
            page=response.get("page", 1),
            page_size=response.get("page_size", 20),
            total_pages=response.get("total_pages", 0),
            has_next=response.get("has_next", False),
            has_prev=response.get("has_prev", False)
        )
    
    def get_expiring_items(self, params: Optional[PaginationParams] = None) -> PaginationResponse:
        """Get expiring items"""
        query_params = {}
        if params:
            query_params.update({
                'page': params.page,
                'page_size': params.page_size,
                'search': params.search,
                'sort_by': params.sort_by,
                'sort_desc': params.sort_desc
            })
        
        query_params = {k: v for k, v in query_params.items() if v}
        
        response = self._get("/items/expiring", params=query_params)
        
        items = [Item(**item) for item in response.get("data", [])]
        
        return PaginationResponse(
            data=items,
            total=response.get("total", 0),
            page=response.get("page", 1),
            page_size=response.get("page_size", 20),
            total_pages=response.get("total_pages", 0),
            has_next=response.get("has_next", False),
            has_prev=response.get("has_prev", False)
        )
    
    def check_item_code_exists(self, code: str, exclude_id: int = None) -> bool:
        """Check if item code already exists"""
        params = {"code": code}
        if exclude_id:
            params["exclude_id"] = exclude_id
        
        response = self._get("/items/check-code", params=params)
        return response.get("exists", False)
    
    # Movement methods
    def get_movements(self, params: Optional[PaginationParams] = None, **filters) -> PaginationResponse:
        """Get movement records with optional filtering and pagination"""
        query_params = {}
        
        if params:
            query_params.update({
                'page': params.page,
                'page_size': params.page_size,
                'search': params.search,
                'sort_by': params.sort_by,
                'sort_desc': params.sort_desc
            })
        
        query_params.update(filters)
        query_params = {k: v for k, v in query_params.items() if v}
        
        response = self._get("/movements", params=query_params)
        
        movements = [Movement(**movement) for movement in response.get("data", [])]
        
        return PaginationResponse(
            data=movements,
            total=response.get("total", 0),
            page=response.get("page", 1),
            page_size=response.get("page_size", 20),
            total_pages=response.get("total_pages", 0),
            has_next=response.get("has_next", False),
            has_prev=response.get("has_prev", False)
        )
    
    def create_movement(self, movement_data: Union[Movement, Dict[str, Any]]) -> Movement:
        """Create new movement record (admin only)"""
        if isinstance(movement_data, Movement):
            data = {k: v for k, v in movement_data.__dict__.items() 
                   if v is not None and k not in ['id', 'created_at', 'updated_at', 'item', 'user']}
        else:
            data = movement_data
        
        response = self._post("/admin/movements", json_data=data)
        return Movement(**response.get("movement", {}))
    
    def delete_movement(self, movement_id: int) -> bool:
        """Delete movement record (admin only)"""
        self._delete(f"/admin/movements/{movement_id}")
        return True
    
    def export_movements_csv(self, **filters) -> bytes:
        """Export movements to CSV"""
        query_params = {k: v for k, v in filters.items() if v}
        
        response = self.session.get(
            f"{self.api_base}/movements/export",
            params=query_params
        )
        response.raise_for_status()
        return response.content
    
    # User management methods (admin only)
    def register_user(self, user_data: Union[User, Dict[str, Any]]) -> User:
        """Register new user (admin only)"""
        if isinstance(user_data, User):
            data = {k: v for k, v in user_data.__dict__.items() 
                   if v is not None and k not in ['id', 'created_at', 'updated_at', 'last_login']}
        else:
            data = user_data
        
        response = self._post("/admin/register", json_data=data)
        return User(**response.get("user", {}))
    
    def get_users(self, params: Optional[PaginationParams] = None, **filters) -> PaginationResponse:
        """Get users (admin only)"""
        query_params = {}
        
        if params:
            query_params.update({
                'page': params.page,
                'page_size': params.page_size,
                'search': params.search,
                'sort_by': params.sort_by,
                'sort_desc': params.sort_desc
            })
        
        query_params.update(filters)
        query_params = {k: v for k, v in query_params.items() if v}
        
        response = self._get("/admin/users", params=query_params)
        
        users = [User(**user) for user in response.get("data", [])]
        
        return PaginationResponse(
            data=users,
            total=response.get("total", 0),
            page=response.get("page", 1),
            page_size=response.get("page_size", 20),
            total_pages=response.get("total_pages", 0),
            has_next=response.get("has_next", False),
            has_prev=response.get("has_prev", False)
        )
    
    def get_user(self, user_id: int) -> User:
        """Get user by ID (admin only)"""
        response = self._get(f"/admin/users/{user_id}")
        return User(**response.get("user", {}))
    
    def update_user(self, user_id: int, user_data: Union[User, Dict[str, Any]]) -> User:
        """Update user (admin only)"""
        if isinstance(user_data, User):
            data = {k: v for k, v in user_data.__dict__.items() 
                   if v is not None and k not in ['id', 'created_at', 'updated_at', 'last_login']}
        else:
            data = user_data
        
        response = self._put(f"/admin/users/{user_id}", json_data=data)
        return User(**response.get("user", {}))
    
    def delete_user(self, user_id: int) -> bool:
        """Delete user (admin only)"""
        self._delete(f"/admin/users/{user_id}")
        return True
    
    # Statistics methods
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics"""
        return self._get("/stats/dashboard")
    
    def get_user_stats(self) -> Dict[str, Any]:
        """Get user statistics"""
        return self._get("/stats/user")
    
    # Health check
    def health_check(self) -> Dict[str, str]:
        """Check API health"""
        return self._get("/health")
