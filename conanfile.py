from conans import ConanFile, ConfigureEnvironment
import os
from conans.tools import download, unzip, replace_in_file, check_md5

class IcuConan(ConanFile):
    name = "icu"
    version = "57.1"
    branch = "master"
    url = "http://github.com/vitallium/conan-icu"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=True"
    generators = "cmake"

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
        if self.settings.os == "Windows":
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

    def build_with_configure(self):
        env = ConfigureEnvironment(self.deps_cpp_info, self.settings)
        self.run("chmod +x icu/source/runConfigureICU icu/source/configure icu/source/install-sh")
        self.run("%s icu/source/runConfigureICU Linux --prefix=%s --enable-shared=yes --enable-tests=no --enable-samples=no" % (env.command_line, self.package_folder))
        self.run("%s make" % env.command_line)
        self.run("%s make install" % env.command_line)

    def package(self):
        if self.settings.os != "Windows":
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
