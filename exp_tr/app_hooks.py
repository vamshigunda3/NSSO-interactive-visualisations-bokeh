from . import d_files
import os
print("you came to hooks")
def on_server_loaded(server_context):
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    print("in server loaded",os.getcwd())
    d_files.update_data()
