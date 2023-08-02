from transformers import pipeline, AutoTokenizer

model="gpt2"

tokenizer = AutoTokenizer.from_pretrained(model)
pipe = pipeline("text-generation", model=model)

prompt = "Hello, I'm a language model."

response = pipe(
    prompt,
    max_new_tokens=100,
    pad_token_id=tokenizer.eos_token_id,
    return_full_text=False,
)

print(response)
