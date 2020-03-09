import os
import yaml
import sys

import yaml.constructor


from collections import OrderedDict

class OrderedDictYamlLoader(yaml.Loader):
    """
    A YAML loader that loads mappings into ordered dictionaries.
    """

    def __init__(self, *args, **kwargs):
        super(OrderedDictYamlLoader,self).__init__(*args, **kwargs)

        self.add_constructor('tag:yaml.org,2002:map', type(self).construct_yaml_map)
        self.add_constructor('tag:yaml.org,2002:omap', type(self).construct_yaml_map)

    def construct_yaml_map(self, node):
        data = OrderedDict()
        yield data
        value = self.construct_mapping(node)
        data.update(value)

    def construct_mapping(self, node, deep=False):
        if isinstance(node, yaml.MappingNode):
            self.flatten_mapping(node)
        else:
            raise yaml.constructor.ConstructorError(None, None,
                'expected a mapping node, but found %s' % node.id, node.start_mark)

        mapping = OrderedDict()
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                hash(key)
            except TypeError as exc:
                raise yaml.constructor.ConstructorError('while constructing a mapping',
                    node.start_mark, 'found unacceptable key (%s)' % exc, key_node.start_mark)
            value = self.construct_object(value_node, deep=deep)
            mapping[key] = value
        return mapping

class OrderedDictYamlDumper(yaml.Dumper):
    class UnsortableList(list):
        def sort(self, *args, **kwargs):
            pass
    class UnsortableOrderedDict(OrderedDict):
        def items(self, *args, **kwargs):
            return UnsortableList(OrderedDict.items(self, *args, **kwargs))
    yaml.Dumper.add_representer(UnsortableOrderedDict, yaml.representer.SafeRepresenter.represent_dict)




class YamlUtils(object):

    @staticmethod
    def load_data(a_file, loader=None):
        data = {}
        try:
            with open(a_file, "rt") as fh:
                if loader == None:
                    data = yaml.load(fh,Loader=yaml.FullLoader)
                else:
                    # note: save_data will not be suportted
                    data = yaml.load(fh, Loader = loader)
        except Exception as e:
            raise Exception("Cannot parse yml file: %s" % e)
        return data

    @staticmethod
    def save_data(a_file,data, dumper=None, indent = 4):
        try:
            with open(a_file, "w") as fh:
                if dumper == None:
                    yaml.safe_dump(data, fh, indent = indent)
                else:
                    yaml.dump(data, fh, Dumper = dumper, indent = indent)
        except Exception as e:
            raise Exception("Cannot save_data yml file: %s" % e)

    @staticmethod
    def _is_abs(path):
        """
        Check if path is absolute on any platform.
        :param str path: Path to validate.
        :returns bool: True is absolute on any platform, False otherwise.
        """
        import posixpath
        import ntpath
        return posixpath.isabs(path) or ntpath.isabs(path)

    @staticmethod
    def _is_current_platform_abspath(path):
        """
        Check if the path is an obsolute path for the current platform.

        :param str path: Path to validate.

        :returns bool: True if absolute for this platform, False otherwise.
        """
        import posixpath
        import ntpath

        if sys.platform == "win32":
            # ntpath likes to consider a path starting with / to be absolute,
            # but it is not!
            return ntpath.isabs(path) and not posixpath.isabs(path)
        else:
            return posixpath.isabs(path)

    @classmethod
    def resolve_include(cls, file_name, include):
        path = os.path.expanduser(os.path.expandvars(include))
        # If the path is not absolute, make it so!
        if not cls._is_abs(path):
            # Append it to the current file's directory.
            path = os.path.join(os.path.dirname(file_name), path)
        # We have an absolute path, so check if it is meant for this platform.
        elif not cls._is_current_platform_abspath(path):
            # It wasn't meant for this platform, return nothing.
            return None
        return path
