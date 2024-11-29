from AIGN import AIGN
from LLM import ChatLLM
from gen_Novel import NovelGenerator

user_idea = "写一本游戏相关题材的短小说，以《黑神话悟空》背景为例，实现《西游记》的重构暗黑版本，加入游戏元素，要有深度的角色塑造，情节紧凑，带有冒险和奇幻元素"
user_requirements = "生成20章左右，这些章需要概括小说的所有内容"

chat_llm = ChatLLM()
aign = AIGN(chat_llm)
generator = NovelGenerator(aign)
novel = generator.generate_novel(user_idea, user_requirements)
