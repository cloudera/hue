from llama_cpp import Llama

def build(model_path):
    llm = Llama(model_path)

    def infer(prompt):
        inferrence = llm(prompt, max_tokens=100, stop=["Q:", "\n"])
        response = inferrence["choices"][0]["text"]
        inferrance = response.strip()
        return {
            "inferrance": inferrance
        }

    return infer
