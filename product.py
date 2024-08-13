from enum import Enum
from json import JSONEncoder
from typing import Any



class product:


    def __init__(self, id: int, name: str, price: float = 0, count: float = 1, isWeight: bool = False, completed: bool = False, category: str = "Стандартные") -> None:
        self.Name = name
        self.Id = id
        self.Price = price
        self.Count = count
        self.IsWeight = isWeight
        self.Completed = completed
        self.Category = category

    def set_price(self, new_price: float):
        self.price = new_price

    def set_count(self, new_count: int):
        self.count = new_count

    def set_complete(self, iscomplete: bool):
        self.completed = iscomplete
    
    def set_category(self, category: str):
        self.Category = category

    def __dict__(self):
        return dict(id=self.Id, name=self.Name, price=self.price, count=self.Count, isWeight=self.IsWeight, completed=self.Completed, category=self.Category)
    
    def __str__(self) -> str:
        return f"[name: {self.Name}, id: {self.Id}, completed: {self.Completed}, category: {self.Category}]"
    
    def __repr__(self) -> str:
        return f"[name: {self.Name}, id: {self.Id}, completed: {self.Completed}, category: {self.Category}]"
    
class productEncoder(JSONEncoder):
    def default(self, p: Any) -> Any:
        if isinstance(p, product):
            return dict(Id=p.Id, Name=p.Name, Price=p.Price, Count=p.Count, IsWeight=p.IsWeight, Completed=p.Completed, Category=p.Category)
        return super(self, p)