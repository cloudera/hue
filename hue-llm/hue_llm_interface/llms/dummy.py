def build(model_path):
    def infer(prompt):
        inferrance = f'Model: Dummy | Model Path: {model_path} | Prompt: {prompt}'
        return {
            "inferrance": inferrance
        }

    return infer
