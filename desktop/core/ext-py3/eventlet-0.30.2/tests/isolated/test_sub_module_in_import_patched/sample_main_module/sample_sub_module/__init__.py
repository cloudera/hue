"""
This file is used together with sample_main_module/__init__.py to setup a
scenario where symbols are imported from sub modules. It is used to test that
pacher.import_patched can correctly patch such symbols.
"""
import socket


def function_use_socket():
    return socket
