import importlib
import inspect
from pathlib import Path
from typing import Dict, List
from test.test_case.base_test import BaseTest

class TestRunner:
    def __init__(self):
        self.test_data_dir = Path(__file__).parent / "data"
        self.test_case_dir = Path(__file__).parent / "test_case"
        self.test_classes = {}
        self._load_test_cases()
    
    def _load_test_cases(self):
        for test_file in self.test_case_dir.glob("test_case_*.py"):
            try:
                module_name = f"test.test_case.{test_file.stem}"
                module = importlib.import_module(module_name)
                
                for _, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and 
                        issubclass(obj, BaseTest) and 
                        obj != BaseTest):
                        try:
                            if module_name == "test.test_case.test_case_1_user_permissions":
                                test_instance = obj()
                            else:
                                test_instance = obj(self.test_data_dir)
                            
                            self.test_classes[module_name] = {
                                "class": obj,
                                "name": test_instance.get_test_name(),
                                "description": test_instance.get_test_description()
                            }
                        except Exception as e:
                            print(f"Lỗi khi khởi tạo test case {test_file.name}: {e}")
            except Exception as e:
                print(f"Lỗi khi load test case {test_file.name}: {e}")
    
    def get_available_tests(self) -> List[Dict]:
        tests = []
        for module_name, test_info in self.test_classes.items():
            tests.append({
                "module": module_name,
                "name": test_info["name"],
                "description": test_info["description"]
            })
        return sorted(tests, key=lambda x: x["name"])
    
    def run_test(self, module_name: str, test_actions: str = None) -> Dict:
        if module_name not in self.test_classes:
            return {
                "test_name": "Unknown Test",
                "passed": False,
                "message": f"Test case không tồn tại: {module_name}",
                "steps": []
            }
        
        test_class = self.test_classes[module_name]["class"]
        
        if module_name == "test.test_case.test_case_1_user_permissions":
            test_instance = test_class()
            if test_actions:
                test_instance.test_actions = test_actions
        else:
            test_instance = test_class(self.test_data_dir)
        
        return test_instance.run()
