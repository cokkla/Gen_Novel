import time

from AIGN_Prompt import *


# # 装饰器函数，发生异常时重试
# def Retryer(func, max_retries=10):
#     def wrapper(*args, **kwargs):
#         for _ in range(max_retries):
#             try:
#                 return func(*args, **kwargs)
#             except Exception as e:
#                 print("-" * 30 + f"\n失败：\n{e}\n" + "-" * 30)
#                 time.sleep(2.333)
#         raise ValueError("失败")
#
#     return wrapper


class MarkdownAgent:
    """处理与AI模型的交互，生成或处理Markdown格式的内容"""

    def __init__(
            self,
            chatLLM,
            sys_prompt: str,
            name: str,
            temperature=0.8,
            top_p=0.8,
            use_memory=False,
            first_replay="明白了。",
            # first_replay=None,
            is_speak=True,
    ) -> None:

        self.chatLLM = chatLLM
        self.sys_prompt = sys_prompt
        self.temperature = temperature
        self.top_p = top_p
        self.use_memory = use_memory
        self.is_speak = is_speak

        self.history = [{"role": "user", "content": self.sys_prompt}]

        if first_replay:
            self.history.append({"role": "assistant", "content": first_replay})
        else:
            resp = chatLLM.chat(messages=self.history)
            self.history.append({"role": "assistant", "content": resp["content"]})

    # 根据输入查询回复
    def query(self, user_input: str) -> str:
        resp = self.chatLLM.chat(
            messages=self.history + [{"role": "user", "content": user_input}],
            temperature=self.temperature,
            top_p=self.top_p,
        )
        if self.use_memory:
            self.history.append({"role": "user", "content": user_input})
            self.history.append({"role": "assistant", "content": resp["content"]})

        return resp

    # 从生成的MD中提取结构化信息
    def getOutput(self, input_content: str, output_keys: list) -> dict:
        """解析类md格式中 # key 的内容，未解析全部output_keys中的key会报错"""
        resp = self.query(input_content)
        # output = resp["content"]

        # lines = output.split("\n")
        lines = resp.split("\n")
        sections = {}
        current_section = ""
        for line in lines:
            if line.startswith("# ") or line.startswith(" # "):
                # new key
                current_section = line[2:].strip()
                sections[current_section] = []
            else:
                # add content to current key
                if current_section:
                    sections[current_section].append(line.strip())
        for key in sections.keys():
            sections[key] = "\n".join(sections[key]).strip()

        for k in output_keys:
            if (k not in sections) or (len(sections[k]) == 0):
                # raise ValueError(f"fail to parse {k} in output:\n{output}\n\n")
                raise ValueError(f"fail to parse {k} in output:\n{resp}\n\n")

        return sections

    # 调用解析后的结果，如果启用了记忆则输出记录对话内容
    def invoke(self, inputs: dict, output_keys: list) -> dict:
        input_content = ""
        for k, v in inputs.items():
            if isinstance(v, str) and len(v) > 0:
                input_content += f"# {k}\n{v}\n\n"

        # result = Retryer(self.getOutput)(input_content, output_keys)
        result = self.getOutput(input_content, output_keys)

        return result

    # 清除记忆
    def clear_memory(self):
        if self.use_memory:
            self.history = self.history[:2]


