from abc import ABC, abstractmethod
from typing import Dict, List, Any

class BaseTest(ABC):
    def __init__(self):
        self.steps = []
        self.test_data_dir = None
        
    def log_step(self, step_name: str, status: str, message: str = "", data: Any = None):
        self.steps.append({
            "step_name": step_name,
            "status": status,
            "message": message,
            "data": data
        })
    
    def get_steps(self) -> List[Dict]:
        return self.steps
    
    @abstractmethod
    def get_test_name(self) -> str:
        pass
    
    @abstractmethod
    def get_test_description(self) -> str:
        pass
    
    @abstractmethod
    def run(self) -> Dict:
        pass
