from openai import OpenAI

api_key = "替换为自己的api"

class ChatLLM:
    def __init__(self, model_name="qwen-long"):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        self.model_name = model_name

    def chat(self, messages, temperature=0.8, top_p=0.8):
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=temperature,
            top_p=top_p,
        )

        return response.choices[0].message.content


if __name__ == "__main__":
    prompt = "请用一句话介绍自己"
    messages = [{"role": "user", "content": prompt}]
    # chat_lmm(prompt)

    chatLLM = ChatLLM()
    print(chatLLM.chat(messages))

    # for resp in chatLLM.chat(messages):
    #     print(resp)
