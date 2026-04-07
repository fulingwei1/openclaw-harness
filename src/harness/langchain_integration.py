"""
LangChain 集成 - 工作流和工具链
"""
import asyncio
from typing import Dict, List, Any, Optional, Sequence
from dataclasses import dataclass
from langchain_core.tools import BaseTool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from pydantic import Field
import json


@dataclass
class ToolResult:
    """工具执行结果"""
    success: bool
    output: str
    metadata: Dict[str, Any] = None


class CodeGeneratorTool(BaseTool):
    """代码生成工具"""
    name: str = "code_generator"
    description: str = "生成代码片段，输入任务描述，输出代码"
    
    llm_client: Any = Field(default=None, exclude=True)
    
    def __init__(self, llm_client=None):
        super().__init__()
        self.llm_client = llm_client
    
    def _run(self, task: str) -> str:
        """同步执行"""
        return asyncio.run(self._arun(task))
    
    async def _arun(self, task: str) -> str:
        """异步执行"""
        # 这里调用 harness 的 Generator
        from ..generator import Generator
        from ..llm import LLMClient
        
        if not self.llm_client:
            self.llm_client = LLMClient()
        
        generator = Generator(self.llm_client)
        result = await generator.generate(task, [])
        
        return result.code


class CodeEvaluatorTool(BaseTool):
    """代码评估工具"""
    name: str = "code_evaluator"
    description: str = "评估代码质量，输入代码和任务，输出评分和建议"
    
    llm_client: Any = Field(default=None, exclude=True)
    
    def __init__(self, llm_client=None):
        super().__init__()
        self.llm_client = llm_client
    
    def _run(self, code: str, task: str) -> str:
        """同步执行"""
        return asyncio.run(self._arun(code, task))
    
    async def _arun(self, code: str, task: str) -> str:
        """异步执行"""
        from ..evaluator import Evaluator
        from ..llm import LLMClient
        
        if not self.llm_client:
            self.llm_client = LLMClient()
        
        evaluator = Evaluator(self.llm_client)
        result = await evaluator.evaluate(code, task)
        
        return json.dumps({
            "score": result.score,
            "passed": result.passed,
            "feedback": result.feedback
        })


class CodeSearchTool(BaseTool):
    """代码搜索工具"""
    name: str = "code_search"
    description: str = "搜索相似代码，输入查询，输出相关代码片段"
    
    vector_store: Any = Field(default=None, exclude=True)
    
    def __init__(self, vector_store=None):
        super().__init__()
        self.vector_store = vector_store
    
    def _run(self, query: str) -> str:
        """同步执行"""
        return asyncio.run(self._arun(query))
    
    async def _arun(self, query: str) -> str:
        """异步执行"""
        if not self.vector_store:
            from ..vectors import create_vector_store
            self.vector_store = create_vector_store()
        
        results = await self.vector_store.search(query, top_k=5)
        
        if not results:
            return "未找到相关代码"
        
        # 格式化输出
        output_lines = []
        for snippet, score in results:
            output_lines.append(
                f"[相似度: {score:.2f}]\n{snippet.code}\n"
            )
        
        return "\n---\n".join(output_lines)


