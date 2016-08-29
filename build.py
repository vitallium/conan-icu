import os, sys
import platform

def system(command):
   retcode = os.system(command)
   if retcode != 0:
       raise Exception("Error while executing:\n\t %s" % command)

if __name__ == "__main__":
   system('conan export vitallium/stable')
   params = " ".join(sys.argv[1:])

   if platform.system() == "Windows":
       for arch in ["x86", "x86_x64"]:
           system('conan test -s compiler="Visual Studio" -s arch=%s -s compiler.version=14 %s' % (arch, params))
   else:
       pass