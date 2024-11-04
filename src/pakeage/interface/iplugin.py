from abc import ABC, abstractmethod

class PluginInterface(ABC):
    @abstractmethod
    def get_name(self) -> str:
        """获取插件名称"""
        pass

    @abstractmethod
    def init(self) -> bool:
        """初始化插件"""
        pass

    @abstractmethod
    def clean(self) -> bool:
        """清理插件"""
        pass

# 可以通过其他方式定义接口标识符，比如使用常量
PluginInterface_iid = "lrl.QtPluginsManager.PluginInterface"
