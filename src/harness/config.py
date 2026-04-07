"""
配置模型
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, field_validator
from pathlib import Path


class LLMConfig(BaseModel):
    """LLM 配置"""
    provider: str = Field(default="openai", description="LLM 提供商")
    model: str = Field(default="gpt-4", description="模型名称")
    api_key: Optional[str] = Field(default=None, description="API Key")
    base_url: Optional[str] = Field(default=None, description="自定义 API URL")
    temperature: float = Field(default=0.7, ge=0, le=2, description="温度参数")
    max_tokens: int = Field(default=4096, gt=0, description="最大 token 数")
    timeout: int = Field(default=60, gt=0, description="超时时间（秒）")
    retry_attempts: int = Field(default=3, ge=0, le=10, description="重试次数")

    @field_validator('provider')
    @classmethod
    def validate_provider(cls, v: str) -> str:
        allowed = ['openai', 'anthropic', 'zai', 'kimi', 'minimax', 'custom']
        if v not in allowed:
            raise ValueError(f"不支持的提供商: {v}，支持的提供商: {allowed}")
        return v


class EvaluatorConfig(BaseModel):
    """评估器配置"""
    pass_threshold: float = Field(default=0.8, ge=0, le=1, description="通过阈值")
    max_retries: int = Field(default=3, ge=0, le=10, description="最大重试次数")
    evaluation_criteria: List[str] = Field(
        default_factory=lambda: ["correctness", "completeness", "clarity"],
        description="评估标准"
    )


class SkillExtractorConfig(BaseModel):
    """技能提取器配置"""
    enabled: bool = Field(default=True, description="是否启用自动提取")
    min_score: float = Field(default=0.8, ge=0, le=1, description="最低评分要求")
    output_dir: str = Field(default=".harness/skills", description="输出目录")


class HarnessConfig(BaseModel):
    """Harness 主配置"""
    llm: LLMConfig = Field(default_factory=LLMConfig)
    evaluator: EvaluatorConfig = Field(default_factory=EvaluatorConfig)
    skill_extractor: SkillExtractorConfig = Field(default_factory=SkillExtractorConfig)
    harness_dir: str = Field(default=".harness", description="Harness 目录")
    log_level: str = Field(default="INFO", description="日志级别")
    log_file: Optional[str] = Field(default=None, description="日志文件路径")

    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        allowed = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        v_upper = v.upper()
        if v_upper not in allowed:
            raise ValueError(f"不支持的日志级别: {v}，支持的级别: {allowed}")
        return v_upper

    @classmethod
    def from_file(cls, config_file: str = "harness.yaml") -> 'HarnessConfig':
        """从文件加载配置"""
        import yaml
        from pathlib import Path
        
        config_path = Path(config_file)
        if not config_path.exists():
            return cls()  # 返回默认配置
        
        with open(config_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
        
        return cls(**data)

    def to_file(self, config_file: str = "harness.yaml"):
        """保存配置到文件"""
        import yaml
        from pathlib import Path
        
        config_path = Path(config_file)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.model_dump(), f, allow_unicode=True, default_flow_style=False)
