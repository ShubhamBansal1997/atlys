import os
import json

from abc import ABC, abstractmethod

from typing import Any

from app.models import Product

class Database(ABC):
    def __init__(self, db_name='testDB.json'):
        self.db_name = db_name
        self.create_db_if_not_exists()
        self.db = self.load_database()
    
    @abstractmethod
    def create_db_if_not_exists(self):
        pass

    @abstractmethod
    def load_database(self):
        pass

    @abstractmethod
    def find_record(self, hash_key: str):
        pass

    @abstractmethod
    def save_new_record(self, item: Any):
        pass

class InMemoryDB(Database):
    def __init__(self, db_name):
        super().__init__(db_name=db_name)
    
    def create_db_if_not_exists(self):
        if not os.path.exists(self.db_name):
            with open(self.db_name, "w") as file:
                json.dump([], file, indent=4)

    def load_database(self):  
        file_path = self.db_name
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                return json.load(file)
        return []
    
    def find_record(self, hash_key: str) -> bool:
        # TODO: Hash key must be shifted to some localized key based on the source
        for d in self.db:
            if d['hash_key'] == hash_key:
                return True
        return False
    
    def save_new_record(self, product: Product):
        self.db.append(product.model_dump())
        with open(self.db_name, "w") as file:
            json.dump(self.db, file, indent=4)
