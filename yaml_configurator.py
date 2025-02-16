#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
YAML文件配置器 [YAML File Configurator]

描述 [Description]：
    在初始化YAML文件后，你可以获得一个YamlConfigurator对象；
    在其他py文件中，通过get和gets方法，可以轻松地深度获取多个嵌套的YAML键的值；
    此外，你还可以将结果也是一个YamlConfigurator对象，并继续使用get和gets方法。
    [After initializing the YAML file, you can obtain a YamlConfigurator object.
    In other py files, you can easily deeply get the values of multiple nested YAML keys through the get and gets methods.
    In addition, the result is also a YamlConfigurator object, and you can continue to use the get and gets methods.]

核心功能 [Core Functions]：
    1. 深度获取嵌套键的值； [Deeply get the values of nested keys.]
    2. 同时深度获取多个嵌套键的值； [Deeply get the values of multiple nested keys at the same time.]
    3. 覆盖写入YAML文件； [Overwrite and write to YAML file.]
    4. 追加写入YAML文件(追加列表)； [Append and write to YAML file (append list).]
    5. 创建、安全读取YAML文件(ruamel.yaml.YAML)。 [Create and safely read YAML files (using ruamel.yaml.YAML).]

Examples:
    >>> from yaml_configurator import YamlConfigurator
    >>> # 1. 创建一个YAML文件('ignore_exists'忽略存在的文件并覆盖)。 [Create a YAML file ('ignore_exists' ignores existing files and overrides).]
    >>> yaml = YamlConfigurator(file_path='config.yaml')
    >>> yaml.create({'key1': {'sub_key1': 'value11'}, 'key2': 'value2'}, ignore_exists=True)
    >>> yaml.data
    {'key1': {'sub_key1': 'value11'}, 'key2': 'value2'}
    >>> # 2.1 加载一个YAML文件。 [Load a YAML file.]
    >>> yaml = YamlConfigurator(file_path='config.yaml').safe_load()
    >>> # 2.2 获取已存在键的值 (key: key1 - sub_key1)。 [Get the value of an existing key.]
    >>> yaml.get('key1', 'sub_key1')
    'value11'
    >>> # 2.3 获取多个已存在键的值 (keys: key1 - sub_key1, key2)。 [Get the values of multiple existing keys.]
    >>> yaml.gets(['key1', 'sub_key1'], 'key2')
    ['value11', 'value2']
    >>> # 2.4 获取不存在键的值，并给定默认值 (key: key2 - sub_key1)。 [Get the value of a non-existing key and give a default value.]
    >>> yaml.get('key2', 'sub_key1', default='default_value')
    'default_value'
    >>> # 2.5 覆盖更新YAML文件中键的值 (key: key1)。 [Overwrite the value of a key in the YAML file.]
    >>> yaml.update({'key1': {'sub_key1': ['value11', 'value12'], 'sub_key2': 'value21'}})
    >>> yaml.data
    {'key1': {'sub_key1': ['value11', 'value12'], 'sub_key2': 'value21'}, 'key2': 'value2'}
    >>> # 2.6 追加更新YAML文件中键的列表 (key: key1 - sub_key)。 [Append update the list of a key in the YAML file.]
    >>> yaml.update({'key1': {'sub_key1': ['value13']}, 'key3': 'value3'}, append_list=True)
    >>> yaml.data
    {'key1': {'sub_key1': ['value11', 'value12', 'value13'], 'sub_key2': 'value21'}, 'key2': 'value2', 'key3': 'value3'}
    >>> # 2.7.1 获取多个已存在键的值，且有的存在同一父源 (keys: key1 - sub_key1, key1 - sub_key2, key2)。
    >>> # [Get the values of multiple existing keys, and some exist in the same parent source.]
    >>> yaml.gets(['key1', ['sub_key1', 'sub_key2']], 'key2')
    [[['value11', 'value12', 'value13'], 'value21'], 'value2']
    >>> # 2.7.2 再进行解包，愉快地获得YAML文件中更深层的值。 [Unpack again to happily get deeper values in the YAML file.]
    >>> (sub_key1, sub_key2), key2 = yaml.gets(['key1', ['sub_key1', 'sub_key2']], 'key2')
    >>> sub_key1, sub_key2, key2
    (['value11', 'value12', 'value13'], 'value21', 'value2')
