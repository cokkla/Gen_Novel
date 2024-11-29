import time
from AIGN import AIGN
from LLM import ChatLLM


class NovelGenerator():
    def __init__(self, aign):
        self.aign = aign
        self.novel = ""
        self.history = []

    def generate_outline(self, user_idea):
        """生成大纲"""
        print("生成小说大纲...")
        outline = self.aign.genNovelOutline(user_idea)
        print(f"大纲生成完成：\n{outline}")
        return outline

    def generate_title(self):
        """生成小说名"""
        print("生成小说名...")
        title = self.aign.genNovelTitle()
        print(f"小说名生成完成：\n{title}")
        return title

    def generate_chaptertitles(self, user_requirements):
        """生成章节目录"""
        print("生成章节目录...")
        chapter_titles = self.aign.genChapterTitles(user_requirements)
        print(f"章节目录生成完成：\n{chapter_titles}")
        chapter_titles = chapter_titles.split("\n")
        return chapter_titles

    def generate_chapter(self, chapter_titles, embellishment_idea=None):
        """生成每一章的内容"""
        for title in chapter_titles:
            print(f"生成章节{title}的内容")
            chapter_content = self.aign.genChapterContent(title, embellishment_idea)
            time.sleep(1)  # 为了避免过快调用模型，适当延迟
            print(f"章节{title}内容生成完成：{chapter_content[:100]}...")
        return chapter_content

    def generate_novel(self, user_idea, user_requirements=None, embellishment_idea=None):
        """生成小说"""
        self.generate_outline(user_idea)
        self.generate_title()
        chapter_titles = self.generate_chaptertitles(user_requirements)
        self.generate_chapter(chapter_titles, embellishment_idea)


if __name__ == "__main__":
    user_idea = "主角独自一人在异世界冒险，它爆种时会大喊一句：原神，启动！！！"
    user_requirements = "要有深度的角色塑造，情节紧凑，带有冒险和奇幻元素"

    # 初始化 ChatLLM 和 AIGN
    chat_llm = ChatLLM()
    aign = AIGN(chat_llm)

    generator = NovelGenerator(aign)
    novel = generator.generate_novel(user_idea, user_requirements)

    with open("generated_novel.txt", "w", encoding="utf-8") as f:
        f.write(novel)
    print("小说保存为 generated_novel.txt")
