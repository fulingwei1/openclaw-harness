"""
向量搜索和代码嵌入系统
"""
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import json
import numpy as np
from pathlib import Path
import hashlib


@dataclass
class CodeSnippet:
    """代码片段"""
    id: str
    code: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "code": self.code,
            "metadata": self.metadata,
            "embedding": self.embedding
        }


class EmbeddingEngine:
    """嵌入引擎"""
    
    def __init__(self, model: str = "text-embedding-3-small", api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key
        self.cache: Dict[str, List[float]] = {}
    
    async def embed(self, text: str) -> List[float]:
        """生成文本嵌入向量"""
        # 检查缓存
        cache_key = hashlib.md5(text.encode()).hexdigest()
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            # 使用 OpenAI Embedding API
            from openai import AsyncOpenAI
            
            client = AsyncOpenAI(api_key=self.api_key)
            response = await client.embeddings.create(
                input=text,
                model=self.model
            )
            
            embedding = response.data[0].embedding
            self.cache[cache_key] = embedding
            return embedding
            
        except Exception as e:
            print(f"嵌入生成失败: {e}")
            # 返回空向量作为后备
            return [0.0] * 1536
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """批量生成嵌入"""
        tasks = [self.embed(text) for text in texts]
        return await asyncio.gather(*tasks)
    
    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """计算余弦相似度"""
        vec1_np = np.array(vec1)
        vec2_np = np.array(vec2)
        
        dot_product = np.dot(vec1_np, vec2_np)
        norm1 = np.linalg.norm(vec1_np)
        norm2 = np.linalg.norm(vec2_np)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))


