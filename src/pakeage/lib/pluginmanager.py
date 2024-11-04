# pluginmanager.py
import os
from PyQt5.QtCore import QObject, QDir, QFileInfo, QPluginLoader, QJsonDocument
from PyQt5.QtWidgets import qApp

PLUGIN_CONF_PATH = os.path.join(qApp.applicationDirPath(), "config", "plugins.json")

class PluginCongInfo:
    def __init__(self, plugin_name="", is_used="1"):
        self.plugin_name = plugin_name
        self.is_used = is_used


class PluginManagerPrivate:
    def __init__(self):
        self.m_names = {}  # plugin path -> plugin name
        self.m_versions = {}  # plugin path -> plugin version
        self.m_dependencies = {}  # plugin path -> list of dependencies
        self.m_loaders = {}  # plugin path -> QPluginLoader instance
        self.plugin_cong_info = {}
        self.m_load_order = []  # load order of plugins

    def check(self, filepath):
        for item in self.m_dependencies.get(filepath, []):
            name = item["name"]
            version = item["version"]
            path = next((k for k, v in self.m_names.items() if v == name), None)

            if name not in self.m_names.values():
                print(f"Missing dependency: {name} for plugin {path}")
                return False
            if self.m_versions[path] != version:
                print(f"Version mismatch: {name} version {self.m_versions[path]} but {version} required for plugin {path}")
                return False
            if not self.check(path):
                print(f"Corrupted dependency: {name} for plugin {path}")
                return False
        return True


class PluginManager(QObject):
    _instance = None

    @staticmethod
    def get_instance():
        if PluginManager._instance is None:
            PluginManager._instance = PluginManager()
        return PluginManager._instance

    def __init__(self):
        super().__init__()
        self.m_config_file = ""
        self.m_plugin_data = PluginManagerPrivate()

    def load_plugin(self, file_path):
        if not QPluginLoader.isLibrary(file_path):
            return False

        if not self.m_plugin_data.check(file_path):
            return False

        loader = QPluginLoader(file_path)
        file_info = QFileInfo(file_path)
        file_name = file_info.fileName()

        if loader.load():
            print(f"加载插件：{file_name} 成功")
            plugin = loader.instance()
            if plugin:
                self.m_plugin_data.m_loaders[file_path] = loader
            else:
                del loader
            return True
        print(f"加载插件：{file_name} 失败")
        return False

    def unload_plugin(self, file_path):
        if not self.m_plugin_data:
            return False
        loader = self.m_plugin_data.m_loaders.get(file_path)
        file_info = QFileInfo(file_path)
        file_name = file_info.fileName()

        if loader and loader.unload():
            del self.m_plugin_data.m_loaders[file_path]
            del loader
            print(f"卸载插件：{file_name} 成功")
            return True
        print(f"卸载插件：{file_name} 失败")
        return False

    def load_all_plugins(self):
        self.set_plugin_list()
        self.m_plugin_data.m_loaders.clear()

        plugins_dir = QDir(qApp.applicationDirPath())
        plugins_dir.cd("plugins")
        plugins_info = plugins_dir.entryInfoList(QDir.Files | QDir.NoDotAndDotDot)

        useable_list = []
        for file_info in plugins_info:
            if QPluginLoader.isLibrary(file_info.absoluteFilePath()):
                file_name = file_info.baseName()
                if file_name in self.m_plugin_data.plugin_cong_info:
                    config = self.m_plugin_data.plugin_cong_info[file_name]
                    if config.is_used == "1":
                        useable_list.append(file_info)

        for plugin_name in self.m_plugin_data.m_load_order:
            for file_info in useable_list:
                if file_info.baseName() == plugin_name:
                    path = file_info.absoluteFilePath()
                    if self.load_plugin(path):
                        self.scan_meta_data(path)

        for plugin_name in self.m_plugin_data.m_load_order:
            for file_info in useable_list:
                if file_info.baseName() == plugin_name:
                    path = file_info.absoluteFilePath()
                    loader = self.m_plugin_data.m_loaders.get(path)
                    if loader:
                        plugin = loader.instance()
                        if plugin:
                            if plugin.init():
                                print(f"初始化插件: {plugin_name} 成功")
                            else:
                                print(f"初始化插件: {plugin_name} 失败")
                    break

        return True

    def unload_all_plugins(self):
        if not self.m_plugin_data:
            return False

        for i in range(len(self.m_plugin_data.m_load_order) - 1, -1, -1):
            for file_info in self.m_plugin_data.m_loaders.keys():
                if file_info.baseName() == self.m_plugin_data.m_load_order[i]:
                    path = file_info.absoluteFilePath()
                    loader = self.m_plugin_data.m_loaders.get(path)
                    if loader:
                        plugin = loader.instance()
                        if plugin:
                            if plugin.clean():
                                print(f"清理插件: {file_info.baseName()} 成功")
                            else:
                                print(f"清理插件: {file_info.baseName()} 失败")
                    break

        for i in range(len(self.m_plugin_data.m_load_order) - 1, -1, -1):
            for file_info in self.m_plugin_data.m_loaders.keys():
                if file_info.baseName() == self.m_plugin_data.m_load_order[i]:
                    path = file_info.absoluteFilePath()
                    self.unload_plugin(path)
                    break
        return True

    def get_plugins_name(self):
        return list(self.m_plugin_data.m_names.values())

    def scan_meta_data(self, filepath):
        if not self.m_plugin_data:
            return
        if not QPluginLoader.isLibrary(filepath):
            return
        loader = QPluginLoader(filepath)
        json = loader.metaData().value("MetaData").toObject()

        self.m_plugin_data.m_names[filepath] = json.value("name").toVariant()
        self.m_plugin_data.m_versions[filepath] = json.value("version").toVariant()
        self.m_plugin_data.m_dependencies[filepath] = json.value("dependencies").toArray().toVariantList()

    def set_plugin_list(self):
        self.m_config_file = PLUGIN_CONF_PATH

        with open(self.m_config_file, 'r') as file:
            data = file.read()

        doc = QJsonDocument.fromJson(data.encode())
        obj = doc.object()
        plugin_array = obj["plugins"].toArray()

        self.m_plugin_data.plugin_cong_info.clear()
        self.m_plugin_data.m_load_order.clear()

        for value in plugin_array:
            plugin_obj = value.toObject()
            plugin_name = plugin_obj["name"].toString()
            is_used = plugin_obj["isUsed"].toString()
            info = PluginCongInfo(plugin_name, is_used)

            if info.is_used == "1":
                self.m_plugin_data.plugin_cong_info[info.plugin_name] = info
                self.m_plugin_data.m_load_order.append(info.plugin_name)
