"""
字典数据内存缓存模块
字典数据读取频繁但修改极少，使用本地内存缓存减少数据库查询
"""
from typing import Dict, List, Optional
from threading import Lock
from app.models import SysDict


class DictCache:
    """字典数据本地内存缓存（线程安全）"""

    def __init__(self):
        # dict_type -> {code: label}
        self._code_label_map: Dict[str, Dict[int, str]] = {}
        # dict_type -> [{code, label, sort_order}]
        self._dict_list: Dict[str, List[dict]] = {}
        self._lock = Lock()

    def load_all(self, db_session):
        """从数据库加载全部启用的字典数据到缓存"""
        items = db_session.query(SysDict).filter(SysDict.status == 1).order_by(
            SysDict.dict_type.asc(), SysDict.sort_order.asc()
        ).all()

        code_label_map: Dict[str, Dict[int, str]] = {}
        dict_list: Dict[str, List[dict]] = {}

        for item in items:
            if item.dict_type not in code_label_map:
                code_label_map[item.dict_type] = {}
                dict_list[item.dict_type] = []
            code_label_map[item.dict_type][item.code] = item.label
            dict_list[item.dict_type].append({
                "code": item.code,
                "label": item.label,
                "sort_order": item.sort_order,
            })

        with self._lock:
            self._code_label_map = code_label_map
            self._dict_list = dict_list

    def get_code_label_map(self, dict_type: str) -> Dict[int, str]:
        """获取指定类型的 code->label 映射"""
        with self._lock:
            return self._code_label_map.get(dict_type, {}).copy()

    def get_dict_list(self, dict_type: str) -> List[dict]:
        """获取指定类型的字典列表 [{code, label, sort_order}]"""
        with self._lock:
            return self._dict_list.get(dict_type, []).copy()

    def get_label(self, dict_type: str, code: int) -> Optional[str]:
        """根据 dict_type + code 获取 label"""
        with self._lock:
            return self._code_label_map.get(dict_type, {}).get(code)

    def invalidate(self, dict_type: Optional[str] = None):
        """
        失效缓存（由 CRUD 接口调用）
        dict_type 为 None 时清空全部缓存
        """
        with self._lock:
            if dict_type is None:
                self._code_label_map.clear()
                self._dict_list.clear()
            else:
                self._code_label_map.pop(dict_type, None)
                self._dict_list.pop(dict_type, None)


# 全局单例
dict_cache = DictCache()
