from conans import ConanFile, ConfigureEnvironment
import os
from conans.tools import download, unzip, os_info

class IcuConan(ConanFile):
    name = "icu"
    version = "57.1"
    branch = "master"
    url = "http://github.com/vitallium/conan-icu"
    license = "http://source.icu-project.org/repos/icu/icu/tags/release-57-1/LICENSE"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=True"

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
        sln_file = "%s\\icu\\source\\allinone\\allinone.sln" % self.conanfile_directory
        if self.settings.arch == "x86_64":
            arch = "x64"
        else:
            arch = "Win32"

        # upgrade projects 
        command_line = "/upgrade"
        self.run("devenv %s %s" % (sln_file, command_line))

        # and build
        command_line = "/build \"Release|%s\" /project i18n" % arch
        self.run("devenv %s %s" % (sln_file, command_line))

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
        flags = "--prefix='%s' --enable-tests=no --enable-samples=no" % self.normalize_prefix_path(self.package_folder)
        if self.options.shared == 'True':
            flags += ' --disable-static --enable-shared'
        else:
            flags += ' --enable-static --disable-shared'

        if os_info.is_macos:
            conf_name = 'MacOSX'
        elif os_info.is_windows:
            conf_name = 'MinGW'
        else:
            conf_name = self.settings.os

        env = ConfigureEnvironment(self.deps_cpp_info, self.settings)
        command_env = env.command_line
        if os_info.is_windows:
            command_env += " &&"

        self.run("which gcc")
        self.run("gcc --version")
        self.run("chmod +x icu/source/runConfigureICU icu/source/configure icu/source/install-sh")
        print   ("%s sh icu/source/runConfigureICU %s %s" % (command_env, conf_name, flags))
        self.run("%s sh icu/source/runConfigureICU %s %s" % (command_env, conf_name, flags))
        self.run("%s make" % command_env)
        self.run("%s make install" % command_env)

    def package(self):
        if self.settings.compiler != "Visual Studio":
            return

        self.copy("*.h", "include", src="icu/include", keep_path=True)
        if self.settings.arch == "x86_64":
            build_suffix = "64"
        else:
            build_suffix = ""

        if self.options.shared:
            self.copy(pattern="*.dll", dst="bin", src=("icu/bin%s" % build_suffix), keep_path=False)

        self.copy(pattern="*.lib", dst="lib", src=("icu/lib%s" % build_suffix), keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["icuin", "icuuc", "icudt"]