# 生成管理小说的创作过程
class AIGN:
    def __init__(self, chatLLM):
        self.chatLLM = chatLLM
        self.is_first_save = True
        self.is_chapter_begin = True
        self.novel_title = ""
        self.chapter_titles = ""
        self.novel_outline = ""
        self.paragraph_list = []
        self.novel_content = ""
        self.writing_plan = ""
        self.temp_setting = ""
        self.writing_memory = ""
        self.no_memory_paragraph = ""
        self.user_idea = ""
        self.user_requriments = ""
        self.embellishment_idea = ""

        self.novel_outline_writer = MarkdownAgent(
            chatLLM=self.chatLLM,
            sys_prompt=novel_outline_writer_prompt,
            name="NovelOutlineWriter",
            temperature=0.98,
        )
        self.novel_title_writer = MarkdownAgent(
            chatLLM=self.chatLLM,
            sys_prompt=novel_name_title_prompt,
            name="NovelNameWriter",
            temperature=0.80,
        )
        self.novel_chaptertitles_writer = MarkdownAgent(
            chatLLM=self.chatLLM,
            sys_prompt=novel_chaptertitles_prompt,
            name="NovelchapterTitlesWriter",
            temperature=0.80,
        )
        self.novel_beginning_writer = MarkdownAgent(
            chatLLM=self.chatLLM,
            sys_prompt=novel_beginning_writer_prompt,
            name="NovelBeginningWriter",
            temperature=0.80,
        )
        self.novel_writer = MarkdownAgent(
            chatLLM=self.chatLLM,
            sys_prompt=novel_writer_prompt,
            name="NovelWriter",
            temperature=0.81,
        )
        self.novel_embellisher = MarkdownAgent(
            chatLLM=self.chatLLM,
            sys_prompt=novel_embellisher_prompt,
            name="NovelEmbellisher",
            temperature=0.92,
        )
        self.memory_maker = MarkdownAgent(
            chatLLM=self.chatLLM,
            sys_prompt=memory_maker_prompt,
            name="MemoryMaker",
            temperature=0.66,
        )

    # 更新内容
    def updateNovelContent(self):
        self.novel_content = ""
        for paragraph in self.paragraph_list:
            self.novel_content += f"{paragraph}\n\n"
        return self.novel_content

    # 生成大纲
    def genNovelOutline(self, user_idea=None):
        if user_idea:
            self.user_idea = user_idea
        resp = self.novel_outline_writer.invoke(
            inputs={"用户想法": self.user_idea},
            output_keys=["大纲"],
        )
        self.novel_outline = resp["大纲"]
        return self.novel_outline

    # 生成小说名
    def genNovelTitle(self):
        if not self.novel_outline:
            raise ValueError("请先生成大纲，再生成小说名称。")

        resp = self.novel_title_writer.invoke(
            inputs={"小说大纲": self.novel_outline},
            output_keys=["小说名"]
        )

        self.novel_title = resp["小说名"]
        return self.novel_title

    # 生成开头
    def genBeginning(self, user_requriments=None, embellishment_idea=None):
        if user_requriments:
            self.user_requriments = user_requriments
        if embellishment_idea:
            self.embellishment_idea = embellishment_idea

        resp = self.novel_beginning_writer.invoke(
            inputs={
                "用户想法": self.user_idea,
                "小说大纲": self.novel_outline,
                "用户要求": self.user_requriments,
            },
            output_keys=["开头", "计划", "临时设定"],
        )
        beginning = resp["开头"]
        self.writing_plan = resp["计划"]
        self.temp_setting = resp["临时设定"]

        resp = self.novel_embellisher.invoke(
            inputs={
                "大纲": self.novel_outline,
                "临时设定": self.temp_setting,
                "计划": self.writing_plan,
                "润色要求": self.embellishment_idea,
                "要润色的内容": beginning,
            },
            output_keys=["润色结果"],
        )
        beginning = resp["润色结果"]

        self.paragraph_list.append(beginning)
        self.updateNovelContent()

        return beginning

    # 生成章节目录
    def genChapterTitles(self, user_requirements=None, embellishment_idea=None):
        """根据大纲生成章节目录"""
        if user_requirements:
            self.user_requriments = user_requirements
        if embellishment_idea:
            self.embellishment_idea = embellishment_idea

        if not self.novel_outline:
            raise ValueError("请先生成大纲，再生成章节目录。")

        resp = self.novel_chaptertitles_writer.invoke(
            inputs={
                "用户要求": self.user_requriments,
                "小说大纲": self.novel_outline,
            },
            output_keys=["章节目录"]
        )

        self.chapter_titles = resp["章节目录"]
        return self.chapter_titles

    # 生成章节内容
    def genChapterContent(self, chapter_title, embellishment_idea=None):
        """生成一章的内容，并记录章节标题"""
        # 生成章节段落
        next_paragraph = self.genNextParagraph(chapter_title, embellishment_idea)

        # self.updateNovelContent()
        self.recordNovel(chapter_title, next_paragraph)

        return next_paragraph

    # 生成下一段
    def genNextParagraph(self, chapter_title, embellishment_idea=None):
        self.chapter_titles = chapter_title
        if embellishment_idea:
            self.embellishment_idea = embellishment_idea

        resp = self.novel_writer.invoke(
            inputs={
                "用户想法": self.user_idea,
                "大纲": self.novel_outline,
                "章节名": self.chapter_titles,
                "前文记忆": self.writing_memory,
                "临时设定": self.temp_setting,
                "计划": self.writing_plan,
                "上文内容": self.getLastParagraph(),
            },
            output_keys=["段落", "计划", "临时设定"],
        )
        next_paragraph = resp["段落"]
        next_writing_plan = resp["计划"]
        next_temp_setting = resp["临时设定"]

        resp = self.novel_embellisher.invoke(
            inputs={
                "大纲": self.novel_outline,
                "章节名": self.chapter_titles,
                "临时设定": next_temp_setting,
                "计划": next_writing_plan,
                "润色要求": embellishment_idea,
                "上文": self.getLastParagraph(),
                "要润色的内容": next_paragraph,
            },
            output_keys=["润色结果"],
        )
        next_paragraph = resp["润色结果"]

        self.paragraph_list.append(next_paragraph)
        self.writing_plan = next_writing_plan
        self.temp_setting = next_temp_setting

        self.no_memory_paragraph += f"\n{next_paragraph}"

        self.updateMemory()
        # self.updateNovelContent()
        # self.recordNovel()

        return next_paragraph

    # 获取最后一段
    def getLastParagraph(self, max_length=2000):
        last_paragraph = ""

        for i in range(0, len(self.paragraph_list)):
            if (len(last_paragraph) + len(self.paragraph_list[-1 - i])) < max_length:
                last_paragraph = self.paragraph_list[-1 - i] + "\n" + last_paragraph
            else:
                break
        return last_paragraph

    # # 将所有内容记录到MD中
    # def recordNovelDetail(self):
    #     record_content = ""
    #     record_content += f"# 大纲\n\n{self.novel_outline}\n\n"
    #     record_content += f"# 正文\n\n"
    #     record_content += self.novel_content
    #     record_content += f"# 记忆\n\n{self.writing_memory}\n\n"
    #     record_content += f"# 计划\n\n{self.writing_plan}\n\n"
    #     record_content += f"# 临时设定\n\n{self.temp_setting}\n\n"
    #
    #     with open("novel_record_detail.md", "w", encoding="utf-8") as f:
    #         f.write(record_content)

    def recordNovel(self, chapter_title=None, next_paragraph=None):
        record_content = ""

        if self.is_first_save:
            record_content += f"# {self.novel_title}\n"
            record_content += f"# 大纲\n\n{self.novel_outline}\n\n"
            record_content += f"# 正文\n\n"
            self.is_first_save = False

        record_content += f"{chapter_title}\n"
        record_content += f"{next_paragraph}\n\n"

        with open("novel.md", "a", encoding="utf-8") as f:
            f.write(record_content)

    # 更新记忆
    def updateMemory(self):
        if (len(self.no_memory_paragraph)) > 2000:
            resp = self.memory_maker.invoke(
                inputs={
                    "前文记忆": self.writing_memory,
                    "正文内容": self.no_memory_paragraph,
                },
                output_keys=["新的记忆"],
            )
            self.writing_memory = resp["新的记忆"]
            self.no_memory_paragraph = ""
