import importlib
import json
import os
import sys

modules = sys.argv[1:]
observations = []
for name in modules:
    before = "pyarrow" in sys.modules
    module = importlib.import_module(name)
    observations.append({"requested": name, "version": module.__version__, "arrow_already_loaded": before})
assert not any(name == "quantumbridge" or name.startswith("quantumbridge.") for name in sys.modules)
print(json.dumps({"modules": observations, "quantumbridge_imported": False,
    "arrow_pool_setting": os.environ.get("ARROW_DEFAULT_MEMORY_POOL"),
    "native_accepted": False}), flush=True)