class VectorStore:
    """向量存储"""
    
    def __init__(self, storage_path: str = "./vector_store"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.snippets: List[CodeSnippet] = []
        self.embedding_engine = EmbeddingEngine()
        
        # 加载已有数据
        self._load()
    
    async def add_code(
        self,
        code: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """添加代码片段"""
        # 生成 ID
        snippet_id = hashlib.sha256(code.encode()).hexdigest()[:16]
        
        # 生成嵌入
        embedding = await self.embedding_engine.embed(code)
        
        # 创建片段
        snippet = CodeSnippet(
            id=snippet_id,
            code=code,
            metadata=metadata or {},
            embedding=embedding
        )
        
        self.snippets.append(snippet)
        self._save()
        
        return snippet_id
    
    async def search(
        self,
        query: str,
        top_k: int = 5,
        threshold: float = 0.7
    ) -> List[Tuple[CodeSnippet, float]]:
        """搜索相似代码"""
        # 生成查询向量
        query_embedding = await self.embedding_engine.embed(query)
        
        # 计算相似度
        results = []
        for snippet in self.snippets:
            if snippet.embedding:
                similarity = EmbeddingEngine.cosine_similarity(
                    query_embedding,
                    snippet.embedding
                )
                if similarity >= threshold:
                    results.append((snippet, similarity))
        
        # 排序并返回 top_k
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    async def find_similar(
        self,
        code: str,
        top_k: int = 5,
        threshold: float = 0.8
    ) -> List[Tuple[CodeSnippet, float]]:
        """查找相似代码"""
        code_embedding = await self.embedding_engine.embed(code)
        
        results = []
        for snippet in self.snippets:
            if snippet.embedding and snippet.code != code:
                similarity = EmbeddingEngine.cosine_similarity(
                    code_embedding,
                    snippet.embedding
                )
                if similarity >= threshold:
                    results.append((snippet, similarity))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    def get_by_id(self, snippet_id: str) -> Optional[CodeSnippet]:
        """通过 ID 获取代码片段"""
        for snippet in self.snippets:
            if snippet.id == snippet_id:
                return snippet
        return None
    
    def delete(self, snippet_id: str) -> bool:
        """删除代码片段"""
        for i, snippet in enumerate(self.snippets):
            if snippet.id == snippet_id:
                del self.snippets[i]
                self._save()
                return True
        return False
    
    def clear(self):
        """清空所有数据"""
        self.snippets = []
        self._save()
    
    def _save(self):
        """保存到磁盘"""
        data_file = self.storage_path / "snippets.json"
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(
                [s.to_dict() for s in self.snippets],
                f,
                ensure_ascii=False,
                indent=2
            )
    
    def _load(self):
        """从磁盘加载"""
        data_file = self.storage_path / "snippets.json"
        if data_file.exists():
            try:
                with open(data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.snippets = [
                        CodeSnippet(**item) for item in data
                    ]
            except Exception as e:
                print(f"加载向量数据失败: {e}")
                self.snippets = []
    
    def stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "total_snippets": len(self.snippets),
            "storage_path": str(self.storage_path),
            "cache_size": len(self.embedding_engine.cache)
        }


class CodeIndexer:
    """代码索引器"""
    
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
    
    async def index_file(
        self,
        file_path: str,
        language: Optional[str] = None
    ) -> List[str]:
        """索引单个文件"""
        path = Path(file_path)
        if not path.exists():
            return []
        
        # 读取文件
        with open(path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # 检测语言
        if not language:
            language = self._detect_language(path.suffix)
        
        # 分割成片段（按函数/类）
        snippets = self._split_code(code, language)
        
        # 添加到向量存储
        snippet_ids = []
        for snippet_code in snippets:
            snippet_id = await self.vector_store.add_code(
                snippet_code,
                metadata={
                    "file": str(path),
                    "language": language,
                    "type": "code_snippet"
                }
            )
            snippet_ids.append(snippet_id)
        
        return snippet_ids
    
    async def index_directory(
        self,
        dir_path: str,
        extensions: List[str] = None,
        exclude_dirs: List[str] = None
    ) -> Dict[str, int]:
        """索引整个目录"""
        if extensions is None:
            extensions = ['.py', '.js', '.ts', '.java', '.go', '.rs']
        
        if exclude_dirs is None:
            exclude_dirs = ['node_modules', '__pycache__', '.git', 'venv']
        
        dir_path = Path(dir_path)
        stats = {"total_files": 0, "total_snippets": 0}
        
        for file_path in dir_path.rglob('*'):
            # 检查排除目录
            if any(excluded in file_path.parts for excluded in exclude_dirs):
                continue
            
            # 检查扩展名
            if file_path.suffix not in extensions:
                continue
            
            # 索引文件
            snippet_ids = await self.index_file(str(file_path))
            stats["total_files"] += 1
            stats["total_snippets"] += len(snippet_ids)
        
        return stats
    
    def _detect_language(self, suffix: str) -> str:
        """检测编程语言"""
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.go': 'go',
            '.rs': 'rust',
            '.cpp': 'cpp',
            '.c': 'c',
            '.rb': 'ruby',
            '.php': 'php'
        }
        return language_map.get(suffix, 'unknown')
    
    def _split_code(self, code: str, language: str) -> List[str]:
        """分割代码为片段"""
        if language == 'python':
            return self._split_python(code)
        elif language in ['javascript', 'typescript']:
            return self._split_js(code)
        else:
            # 简单按空行分割
            return [s.strip() for s in code.split('\n\n') if s.strip()]
    
    def _split_python(self, code: str) -> List[str]:
        """分割 Python 代码"""
        import re
        
        # 匹配函数和类定义
        pattern = r'((?:def |class |async def ).*?)(?=\n(?:def |class |async def |$))'
        matches = re.findall(pattern, code, re.DOTALL)
        
        return [m.strip() for m in matches if m.strip()]
    
    def _split_js(self, code: str) -> List[str]:
        """分割 JavaScript/TypeScript 代码"""
        import re
        
        # 匹配函数和类定义
        pattern = r'((?:function |const |class ).*?)(?=\n(?:function |const |class |$))'
        matches = re.findall(pattern, code, re.DOTALL)
        
        return [m.strip() for m in matches if m.strip()]


# 便捷函数
def create_vector_store(storage_path: str = "./vector_store") -> VectorStore:
    """创建向量存储"""
    return VectorStore(storage_path)


def create_code_indexer(vector_store: VectorStore) -> CodeIndexer:
    """创建代码索引器"""
    return CodeIndexer(vector_store)