"""
import os
from typing import Any, Dict, List, Union

from ruamel.yaml import YAML


class YamlConfigurator:
    """
    YAML文件配置器。 [YAML File Configurator.]

    Parameters:
        file_path: 文件路径。 [YAML file path, default: None.]
        data: 配置数据。 [YAML file data, default: None.]
    """

    def __init__(self, file_path: str = None, data: Dict = None):
        self.file_path = file_path
        self._data = data

    def __str__(self):
        return os.path.basename(self.file_path) if self.file_path is not None else None

    @staticmethod
    def __write(file_path: str, data: Dict, create: bool = False) -> None:
        """
        写入 YAML 文件。 [Write to YAML file.]
        """
        if os.path.exists(file_path) and create:
            raise FileExistsError(f'The file already exists: {file_path}')

        yaml = YAML(typ='safe')
        with open(file_path, 'w', encoding='utf-8') as file:
            yaml.dump(data, file)

    @classmethod
    def __get(cls, *args: Union[str, List[str]], data: Dict, parent_args: List = None, **kwargs) -> Any:
        """
        获取子值。 [Get child value.]

        :param args: YAML对象的键，用于访问嵌套值。 [Keys of the YAML object, used to access nested values.]
        :param data: 深度拷贝后的字典对象。 [Deep copy of the dictionary object.]
        :param has_default: 是否存在默认值。 [Whether there is a default value.]
        :return: 子值的值，如果不存在则返回默认值，若无默认值则抛出异常。 [The value of the child value, if it does not exist, return the default value, otherwise throw an exception.]
        :raises KeyError: 配置参数缺失。 [Missing configuration parameters.]
        :raises ValueError: 只允许最后一个参数为列表。 [Only the last parameter is allowed to be a list.]
        """
        has_default = 'default' in kwargs
        default = kwargs.get('default')

        exists_args = [] if not parent_args else parent_args.copy()
        for i, arg in enumerate(args):
            # 仅最后一个参数可以是列表，且该列表中的元素用于访问多个子键。 [This is to allow fetching multiple keys in a single operation.]
            if isinstance(arg, list):
                if i != len(args) - 1:
                    raise ValueError(f'Only the last parameter can be a list: {arg}.')

                results = []
                for a in arg:
                    results.append(cls.__get(a, data=data, parent_args=exists_args, **kwargs))
                return results

            else:
                exists_args.append(arg)
                try:
                    data = data[arg]
                except (KeyError, TypeError):
                    if has_default:
                        return default

                    raise KeyError(f'Missing configuration parameters: {exists_args}.')

        return data

    @classmethod
    def _recursive_update(cls, original_dict: Dict, new_dict: Dict, append_list: bool = False) -> Dict:
        """
        递归更新字典。 [Recursively update dictionary.]

        :param original_dict: 原始字典。 [the original dictionary.]
        :param new_dict: 新字典。 [the new dictionary.]
        :param append_list: 如果为True，则会将新字典中的列表元素追加到原始字典中的对应位置。否则，会直接覆盖原始字典中的值。
         [If append_list is True, new list elements in the new dictionary will be appended to the original list.
          Otherwise, it will overwrite the values in the original dictionary.]
        """
        for key, value in new_dict.items():
            if isinstance(value, dict):
                # 如果original_dict中没有key或者key对应的值不是字典类型，则将key对应的值设为空字典。
                # [if original_dict does not have key or key value is not a dictionary type, set key value to empty dictionary.]
                if not isinstance(original_dict, dict) or key not in original_dict or not isinstance(original_dict[key],
                                                                                                     dict):
                    original_dict[key] = {}
                cls._recursive_update(original_dict[key], value, append_list)
            elif isinstance(value, list) and append_list:
                # 如果original_dict中没有key或者key对应的值不是列表类型，则将key对应的值设为空列表。
                # [if original_dict does not have key or key value is not a list type, set key value to empty list.]
                if key not in original_dict or not isinstance(original_dict[key], list):
                    original_dict[key] = []
                cls._append_list_items(original_dict[key], value)
            else:
                original_dict[key] = value

        return original_dict

    @classmethod
    def _append_list_items(cls, original_list: List, new_items: List) -> None:
        """
        将新项追加到原始列表中。如果原始列表中的项是字典类型，则递归更新它们。
        [Append new items to the original list.
        if the items in the original list are of dictionary type, update them recursively.]
        """
        for item in new_items:
            if isinstance(item, dict):
                # 如果item是字典类型，递归更新。 [if item is a dictionary type, update recursively.]
                original_list.append({})
                cls._recursive_update(original_list[-1], item)
            else:
                # 如果item不是字典类型，直接追加到列表。 [if item is not a dictionary type, append directly to the list.]
                original_list.append(item)

    @property
    def data(self) -> Dict:
        """
        获取数据副本。 [Get a copy of the data.]
        :return: 数据副本。 [data copy.]
        """
        return self._data.copy()

    def safe_load(self, default: Dict = None) -> 'YamlConfigurator':
        """
        安全加载 YAML 文件。 [Safe load YAML file.]
        :param default: 默认值。 [default value.]
        :return: YamlConfigurator对象。 [YamlConfigurator object.]
        """
        try:
            yaml = YAML(typ='safe')
            with open(self.file_path, 'r', encoding='utf-8') as file:
                self._data = yaml.load(file)
        except FileNotFoundError as e:
            if default is None:
                raise e
            self._data = default

        return self

    def create(self, data: Dict, ignore_exists: bool = False) -> None:
        """
        创建 YAML 文件。 [Create YAML file.]
        """
        self.__write(self.file_path, data, create=ignore_exists == False)
        self._data = data

    def write(self, data: Dict) -> None:
        """
        覆盖写入 YAML 文件。 [Override write YAML file.]
        """
        self.__write(self.file_path, data)
        self._data = data

    def update(self, data: Dict, append_list: bool = False) -> None:
        """
        更新 YAML 文件。 [Update YAML file.]

        :param data: 要更新的数据。 [Data to be updated.]
        :param append_list: 是否将新项追加到列表中，而不是替换它们。 [Whether to append new items to the list instead of replacing them.]
        :return: None
        """
        new_data = self._recursive_update(self._data, data, append_list)
        self.__write(self.file_path, new_data)
        self._data = new_data

    def get(self, *args: Union[str, List[str]], return_yc: bool = False, **kwargs) -> Union['YamlConfigurator', Any]:
        """
        从 YAML 对象中依次获得嵌套键的值。 [YAML object to obtain nested key values in turn.]

        :param args: YAML中的键，用于访问里面嵌套键的值。 [Keys in YAML, used to access the value of nested keys.]
        :param return_yc: 是否返回YamlConfigurator对象。 [Whether to return YamlConfigurator object.]
        :param kwargs: 可选参数，用于指定默认值(default)。 [Optional parameter, used to specify the default value (default).]
        :return: 键的值。如果不存在则返回默认值，若无默认值则抛出异常。
         [The value of the key. if it does not exist, return the default value.
          if there is no default value, an exception will be thrown.]
        """
        data = self.__get(*args, data=self._data, **kwargs)

        if not return_yc:
            return data

        # 字典对象可以转为YamlManager对象。 [Dictionary objects can be converted to YamlManager objects.]
        if not isinstance(data, dict):
            raise TypeError(
                f'When converting to YamlManager object, data type error, should be dict, actual: {type(data)}')

        return YamlConfigurator(self.file_path, data)

    def gets(self, *args: Union[List, str], return_yc: bool = False, **kwargs) -> Union['YamlConfigurator', Any]:
        """
        从 YAML 对象中依次获得多个嵌套键的值。 [YAML object to obtain multiple nested keys in turn.]

        :param args: YAML中的键，用于访问里面更深的键的值。 [Keys in YAML, used to access the value of deeper keys.]
        :param return_yc: 是否返回YamlConfigurator对象。 [Whether to return YamlConfigurator object.]
        :param kwargs: 可选参数，用于指定默认值(default)。 [Optional parameter, used to specify the default value (default).]
        :return: 键的值。如果不存在则返回默认值，若无默认值则抛出异常。
         [The value of the key. if it does not exist, return the default value.
          if there is no default value, an exception will be thrown.]
        """
        results = []

        # 处理默认值 [Handle default value]
        has_default = 'default' in kwargs
        if not has_default:
            defaults = []
        else:
            default = kwargs.get('default')
            if isinstance(default, list):
                if len(default) != len(args):
                    raise ValueError(f'The length of the default value list ({len(default)})'
                                     f' does not match the length of the parameter list ({len(args)})')

                defaults = default
            else:
                defaults = [default] * len(args)

        # 获取多个嵌套键的值 [Get multiple nested key values]
        for (i, x) in enumerate(args):
            if isinstance(x, list):
                result = self.get(*x, return_yc=return_yc, **{'default': defaults[i]} if has_default else {})
            elif isinstance(x, str):
                result = self.get(x, return_yc=return_yc, **{'default': defaults[i]} if has_default else {})
            else:
                raise TypeError(f'Parameter type error, should be str or list, actual: {type(x)}')

            results.append(result)

        return results[0] if len(args) == 1 else results


def test_configurator():
    """
    单元测试。 [Single unit test.]
    """
    # 创建一个临时文件路径。 [Create a temporary file path.]
    file_path = "test.yaml"

    # 测试1：创建一个新的YAML文件。 [Create a new YAML file.]
    yaml_configurator = YamlConfigurator(file_path)
    yaml_configurator.create({"name": "John", "age": 30})
    assert os.path.exists(file_path)

    # 测试2：读取YAML文件。 [YAML file reading.]
    yaml_configurator.safe_load()
    assert yaml_configurator.get("name") == "John"
    assert yaml_configurator.get("age") == 30

    # 测试3：更新YAML文件。 [Update YAML file.]
    yaml_configurator.update({"age": 31})
    assert yaml_configurator.get("age") == 31

    # 测试4：递归更新YAML文件。 [Recursive update YAML file.]
    yaml_configurator.update({"address": {"city": "New York", "zip": "10001"}})
    assert yaml_configurator.get("address", "city") == "New York"
    assert yaml_configurator.get("address", "zip") == "10001"

    # 测试5：安全加载YAML文件。 [YAML file safe loading.]
    yaml_configurator = YamlConfigurator(file_path).safe_load()
    assert yaml_configurator.get("name") == "John"
    assert yaml_configurator.get("age") == 31
    assert yaml_configurator.get("address", "city") == "New York"
    assert yaml_configurator.get("address", "zip") == "10001"

    # 测试6：获取不存在的键。 [Get non-existent key.]
    assert yaml_configurator.get("gender", default=None) is None

    # 测试7：获取不存在的嵌套键。 [Get non-existent nested key.]
    assert yaml_configurator.get("address", "state", default=None) is None

    # 测试8：获取默认值。 [Get default value.]
    assert yaml_configurator.get("gender", default="Male") == "Male"

    # 测试9：获取嵌套键的默认值。 [Get default value of nested key.]
    assert yaml_configurator.get("address", "state", default="NY") == "NY"

    # 测试10：覆盖写入YAML文件。 [Overwrite writing YAML file.]
    yaml_configurator.write({"name": "Jane", "age": 25})
    assert yaml_configurator.get("name") == "Jane"
    assert yaml_configurator.get("age") == 25

    # 测试11：更新列表。 [Update list.]
    yaml_configurator.update({"hobbies": ["reading", "painting"]}, append_list=True)
    assert yaml_configurator.get("hobbies") == ["reading", "painting"]

    # 测试12：递归更新列表。 [Recursive update list.]
    yaml_configurator.update({"hobbies": [{"name": "swimming", "level": "intermediate"}]}, append_list=True)
    assert {"name": "swimming", "level": "intermediate"} in yaml_configurator.get("hobbies")

    # 删除临时文件。 [Delete temporary file.]
    os.remove(file_path)

    print("All test cases pass.")


if __name__ == "__main__":
    test_configurator()
