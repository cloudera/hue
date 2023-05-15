from llama_cpp import Llama

def build(model_path):
    llm = Llama(model_path)

    def infer(payload):
        table_names = ", ".join(payload["table_names"])
        prompt = payload["prompt"]

        enriched_prompt = f'Given table names {table_names}. Q: Generate just one SQL query to return {prompt}. A:';
        inferrence = llm(enriched_prompt, max_tokens=100, stop=["Q:", "\n"])
        response = inferrence["choices"][0]["text"]
        return response.strip()

    return infer
