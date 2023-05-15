def build(model_path):
    def infer(prompt):
        return f'Model: {model_path} | Prompt: {prompt}'

    return infer
