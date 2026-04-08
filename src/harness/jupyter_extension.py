"""
Jupyter Notebook 支持
"""
from IPython.core.magic import Magics, magics_class, line_magic, cell_magic
from IPython.display import HTML, JSON, display
import asyncio
from typing import Optional
import json


@magics_class
class HarnessMagics(Magics):
    """Harness Jupyter 魔法命令"""
    
    def __init__(self, shell):
        super().__init__(shell)
        self.harness = None
        self.output_format = "html"  # html, json, text
    
    @line_magic
    def harness_init(self, line):
        """初始化 Harness
        
        Usage:
            %harness_init
        """
        try:
            from harness import HarnessEngine
            
            self.harness = HarnessEngine()
            print("✅ Harness 初始化成功")
            
        except Exception as e:
            print(f"❌ 初始化失败: {e}")
    
    @line_magic
    def harness_config(self, line):
        """配置 Harness
        
        Usage:
            %harness_config output=html model=gpt-4
        """
        if not self.harness:
            print("❌ 请先运行 %harness_init")
            return
        
        # 解析配置
        parts = line.split()
        for part in parts:
            if "=" in part:
                key, value = part.split("=", 1)
                
                if key == "output":
                    self.output_format = value
                elif key == "model":
                    self.harness.config.llm_model = value
                else:
                    print(f"⚠️  未知配置: {key}")
        
        print(f"✅ 配置已更新: output={self.output_format}")
    
    @cell_magic
    def harness_generate(self, line, cell):
        """生成代码
        
        Usage:
            %%harness_generate
            创建一个 REST API
        """
        if not self.harness:
            print("❌ 请先运行 %harness_init")
            return
        
        # 运行生成
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            self.harness.run(cell.strip())
        )
        
        # 显示结果
        self._display_result(result)
    
    @cell_magic
    def harness_evaluate(self, line, cell):
        """评估代码
        
        Usage:
            %%harness_evaluate
            def hello():
                pass
        """
        if not self.harness:
            print("❌ 请先运行 %harness_init")
            return
        
        # 运行评估
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            self.harness.evaluate(cell.strip())
        )
        
        # 显示结果
        self._display_result(result)
    
    @line_magic
    def harness_cost(self, line):
        """查看成本
        
        Usage:
            %harness_cost
        """
        try:
            from harness.cost_tracker import create_cost_tracker
            
            tracker = create_cost_tracker()
            stats = tracker.get_stats()
            
            summary = stats["summary"]
            
            html = f"""
            <div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h3>💰 成本统计</h3>
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-top: 15px;">
                    <div>
                        <div style="font-size: 24px; color: #667eea; font-weight: bold;">${summary['total_cost']:.4f}</div>
                        <div style="color: #6c757d; font-size: 12px;">总成本</div>
                    </div>
                    <div>
                        <div style="font-size: 24px; color: #667eea; font-weight: bold;">{summary['total_tokens']:,}</div>
                        <div style="color: #6c757d; font-size: 12px;">总 Tokens</div>
                    </div>
                    <div>
                        <div style="font-size: 24px; color: #667eea; font-weight: bold;">{summary['total_calls']:,}</div>
                        <div style="color: #6c757d; font-size: 12px;">调用次数</div>
                    </div>
                    <div>
                        <div style="font-size: 24px; color: #667eea; font-weight: bold;">${summary['avg_cost_per_call']:.6f}</div>
                        <div style="color: #6c757d; font-size: 12px;">平均成本</div>
                    </div>
                </div>
            </div>
            """
            
            display(HTML(html))
            
        except Exception as e:
            print(f"❌ 获取成本失败: {e}")
    
    @line_magic
    def harness_agents(self, line):
        """查看 Agent 状态
        
        Usage:
            %harness_agents
        """
        try:
            from harness.web.agent_dashboard import orchestrator
            
            agents = list(orchestrator.agents.values())
            
            if not agents:
                print("ℹ️  暂无 Agent")
                return
            
            html = "<div style='background: white; padding: 20px; border-radius: 10px;'>"
            html += "<h3>🤖 Agent 状态</h3>"
            
            for agent in agents:
                status_color = {
                    "idle": "#6c757d",
                    "running": "#ffc107",
                    "completed": "#28a745",
                    "failed": "#dc3545"
                }.get(agent.status, "#6c757d")
                
                html += f"""
                <div style='border-left: 4px solid {status_color}; padding: 10px; margin: 10px 0; background: #f8f9fa;'>
                    <div style='display: flex; justify-content: space-between;'>
                        <strong>{agent.name}</strong>
                        <span style='background: {status_color}; color: white; padding: 2px 10px; border-radius: 10px; font-size: 12px;'>
                            {agent.status}
                        </span>
                    </div>
                    <div style='color: #6c757d; font-size: 12px; margin-top: 5px;'>
                        类型: {agent.type} | 效率: {agent.performance.get('efficiency', 0)*100:.0f}%
                    </div>
                </div>
                """
            
            html += "</div>"
            display(HTML(html))
            
        except Exception as e:
            print(f"❌ 获取 Agent 状态失败: {e}")
    
    @line_magic
    def harness_plot(self, line):
        """绘制成本图表
        
        Usage:
            %harness_plot
        """
        try:
            import plotly.graph_objects as go
            from plotly.subplots import make_subplots
            from harness.cost_tracker import create_cost_tracker
            
            tracker = create_cost_tracker()
            stats = tracker.get_stats()
            
            # 创建子图
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('提供商分布', '成本趋势', '模型使用', '成本分布'),
                specs=[[{'type':'pie'}, {'type':'scatter'}],
                       [{'type':'bar'}, {'type':'bar'}]]
            )
            
            # 提供商分布（饼图）
            by_provider = stats["by_provider"]
            fig.add_trace(
                go.Pie(
                    labels=list(by_provider.keys()),
                    values=[v["cost"] for v in by_provider.values()]
                ),
                row=1, col=1
            )
            
            # 成本趋势（折线图）
            by_date = stats["by_date"]
            dates = sorted(by_date.keys())
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=[by_date[d]["cost"] for d in dates],
                    mode='lines+markers'
                ),
                row=1, col=2
            )
            
            # 模型使用（条形图）
            by_model = stats["by_model"]
            fig.add_trace(
                go.Bar(
                    x=list(by_model.keys())[:5],
                    y=[v["cost"] for v in list(by_model.values())[:5]]
                ),
                row=2, col=1
            )
            
            # 成本分布（条形图）
            fig.add_trace(
                go.Bar(
                    x=['<$0.01', '$0.01-$0.10', '$0.10-$1.00', '>$1.00'],
                    y=[0, 0, 0, 0]  # 需要从 tracker 计算
                ),
                row=2, col=2
            )
            
            fig.update_layout(height=800, showlegend=False, title_text="Harness 成本分析")
            fig.show()
            
        except ImportError:
            print("⚠️  需要安装 plotly: pip install plotly")
        except Exception as e:
            print(f"❌ 绘图失败: {e}")
    
    def _display_result(self, result: dict):
        """显示结果"""
        if self.output_format == "html":
            html = self._format_html(result)
            display(HTML(html))
        elif self.output_format == "json":
            display(JSON(result))
        else:
            print(json.dumps(result, indent=2, ensure_ascii=False))
    
    def _format_html(self, result: dict) -> str:
        """格式化为 HTML"""
        status = result.get("status", "unknown")
        status_color = "#28a745" if status == "success" else "#dc3545"
        
        html = f"""
        <div style="background: white; padding: 20px; border-radius: 10px; margin: 10px 0;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h4 style="margin: 0;">执行结果</h4>
                <span style="background: {status_color}; color: white; padding: 4px 12px; border-radius: 12px;">
                    {status}
                </span>
            </div>
        """
        
        # 代码
        if "code" in result:
            html += f"""
            <div style="margin-top: 15px;">
                <strong>生成的代码:</strong>
                <pre style="background: #f8f9fa; padding: 15px; border-radius: 5px; overflow-x: auto;">
{result['code']}
                </pre>
            </div>
            """
        
        # 评估结果
        if "evaluation" in result:
            eval_data = result["evaluation"]
            score = eval_data.get("score", 0)
            score_color = "#28a745" if score >= 8 else "#ffc107" if score >= 6 else "#dc3545"
            
            html += f"""
            <div style="margin-top: 15px;">
                <strong>评估结果:</strong>
                <div style="margin-top: 10px;">
                    <span style="font-size: 32px; color: {score_color}; font-weight: bold;">{score}/10</span>
                </div>
                <div style="color: #6c757d; margin-top: 5px;">
                    {eval_data.get('summary', '')}
                </div>
            </div>
            """
        
        # 成本
        if "cost" in result:
            html += f"""
            <div style="margin-top: 15px; color: #6c757d; font-size: 12px;">
                💰 成本: ${result['cost']:.6f} | ⏱️ 耗时: {result.get('duration', 0):.2f}s
            </div>
            """
        
        html += "</div>"
        
        return html


# 注册魔法命令
def load_ipython_extension(ipython):
    """加载 Jupyter 扩展"""
    ipython.register_magics(HarnessMagics)
    print("✅ Harness Jupyter 扩展已加载")
    print("\n📖 可用命令:")
    print("  %harness_init           - 初始化 Harness")
    print("  %harness_config         - 配置参数")
    print("  %%harness_generate      - 生成代码")
    print("  %%harness_evaluate      - 评估代码")
    print("  %harness_cost           - 查看成本")
    print("  %harness_agents         - 查看 Agent")
    print("  %harness_plot           - 绘制图表")


def unload_ipython_extension(ipython):
    """卸载扩展"""
    pass
