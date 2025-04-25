import os
import all_import
from all_import import Llama

# Print working directory to help debug if needed
print("Current working directory:", os.getcwd())

# Load the model
llama3 = Llama(
    model_path="/Users/caesar/Desktop/makentu-v2v/models/Meta-Llama-3.1-8B-Instruct-Q8_0.gguf",  # full path to your model
    verbose=False,
    n_gpu_layers=-1,  # -1 = automatically use all GPU layers available
    n_ctx=16384,      # context window size
)

def generate_response(_model: Llama, _messages: str) -> str:
    """
    Generate a response from the Llama model based on input messages.
    """
    _output = _model.create_chat_completion(
        _messages,
        stop=["<|eot_id|>", "<|end_of_text|>"],
        max_tokens=512,
        temperature=0,
        repeat_penalty=2.0,
    )["choices"][0]["message"]["content"]
    return _output

# Example of using the model
if __name__ == "__main__":
    example_message = "Hello! Can you introduce yourself?"
    result = generate_response(llama3, example_message)
    print("Model Response:", result)
