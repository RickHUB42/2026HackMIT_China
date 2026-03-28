import requests
import hashlib
import time
import json
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class Restaurant:
    """Restaurant data structure"""
    id: str
    name: str
    address: str
    latitude: float
    longitude: float
    rating: float
    category: str
    phone: Optional[str] = None
    business_hours: Optional[str] = None


@dataclass
class Product:
    """Product/Menu item data structure"""
    id: str
    restaurant_id: str
    name: str
    price: float
    original_price: Optional[float] = None
    description: Optional[str] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    is_available: bool = True


class MeituanAPIClient:
    BASE_URL = "https://api-open-cater.meituan.com"
    TEST_URL = "https://sqt-api.test.meituan.com"
    def __init__(self, app_key, app_secret, developer_id, use_test_env = False):
        self.app_key = app_key
        self.app_secret = app_secret
        self.developer_id = developer_id
        self.base_url = self.TEST_URL if use_test_env else self.BASE_URL
    def _generate_sign(self, params):
        sorted_params = sorted(params.items())
        sign_str = "&".join([f"{k}={v}" for k, v in sorted_params])
        sign_str += f"&{self.app_secret}"
        return hashlib.md5(sign_str.encode('utf-8')).hexdigest()
    
    def _build_common_params(self):
        timestamp = str(int(time.time()))
        
        return {
            "developerId": self.developer_id,
            "timestamp": timestamp,
            "version": "2",
            "charset": "utf-8"
        }
    
    def get_nearby_restaurants(
        self, 
        latitude, 
        longitude, 
        radius = 5000,
        category = None,
        page = 1,
        page_size = 20
    ):
        common_params = self._build_common_params()
        biz_params = {
            "lng": str(longitude),
            "lat": str(latitude),
            "distance": radius,
            "page": page,
            "pageSize": page_size
        }
        if category:
            biz_params["category"] = category
        biz_json = json.dumps(biz_params, separators=(',', ':'))
        params = {
            **common_params,
            "appAuthToken": self.app_key,  # In real implementation, this is an OAuth token
            "biz": biz_json
        }
        params["sign"] = self._generate_sign(params)
        try:
            endpoint = f"{self.base_url}/openapi/daocanPoi/list"
            response = requests.post(
                endpoint,
                data=params,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded;charset=utf-8"
                },
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            if data.get("code") == "OP_SUCCESS":
                return self._parse_restaurants(data.get("data", {}))
            else:
                raise MeituanAPIError(f"API Error: {data.get('msg', 'Unknown error')}")
        except requests.RequestException as e:
            raise MeituanAPIError(f"Request failed: {str(e)}")
    
    def get_restaurant_products(
        self, 
        restaurant_id,
        page= 1,
        page_size = 50
    ):
        common_params = self._build_common_params()
        biz_params = {
            "poiId": restaurant_id,  # Point of Interest ID
            "page": page,
            "pageSize": page_size
        }
        biz_json = json.dumps(biz_params, separators=(',', ':'))
        params = {
            **common_params,
            "appAuthToken": self.app_key,
            "biz": biz_json,
            "sign": ""  # Will be generated
        }
        params["sign"] = self._generate_sign(params)
        try:
            endpoint = f"{self.base_url}/rms/pos/api/v1/poi/wm/goods/rel"
            response = requests.post(
                endpoint,
                data=params,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded;charset=utf-8"
                },
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            if data.get("code") == "OP_SUCCESS":
                return self._parse_products(data.get("data", {}), restaurant_id)
            else:
                raise MeituanAPIError(f"API Error: {data.get('msg', 'Unknown error')}")
        except requests.RequestException as e:
            raise MeituanAPIError(f"Request failed: {str(e)}")
    
    def get_nearby_restaurants_with_products(
        self,
        latitude,
        longitude,
        radius = 5000
    ):
        restaurants = self.get_nearby_restaurants(
            latitude=latitude,
            longitude=longitude,
            radius=radius
        )
        
        results = {}
        for restaurant in restaurants:
            try:
                products = self.get_restaurant_products(restaurant.id)
                results[restaurant.id] = products
            except MeituanAPIError as e:
                print(f"Warning: Failed to fetch products for {restaurant.name}: {e}")
                results[restaurant.id] = []        
        return results
    
    def _parse_restaurants(self, data):
        restaurants = []
        poi_list = data.get("poiList", []) or data.get("data", [])
        
        for poi in poi_list:
            restaurant = Restaurant(
                id=str(poi.get("poiId") or poi.get("id")),
                name=poi.get("name", ""),
                address=poi.get("address", ""),
                latitude=float(poi.get("lat", 0)),
                longitude=float(poi.get("lng", 0)),
                rating=float(poi.get("avgScore", 0) or poi.get("rating", 0)),
                category=poi.get("category", ""),
                phone=poi.get("phone"),
                business_hours=poi.get("openTime")
            )
            restaurants.append(restaurant)
        return restaurants
    
    def _parse_products(self, data, restaurant_id):
        products = []
        goods_list = data.get("goodsList", []) or data.get("data", [])
        
        for item in goods_list:
            product = Product(
                id=str(item.get("skuId") or item.get("id")),
                restaurant_id=restaurant_id,
                name=item.get("name", ""),
                price=float(item.get("price", 0)),
                original_price=item.get("originalPrice"),
                description=item.get("description"),
                category=item.get("categoryName"),
                image_url=item.get("picture"),
                is_available=item.get("status", 1) == 1
            )
            products.append(product)
        return products


client = MeituanAPIClient(
    app_key="被美团做局了",
    app_secret="未成年人歧视", 
    developer_id="",
    use_test_env=True  
)

latitude = 22.3248
longitude = 114.0316
restaurants = client.get_nearby_restaurants(
    latitude=latitude,
    longitude=longitude,
    radius=5000  # 5km
)

#print(f"Found {len(restaurants)} restaurants:")
#for r in restaurants[:5]:
#    print(f"  - {r.name} ({r.rating}★) - {r.category}")
restaurant_products = client.get_nearby_restaurants_with_products(
    latitude=latitude,
    longitude=longitude,
    radius=5000
)

for restaurant_id, products in list(restaurant_products.items())[:3]:
    print(f"\nRestaurant ID {restaurant_id}:")
    print(f"  Products: {len(products)} items")
    for p in products[:3]:
        print(f"    - {p.name}: ¥{p.price}")
