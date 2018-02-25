#!/usr/bin/env python

import os
import fnmatch
from glob import glob

from conans import ConanFile
from conans.tools import download, unzip, os_info, cpu_count

from vcproj import Project

class IcuConan(ConanFile):
    name = "icu"
    version = "59.1"
    branch = "master"
    url = "http://github.com/vitallium/conan-icu"
    license = "http://source.icu-project.org/repos/icu/tags/release-59-1/icu4c/LICENSE"
    description = "ICU is a mature, widely used set of C/C++ and Java libraries providing Unicode and Globalization support for software applications."
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=True"
    generators = "cmake"
    exports = ["vcproj/*.py"]

    def source(self):
        zip_name = "icu4c-%s-src.zip" % self.version.replace(".", "_")
        url = "http://download.icu-project.org/files/icu4c/%s/%s" % (self.version, zip_name)
        download(url, zip_name)
        unzip(zip_name)
        os.unlink(zip_name)

    def config(self):
        if self.settings.compiler == "Visual Studio" and \
           self.options.shared and "MT" in str(self.settings.compiler.runtime):
            self.options.shared = False

    def build(self):
        if self.settings.compiler == "Visual Studio":
            self.build_windows()
        else:
            self.build_with_configure()

    def build_windows(self):
        sln_file = "%s\\icu\\source\\allinone\\allinone.sln" % self.source_folder
        if self.settings.arch == "x86_64":
            arch = "x64"
        else:
            arch = "Win32"

        runtime_map = {
            "MDd": "MultiThreadedDebugDLL",
            "MD": "MultiThreadedDLL",
            "MTd": "MultiThreadedDebug",
            "MT": "MultiThreaded"
        }
        runtime = runtime_map[str(self.settings.compiler.runtime)]
        self.patch_vcproj(self.source_folder, runtime)

        # build
        command_line = "/t:makedata /p:configuration=%s /property:Platform=%s" % (self.settings.build_type, arch)
        self.run("msbuild %s /property:MultiProcessorCompilation=true %s" % (sln_file, command_line))

    def normalize_prefix_path(self, p):
        if os_info.is_windows:
            drive, path = os.path.splitdrive(p)
            msys_path = path.replace('\\', '/')
            if drive:
                return '/' + drive.replace(':', '') + msys_path
            else:
                return msys_path
        else:
            return p

    def build_with_configure(self):
        pass
        # flags = "--prefix='%s' --enable-tests=no --enable-samples=no" % self.normalize_prefix_path(self.package_folder)
        # if self.options.shared == 'True':
        #     flags += ' --disable-static --enable-shared'
        # else:
        #     flags += ' --enable-static --disable-shared'

        # if os_info.is_macos:
        #     conf_name = 'MacOSX'
        # elif os_info.is_windows:
        #     conf_name = 'MinGW'
        # elif os_info.is_linux and self.settings.compiler == "gcc":
        #     conf_name = 'Linux/gcc'
        # else:
        #     conf_name = self.settings.os

        # env = ConfigureEnvironment(self.deps_cpp_info, self.settings)
        # command_env = env.command_line_env
        # if os_info.is_windows:
        #     command_env += " &&"

        # self.run("chmod +x icu/source/runConfigureICU icu/source/configure icu/source/install-sh")
        # self.run("%s sh icu/source/runConfigureICU %s %s" % (command_env, conf_name, flags))
        # self.run("%s make -j %s" % (command_env, cpu_count()))
        # self.run("%s make install" % command_env)

    def package(self):
        if self.settings.compiler != "Visual Studio":
            return

        self.copy("*.h", "include", src="icu/include", keep_path=True)
        if self.settings.arch == "x86_64":
            arch_suffix = "64"
        else:
            arch_suffix = ""

        # match_pattern = "icu(?:dt|in|uc)\\d{0,2}\\.(?:dll|lib)"
        self.copy(pattern="*.dll", dst="bin", src=("icu/bin%s" % arch_suffix), keep_path=False)
        self.copy(pattern="*.lib", dst="lib", src=("icu/lib%s" % arch_suffix), keep_path=False)

    def package_info(self):
        if os_info.is_windows:
            debug_suffix = ""
            if self.settings.build_type == "Debug":
                debug_suffix = "d"
            self.cpp_info.libs = ["icuin" + debug_suffix, "icuuc" + debug_suffix, "icudt"]
        else:
            self.cpp_info.libs = ["icui18n", "icuuc", "icudata"]

    def patch_vcproj(self, root, runtime):
        for root, _, filenames in os.walk(root):
            for filename in fnmatch.filter(filenames, '*.vcxproj'):
                p = Project(os.path.join(root, filename))
                p.set_windows_sdk_version('10.0.16299.0')
                p.set_platform_toolset('v141')
                p.set_runtime_library(runtime)
                p.save()
