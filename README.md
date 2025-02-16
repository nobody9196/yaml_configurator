## 📄描述 [Description]

这是一个实现了YAML文件操作的Python类 `YamlConfigurator`，提供了读取、写入、更新和**深度访问YAML文件内容**的功能。

[This is a Python class `YamlConfigurator` that implements YAML file operations, providing functionality for reading, writing, updating, and **deep access to YAML file content**.]

## ✏️主要功能 [Core Functions]

1. 深度获取嵌套键的值； [Deeply get the values of nested keys.]
2. 同时深度获取多个嵌套键的值； [Deeply get the values of multiple nested keys at the same time.]
3. 覆盖写入YAML文件； [Overwrite and write to YAML file.]
4. 追加写入YAML文件(追加列表)； [Append and write to YAML file (append list).]
5. 创建、安全读取YAML文件(ruamel.yaml.YAML)。 [Create and safely read YAML files (using ruamel.yaml.YAML).]

## 🔧核心方法 [Core Methods]

* safe_load：安全地加载YAML文件，若文件不存在，则加载默认值。[Safely loads a YAML file, loading default values if the file does not exist.]
* create：创建新的YAML文件。[Creates a new YAML file.]
* write：覆盖写入YAML文件。[Overwrites the YAML file.]
* update：更新YAML文件内容，可以选择追加列表中的数据。[Updates the content of the YAML file, with the option to append data to lists.]
* get：获取单个嵌套键的值。[Retrieves the value of a single nested key.]
* gets：获取多个嵌套键的值。[Retrieves the values of multiple nested keys.]

## 🛠️示例 [Examples]

```python
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
```

## 🔑关键点 [Key Points]

1. **递归更新字典**：`update`方法支持递归更新字典，并根据需要向列表中添加元素。

    [**Recursive Dictionary Update**: The update method supports recursively updating dictionaries and can add elements to lists as needed.]

2. **默认值处理**：`get`和`gets`方法支持提供默认值，若某些键不存在，可以返回默认值而不会抛出异常。

    [**Default Value Handling**: The get and gets methods support providing default values, so if some keys do not exist, they will return the default value without raising an exception.]

## ⏳测试 [Test]

`test_configurator`函数包含了对`YamlConfigurator`类各个功能的单元测试，确保其正确性。你可以通过调用此函数来验证类的功能。

[The `test_configurator` function contains unit tests for various functionalities of the `YamlConfigurator` class to ensure its correctness. You can call this function to validate the class’s functionality.]

## 📝最后 [Final Notes]

我并不清楚如今是否已有实现YAML文件深度解读的工具。如果你发现了，请告诉我！

[I’m not sure whether there are existing tools that provide deep parsing of YAML files. If you come across any, please let me know!]

如果你有任何问题或需要更深入的讲解，可以随时提问！

[Feel free to ask any questions or request further clarification!]