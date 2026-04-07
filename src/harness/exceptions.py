"""
异常类定义
"""


class HarnessError(Exception):
    """Harness 基础异常"""
    pass


class LLMError(HarnessError):
    """LLM 调用异常"""
    pass


class PlannerError(HarnessError):
    """规划异常"""
    pass


class GeneratorError(HarnessError):
    """生成异常"""
    pass


class EvaluatorError(HarnessError):
    """评估异常"""
    pass


class SkillExtractionError(HarnessError):
    """技能提取异常"""
    pass


class ConfigurationError(HarnessError):
    """配置异常"""
    pass


class StateError(HarnessError):
    """状态管理异常"""
    pass


class GoldenRuleError(HarnessError):
    """黄金法则异常"""
    pass


class TemplateError(HarnessError):
    """模板异常"""
    pass


class ValidationError(HarnessError):
    """验证异常"""
    pass


class TimeoutError(HarnessError):
    """超时异常"""
    pass


class RetryExhaustedError(HarnessError):
    """重试次数耗尽异常"""
    def __init__(self, attempts: int, last_error: Exception):
        self.attempts = attempts
        self.last_error = last_error
        super().__init__(f"重试 {attempts} 次后仍失败: {last_error}")
