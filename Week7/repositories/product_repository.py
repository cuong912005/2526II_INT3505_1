from pymongo import MongoClient, ReturnDocument
from bson.objectid import ObjectId
from config import MONGO_CONFIG
from datetime import datetime

class ProductRepository:
    def __init__(self):
        # Khởi tạo kết nối MongoDB theo config.py
        self.client = MongoClient(
            MONGO_CONFIG['uri'],
            serverSelectionTimeoutMS=MONGO_CONFIG['server_selection_timeout']
        )
        self.db = self.client[MONGO_CONFIG['database']]
        self.collection = self.db['products']

    def get_all(self, skip=0, limit=10, search=None):
        query = {}
        if search:
            # Tìm kiếm gần đúng không phân biệt hoa/thường
            query['name'] = {'$regex': search, '$options': 'i'}
            
        cursor = self.collection.find(query).skip(skip).limit(limit)
        return list(cursor)

    def get_by_id(self, product_id):
        if not ObjectId.is_valid(product_id):
            return None
        return self.collection.find_one({'_id': ObjectId(product_id)})

    def create(self, product_data):
        now = datetime.utcnow()
        product_data['createdAt'] = now
        product_data['updatedAt'] = now
        
        result = self.collection.insert_one(product_data)
        product_data['_id'] = result.inserted_id
        return product_data

    def update(self, product_id, product_data):
        if not ObjectId.is_valid(product_id):
            return None
            
        product_data['updatedAt'] = datetime.utcnow()
        result = self.collection.find_one_and_update(
            {'_id': ObjectId(product_id)},
            {'$set': product_data},
            return_document=ReturnDocument.AFTER
        )
        return result

    def delete(self, product_id):
        if not ObjectId.is_valid(product_id):
            return False
            
        result = self.collection.delete_one({'_id': ObjectId(product_id)})
        return result.deleted_count > 0