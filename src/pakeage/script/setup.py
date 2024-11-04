from setuptools import setup, find_packages

setup(
    name='testpy01',  # 项目名称
    version='0.1',  # 版本号
    author='lrl',  # 作者姓名
    author_email='12345@example.com',  # 作者邮箱
    description='测试pyqt',  # 项目描述
    packages=find_packages(),  # 自动查找并包含包
    package_dir={'': 'lib'},  # 指定包目录为 lib
    py_modules=['app.main', 'lib.test'],  # 显式指定模块
    install_requires=[
        # 在这里列出项目的依赖项（如果有的话）
    ],
    entry_points={
        'console_scripts': [
            'run-main=..main:main',  # 假设 main.py 有一个名为 main 的函数
        ],
    },
)
