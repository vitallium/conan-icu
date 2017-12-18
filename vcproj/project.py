# Copyright Josh Handley <https://github.com/jhandley/pyvcproj>

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

try:
    _register_namespace = ET.register_namespace
except AttributeError:
    def _register_namespace(prefix, uri):
        ET._namespace_map[uri] = prefix

_MS_BUILD_NAMESPACE = "http://schemas.microsoft.com/developer/msbuild/2003"

class Project(object):
    """A very dumb class for manipulating *.vcxproj files"""

    def __init__(self, filename):
        _register_namespace('', _MS_BUILD_NAMESPACE)
        self.filename = filename
        self.tree = ET.parse(filename)
        self.root = self.tree.getroot()

    def set_windows_sdk_version(self, version):
        # Global is a single element
        parent_element = self.root.find("./{" + _MS_BUILD_NAMESPACE + "}PropertyGroup[@Label='Globals']")
        element = ET.Element("WindowsTargetPlatformVersion")
        element.text = version
        parent_element.append(element)

    def set_runtime_library(self, runtime_library):
        # umm...
        for runtime in self.root.findall("./{" + _MS_BUILD_NAMESPACE + "}ItemDefinitionGroup/{" + _MS_BUILD_NAMESPACE + "}ClCompile/{" + _MS_BUILD_NAMESPACE + "}RuntimeLibrary"):
            runtime.text = runtime_library

    def set_platform_toolset(self, platform_toolset):
        # umm v2...
        for platform in self.root.findall("./{" + _MS_BUILD_NAMESPACE + "}PropertyGroup[@Label='Configuration']/{" + _MS_BUILD_NAMESPACE + "}PlatformToolset"):
            platform.text = platform_toolset

    def save(self, filename=None):
        filename = filename or self.filename
        self.tree.write(filename, xml_declaration=True, encoding="utf-8", method="xml")
