from importlib import import_module

def inferrer_factory(model, model_path):
    mod = import_module(f'hue_llm_interface.llms.{model}', package=model)
    build_inferer = getattr(mod, 'build')

    return build_inferer(model_path)
