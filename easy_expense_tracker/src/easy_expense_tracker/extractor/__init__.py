import importlib

def get_extractor(template_name, path):
    module = importlib.import_module('.' + template_name, package=__package__)
    if hasattr(module, 'extract'):
        module.path = path
        return getattr(module, 'extract')

