import shutil
import sys
from distutils.dist import Distribution

from setuptools import setup, Extension
import os
import distutils.cmd
from pathlib import Path
from zipfile import ZipFile

import distutils.cmd


# setup(
#     author='Andy Stokely',
#     email='amstokely@ucsd.edu',
#     name='netcalc',
#     install_requires=[],
#     platforms=['Linux',
#                'Unix', ],
#     python_requires="<=3.9",
#     py_modules=[path + "/netcalc/netcalc"],
#     packages=find_packages() + [''],
#     zip_safe=False,
#     package_data={
#         '': [
#             path + '/netcalc/_python_netcalc.so'
#         ]
#     },
# )


class PyNFsimInstallBuild(distutils.cmd.Command):
    description = "Compiles NFsim C++ using cmake."
    user_options = []

    def __init__(self, *args, **kwargs):
        cwd = Path.cwd()
        self.working_dir = cwd
        self.cmake_build_dir = cwd / "cbuild"
        self.dist_dir = cwd / "dist"
        self.dist_package_dir = self.dist_dir / "pynfsim"
        self.wrapper_name = Path("pynfsim.py")
        self.lib_name = Path("_pynfsim.so")
        self.cmake_build_dir.mkdir(exist_ok=True)
        self.dist_dir.mkdir(exist_ok=True)
        self.dist_package_dir.mkdir(exist_ok=True)
        self.version = "0.0.0"
        super().__init__(*args, **kwargs)

    def wheel_name(self):
        # create a fake distribution from arguments
        dummy_ext = Extension("foo", ["bar.pyx", "bar.c"])
        dist = Distribution(
            attrs = dict(
                name="pynfsim",
                version=self.version,
                ext_modules=[dummy_ext]
            )

        )
        # finalize bdist_wheel command
        bdist_wheel_cmd = dist.get_command_obj('bdist_wheel')
        bdist_wheel_cmd.ensure_finalized()
        # assemble wheel file name
        distname = bdist_wheel_cmd.wheel_dist_name
        tag = '-'.join(bdist_wheel_cmd.get_tag())
        return f'{distname}-{tag}.whl'

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.chdir(self.cmake_build_dir)
        os.system("cmake ..")
        os.system("cmake --build . -j")
        self.wrapper_name.rename(self.dist_package_dir / "pynfsim.py")
        self.lib_name.rename(self.dist_package_dir / "_pynfsim.so")
        os.chdir(self.dist_dir)
        with ZipFile(self.wheel_name(), 'w') as zipObj:
            zipObj.write(
                filename=self.dist_package_dir / "pynfsim.py",
                arcname="pynfsim/pynfsim.py",
            )
            zipObj.write(
                filename=self.dist_package_dir / "_pynfsim.so",
                arcname="pynfsim/_pynfsim.so",
            )
        shutil.rmtree(self.cmake_build_dir)
        shutil.rmtree(self.dist_package_dir)


class PyNFsimInstallCleanup(distutils.cmd.Command):
    description = "Cleans out junk files we don't want in the repo"
    user_options = []

    def __init__(self, *args, **kwargs):
        cwd = Path.cwd()
        self.install_dirs = [

        ]
        self.lib_files = []
        self.install_dirs.extend([
            cwd / "build",
            cwd / "dist",
        ])
        self.install_dirs.extend(list(cwd.glob("*.egg*")))
        self.remove_install_dirs()
        self.lib_files.extend(
            list((cwd / "pysrc/pynfsim").glob("*.so")))
        self.lib_files.extend(
            list((cwd / "pysrc/pynfsim").glob("*.dylib")))
        self.remove_lib_files()
        wrapper_files = list((cwd / "swig").glob("*.cxx*"))
        wrapper_files.extend(
            list((cwd / "swig").glob("*.cpp")))
        if (cwd / "pysrc/pynfsim/pynfsim.py").exists():
            wrapper_files.append(cwd / "pysrc/pynfsim/pynfsim.py")
        for w in wrapper_files:
            w.unlink()
        super().__init__(*args, **kwargs)

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def remove_install_dirs(self):
        for d in self.install_dirs:
            if d.exists():
                shutil.rmtree(d)

    def remove_lib_files(self):
        for f in self.lib_files:
            if f.exists():
                f.unlink()

    def run(self):
        cwd = Path.cwd()
        self.install_dirs.extend([
            cwd / "build",
            cwd / "dist",
        ])
        self.remove_install_dirs()
        egg = list(cwd.glob("*.egg*"))
        if egg:
            egg[0].unlink()
        self.lib_files.extend(
            list((cwd / "pysrc/pynfsim").glob("*.so")))
        self.lib_files.extend(
            list((cwd / "pysrc/pynfsim").glob("*.dylib")))
        self.remove_lib_files()
        wrapper_files = list(
            (cwd / "pysrc/pynfsim/swig").glob("*.cxx*"))
        wrapper_files.extend(
            list((cwd / "swig").glob("*.cpp")))
        if (cwd / "pysrc/pynfsim/pynfsim.py").exists():
            wrapper_files.append(cwd / "pysrc/pynfsim/pynfsim.py")
        for wrapper_file in wrapper_files:
            wrapper_file.unlink()


setup_args = dict(
    name='pynfsim',
    ext_modules=[
        Extension(
            'pynfsim._pynfsim',
            [
                'swig/pynfsim.i',
                'src/NFsim.cpp',
            ] +
            [str(p) for p in
             Path.cwd().rglob("src") if ".cpp" in p.name]
            ,
            swig_opts=["-c++", "-outdir", "pysrc/pynfsim",
                       f"-I{Path.cwd()}/src", ] +
                      ["-I" + str(p) for p in Path.cwd().glob("src/*")
                       if
                       p.is_dir()]
            ,
            extra_compile_args=["-Wno-deprecated",
                                ],
            include_dirs=[
                             f"{Path.cwd()}/src",
                         ] + [
                             str(p) for p in Path.cwd().glob("src/*") if
                             p.is_dir()
                         ],
        )
    ],
    packages=['pynfsim'],
    package_dir={'pynfsim': 'pysrc/pynfsim'},
    package_data={'pynfsim': ['pysrc/pynfsim/pynfsim.py']},
    cmdclass={
        'build': PyNFsimInstallBuild,
        'clean': PyNFsimInstallCleanup,
    },
)

setup(**setup_args)
