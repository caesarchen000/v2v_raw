import os
import all_import
import json
import asyncio
from all_import import Llama
from llama_cpp import Llama
from pathlib import Path


# Print working directory to help debug if needed
print("Current working directory:", os.getcwd())

# Load the model
llama3 = Llama(
    model_path = "/home/caesar/Desktop/v2v_raw/models/meta-llama-3.1-8b-instruct-q8_0.gguf",
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
                        1. 請從以下對話中取出這段對話來自哪個車牌號碼、目標對象車牌號碼、使用者想要傳達的訊息
                        2. 若你判斷無法從問題中取出這些資訊，則將輸出的"correctness"設為"0"，否則設為"1"
                        3. 若你判斷問題中有多個目標對象車牌號碼、多個來自哪個車牌號碼、使用者想要傳達的訊息，則將輸出的"correctness"設為"0"
                        4. 整理的結果請將結果整理成list格式
                        5. 關鍵字中必須要有correctness、目標對象車牌號碼、使用者想要傳達的訊息
                        6. 關鍵字產出順序需依照correctness、目標對象車牌號碼、使用者想要傳達的訊息產出
                        7. Jlist格式範例：["0", "來自的車牌號碼","傳給的車牌號碼","想超車"]
                        8. correctness的值為"0"或"1"
                        9. 車牌號碼的格式為"ABC-1234"或"1234-ABC"，請注意區分
                        10. 傳達訊息的部分請用繁體中文回答
                        11. 若你接收到的文字有不雅的語言請將其過濾掉，並用比較中性的語言來表達
                     """,
    verbose=False
)

json_to_txt_agent = LLMAgent(
    role_description="你是個專門將給你的資料換句話說的AI，負責將條列式的資料轉換成繁體中文的對話",
    task_description="""
                        1. 請根據以下資料，幫我用繁體中文整理成一段跟駕駛者講的話
                        2. 整理的結果請將結果整理成txt格式
                        3. 關鍵字中必須要有(1)訊息來自的車牌號碼(2)使用者想要傳達的訊息
                        4. 關鍵字產出順序需依照訊息來自的車牌號碼、使用者想要傳達的訊息產出
                        5. 我會給你：(來自的車牌號碼、傳給的車牌號碼、傳達訊息)
                        6. 傳達訊息的部分請用繁體中文回答
                     """,
    verbose=False
)

async def txt_to_json_pipeline(request: str) -> None:
    extracted_keywords = keyword_extraction_agent.inference(request)
    print(f"Extracted keywords: {extracted_keywords}")

    # Convert the extracted keywords into a list (split by 頓號)
    keyword_list = [kw.strip() for kw in extracted_keywords.split('、') if kw.strip()]

    # Create a dictionary
    txt_to_json = {
        "correctness": keyword_list[0],
        "來自的車牌號碼": keyword_list[1] if len(keyword_list) > 1 else "none",
        "傳給的車牌號碼": keyword_list[2] if len(keyword_list) > 2 else "none",
        "傳達訊息": keyword_list[3] if len(keyword_list) > 3 else "none",
    }

    # Define output path
    output_path = Path("txt_to_json.json")

    # Save to JSON file
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(txt_to_json, f, ensure_ascii=False, indent=4)


async def json_to_txt_pipeline(json_file_path: str) -> None:

    with open(json_file_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    formatted_message = f"""
    1. 來自的車牌號碼：{json_data.get("來自的車牌號碼", "none")}
    2. 傳給的車牌號碼：{json_data.get("傳給的車牌號碼", "none")}
    3. 傳達訊息：{json_data.get("傳達訊息", "none")}
    """
    reconstructed_message = json_to_txt_agent.inference(formatted_message)
    output_path = Path("json_to_txt.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(formatted_message)
