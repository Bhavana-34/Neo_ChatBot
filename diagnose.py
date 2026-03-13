#!/usr/bin/env python
import sys
import inspect
sys.path.insert(0, '.')

print("Importing models.llm...")
import models.llm as llm

print("\nAll attributes in models.llm:")
for name in sorted(dir(llm)):
    if not name.startswith('_'):
        obj = getattr(llm, name)
        if callable(obj):
            print(f"  Function: {name}")
        elif isinstance(obj, type):
            print(f"  Class: {name}")
        else:
            print(f"  Object: {name}")

print("\n=== Checking llm.py file directly ===")
with open('models/llm.py', 'r') as f:
    content = f.read()
    print(f"File size: {len(content)} bytes")
    print(f"Number of lines: {len(content.splitlines())}")
    
    # Count function definitions
    import re
    functions = re.findall(r'^def\s+(\w+)', content, re.MULTILINE)
    print(f"Functions defined: {functions}")
