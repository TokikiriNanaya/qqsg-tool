"""拼音搜索工具模块"""
from pypinyin import pinyin, Style


def get_pinyin_initials(name: str) -> str:
    """获取字符串的拼音首字母（小写）。
    
    例如: "钙化大骨" -> "ghdg"
    """
    if not name:
        return ""
    result = pinyin(name, style=Style.FIRST_LETTER, errors='default')
    return ''.join(item[0] for item in result).lower()


def get_pinyin_full(name: str) -> str:
    """获取字符串的完整拼音（小写，无空格）。
    
    例如: "钙化大骨" -> "gaihuadagu"
    """
    if not name:
        return ""
    result = pinyin(name, style=Style.NORMAL, errors='default')
    return ''.join(item[0] for item in result).lower()


def match_pinyin(name: str, query: str) -> bool:
    """检查名称是否匹配搜索词（支持中文名、拼音全拼、拼音首字母匹配）。
    
    - 中文名称子串匹配
    - 拼音全拼子串匹配
    - 拼音首字母子串匹配
    
    例如:
        name="钙化大骨", query="gh"  -> True (首字母 "ghdg" 包含 "gh")
        name="卤大骨", query="dg"   -> True (首字母 "ldg" 包含 "dg")
        name="钙化大骨", query="dg"  -> True (首字母 "ghdg" 包含 "dg")
    """
    if not query or not name:
        return False

    query_lower = query.lower()

    # 中文名称子串匹配
    if query_lower in name.lower():
        return True

    # 拼音首字母子串匹配
    initials = get_pinyin_initials(name)
    if query_lower in initials:
        return True

    # 拼音全拼子串匹配
    full_pinyin = get_pinyin_full(name)
    if query_lower in full_pinyin:
        return True

    return False
