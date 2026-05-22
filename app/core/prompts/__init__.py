"""
提示词模块
集中管理所有 AI 提示词模板及敏感词黑名单
"""
import json
from pathlib import Path
from typing import Optional, List


class PromptLoader:
    """提示词加载器"""
    
    _prompts_cache = {}
    
    @classmethod
    def load_prompt(cls, prompt_name: str, cache: bool = True) -> str:
        """
        加载提示词文件
        
        Args:
            prompt_name: 提示词文件名（不含 .md 后缀）
            cache: 是否缓存提示词内容
            
        Returns:
            提示词内容字符串
        """
        # 检查缓存
        if cache and prompt_name in cls._prompts_cache:
            return cls._prompts_cache[prompt_name]
        
        # 构建文件路径
        prompts_dir = Path(__file__).parent
        prompt_file = prompts_dir / f"{prompt_name}.md"
        
        if not prompt_file.exists():
            raise FileNotFoundError(f"提示词文件不存在: {prompt_file}")
        
        # 读取文件
        with open(prompt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 缓存
        if cache:
            cls._prompts_cache[prompt_name] = content
        
        return content
    
    @classmethod
    def clear_cache(cls):
        """清空提示词及敏感词缓存"""
        cls._prompts_cache.clear()
        cls._sensitive_words_cache = None
        cls._sensitive_words_regex = None


# 便捷函数
def load_ai_audit_prompt() -> str:
    """加载 AI 文案审核系统提示词"""
    return PromptLoader.load_prompt("ai_audit_system")


def load_sensitive_lexicon() -> List[str]:
    """
    加载敏感词黑名单
    
    Returns:
        敏感词列表
    """
    # 缓存键
    cache_key = "__sensitive_lexicon__"
    if cache_key in PromptLoader._prompts_cache:
        return PromptLoader._prompts_cache[cache_key]
    
    lexicon_file = Path(__file__).parent / "SensitiveLexicon.json"
    if not lexicon_file.exists():
        print(f"⚠️  敏感词黑名单文件不存在: {lexicon_file}")
        return []
    
    with open(lexicon_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    words = data.get("words", [])
    PromptLoader._prompts_cache[cache_key] = words
    return words
