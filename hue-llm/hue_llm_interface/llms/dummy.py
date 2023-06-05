def build(model_path):
    def infer(prompt):
        inference = f'Model: Dummy | Model Path: {model_path} | Prompt: {prompt}'
        return {
            "inference": inference
        }

    return infer
