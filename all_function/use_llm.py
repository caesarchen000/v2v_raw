import os
import all_import
import json
from all_import import Llama
from llama_cpp import Llama
from pathlib import Path

model_name = "Meta-Llama-3.1-8B-Instruct-Q8_0"  # 升級模型
cache_dir = "./models"

# Print working directory to help debug if needed
print("Current working directory:", os.getcwd())

# Load the model
llama3 = Llama(
    model_path = "/Users/caesar/Desktop/makentu-v2v/models/Meta-Llama-3.1-8B-Instruct-Q8_0.gguf",
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


class LLMAgent():
    def __init__(self, role_description: str, task_description: str, llm:str="bartowski/Meta-Llama-3.1-8B-Instruct-GGUF",temperature=0,max_tokens=512, verbose=False):
        self.role_description = role_description   # Role means who this agent should act like. e.g. the history expert, the manager......
        self.task_description = task_description    # Task description instructs what task should this agent solve.
        self.temperature=temperature
        self.verbose=verbose
        self.max_tokens=max_tokens
        self.llm = llm  # LLM indicates which LLM backend this agent is using.
    def inference(self, message:str) -> str:
        if self.llm == 'bartowski/Meta-Llama-3.1-8B-Instruct-GGUF': # If using the default one.
            # TODO: Design the system prompt and user prompt here.
            # Format the messsages first.
            if self.verbose:
              print(f" Agent Role {self.role_description}")
              print(f" Tasks: {self.task_description}")
              print(f" User message: {message}")
            messages = [
                {"role": "system", "content": f"你的角色：{self.role_description}，請用繁體中文回答"},  # Hint: you may want the agents to speak Traditional Chinese only.
                {"role": "user", "content": f"你的任務：{self.task_description}\n 訊息，資料：{message}"}, # Hint: you may want the agents to clearly distinguish the task descriptions and the user messages. A proper seperation text rather than a simple line break is recommended.
            ]
            return generate_response(llama3, messages)
        


keyword_extraction_agent = LLMAgent(
    role_description="你是個專門提取關鍵字的AI，負責從問題中找出使用者想要對話的目標對象車牌號碼、使用者想要傳達的訊息，並將這些資訊整理成.json格式",
    task_description="""
                        1. 請從以下問題中取出目標對象車牌號碼、使用者想要傳達的訊息
                        2. 若你判斷無法從問題中取出這些資訊，則將輸出的"correctness"設為"0"，否則設為"1"
                        3. 若你判斷問題中有多個目標對象車牌號碼、使用者想要傳達的訊息，則將輸出的"correctness"設為"0"
                        4. 整理的結果請將結果整理成list格式
                        5. 關鍵字中必須要有correctness、目標對象車牌號碼、使用者想要傳達的訊息
                        6. 關鍵字產出順序需依照correcness、目標對象車牌號碼、使用者想要傳達的訊息產出
                        7. Jlist格式範例：["0", "車牌號碼","想超車"]
                        8. correctness的值為"0"或"1"
                        9. 車牌號碼的格式為"ABC-1234"或"1234-ABC"，請注意區分
                        10. 傳達訊息的部分請用繁體中文回答
                     """,
    verbose=False
)

async def pipeline(question: str) -> None:
    extracted_keywords = keyword_extraction_agent.inference(question)
    print(f"Extracted keywords: {extracted_keywords}")

    # Convert the extracted keywords into a list (split by 頓號)
    keyword_list = [kw.strip() for kw in extracted_keywords.split('、') if kw.strip()]

    # Create a dictionary
    output_json = {
        "correctness": keyword_list[0],
        "車牌號碼": keyword_list[1] if len(keyword_list) > 1 else "none",
        "傳達訊息": keyword_list[2] if len(keyword_list) > 2 else "none",
    }

    # Define output path
    output_path = Path("output_keywords.json")

    # Save to JSON file
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_json, f, ensure_ascii=False, indent=4)

# Example of using the model
if __name__ == "__main__":
    example_message = "Hello! Can you introduce yourself?"
    result = generate_response(llama3, example_message)
    print("Model Response:", result)