class LangChainHarness:
    """LangChain Harness 集成"""
    
    def __init__(
        self,
        provider: str = "openai",
        model: str = "gpt-4",
        api_key: Optional[str] = None
    ):
        self.provider = provider
        self.model = model
        self.api_key = api_key
        
        # 初始化 LLM
        self.llm = self._create_llm()
        
        # 工具集合
        self.tools: List[BaseTool] = []
        
        # 链集合
        self.chains: Dict[str, Any] = {}
    
    def _create_llm(self):
        """创建 LLM"""
        if self.provider == "openai":
            return ChatOpenAI(
                model=self.model,
                api_key=self.api_key,
                temperature=0.7
            )
        elif self.provider == "anthropic":
            return ChatAnthropic(
                model=self.model,
                api_key=self.api_key,
                temperature=0.7
            )
        else:
            raise ValueError(f"不支持的提供商: {self.provider}")
    
    def register_tool(self, tool: BaseTool):
        """注册工具"""
        self.tools.append(tool)
    
    def create_chain(
        self,
        chain_name: str,
        prompt_template: str,
        output_parser=None
    ):
        """创建链"""
        prompt = ChatPromptTemplate.from_template(prompt_template)
        parser = output_parser or StrOutputParser()
        
        chain = prompt | self.llm | parser
        self.chains[chain_name] = chain
        
        return chain
    
    async def run_chain(
        self,
        chain_name: str,
        inputs: Dict[str, Any]
    ) -> Any:
        """运行链"""
        if chain_name not in self.chains:
            raise ValueError(f"链不存在: {chain_name}")
        
        chain = self.chains[chain_name]
        
        # 判断是否是异步链
        if hasattr(chain, "ainvoke"):
            return await chain.ainvoke(inputs)
        else:
            return chain.invoke(inputs)
    
    async def run_with_tools(
        self,
        task: str,
        tool_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """使用工具运行任务"""
        from langchain.agents import AgentExecutor, create_openai_functions_agent
        
        # 过滤工具
        tools = (
            [t for t in self.tools if t.name in tool_names]
            if tool_names
            else self.tools
        )
        
        if not tools:
            # 直接用 LLM
            result = await self.llm.ainvoke(task)
            return {"output": result.content}
        
        # 创建 Agent
        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个代码助手，使用工具完成任务"),
            ("user", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])
        
        agent = create_openai_functions_agent(self.llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools)
        
        # 执行
        result = await agent_executor.ainvoke({"input": task})
        
        return result
    
    def create_code_generation_chain(self):
        """创建代码生成链"""
        template = """你是一个专业的代码生成助手。

任务：{task}

约束条件：
- 语言：{language}
- 框架：{framework}
- 代码风格：{style}

请生成符合要求的代码：
"""
        return self.create_chain("code_generation", template)
    
    def create_code_review_chain(self):
        """创建代码审查链"""
        template = """请审查以下代码：

```{language}
{code}
```

审查要点：
1. 代码质量
2. 潜在bug
3. 性能问题
4. 安全隐患
5. 最佳实践

请给出详细的审查报告：
"""
        return self.create_chain("code_review", template)
    
    def create_refactor_chain(self):
        """创建重构链"""
        template = """请重构以下代码：

```{language}
{code}
```

重构目标：
- 提高可读性
- 优化性能
- 遵循最佳实践
- 保持功能不变

请输出重构后的代码和改进说明：
"""
        return self.create_chain("refactor", template)


# 预定义工作流
class Workflows:
    """预定义工作流"""
    
    @staticmethod
    def create_full_development_workflow() -> LangChainHarness:
        """创建完整开发工作流"""
        harness = LangChainHarness()
        
        # 注册工具
        harness.register_tool(CodeGeneratorTool())
        harness.register_tool(CodeEvaluatorTool())
        harness.register_tool(CodeSearchTool())
        
        # 创建链
        harness.create_code_generation_chain()
        harness.create_code_review_chain()
        harness.create_refactor_chain()
        
        return harness
    
    @staticmethod
    async def generate_and_review(
        task: str,
        language: str = "python"
    ) -> Dict[str, str]:
        """生成并审查代码"""
        harness = Workflows.create_full_development_workflow()
        
        # 生成代码
        code = await harness.run_chain(
            "code_generation",
            {"task": task, "language": language, "framework": "", "style": "clean"}
        )
        
        # 审查代码
        review = await harness.run_chain(
            "code_review",
            {"code": code, "language": language}
        )
        
        return {
            "code": code,
            "review": review
        }
    
    @staticmethod
    async def search_and_adapt(
        query: str,
        adaptation_requirements: str
    ) -> str:
        """搜索并改编代码"""
        harness = Workflows.create_full_development_workflow()
        
        # 搜索相似代码
        search_tool = CodeSearchTool()
        similar_code = await search_tool._arun(query)
        
        # 改编代码
        adapted_code = await harness.run_chain(
            "refactor",
            {"code": similar_code, "language": "python"}
        )
        
        return adapted_code


# 便捷函数
def create_langchain_harness(
    provider: str = "openai",
    model: str = "gpt-4",
    api_key: Optional[str] = None
) -> LangChainHarness:
    """创建 LangChain Harness"""
    return LangChainHarness(provider, model, api_key)


def create_tool_enabled_harness() -> LangChainHarness:
    """创建带工具的 Harness"""
    harness = create_langchain_harness()
    
    # 注册默认工具
    harness.register_tool(CodeGeneratorTool())
    harness.register_tool(CodeEvaluatorTool())
    harness.register_tool(CodeSearchTool())
    
    return harness
