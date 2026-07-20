import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from system_control import SystemController

sc = SystemController()

print("Testing: ADJUST_VOLUME +20%")
result = sc.execute_task("ADJUST_VOLUME", {"percentage_change": 20})
print(f"Status : {result['status']}")
print(f"Message: {result['message']}")
