from llama_cpp import Llama

def build(model_path):
    llm = Llama(model_path)

    def infer(prompt):
        response = llm(prompt, max_tokens=100, stop=["Q:", "\n"])
        inference = response["choices"][0]["text"]
        inference = inference.strip()
        return {
            "inference": inference
        }

    return infer
