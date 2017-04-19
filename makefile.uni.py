# Copyright (C) 2015 Sebastian Herbord. All rights reserved.
#
# This file is part of Mod Organizer.
#
# Mod Organizer is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mod Organizer is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mod Organizer.  If not, see <http://www.gnu.org/licenses/>.


from unibuild import Project
from unibuild.modules import github, cmake, Patch, git, hg, msbuild, build, dummy
from unibuild.utility import lazy, FormatDict
from config import config
from functools import partial
from string import Formatter
import os


"""
Settings
"""

loot_version = "0.10.3"
commit_id = "g0fcf788"

"""
Projects
"""


from unibuild.projects import sevenzip, qt5, boost, zlib, python, sip, pyqt5, ncc
from unibuild.projects import asmjit, udis86, googletest, spdlog, fmtlib, lz4

# TODO modorganizer-lootcli needs an overhaul as the api has changed alot
def bitness():
    return "x64" if config['architecture'] == "x86_64" else "Win32"
	
Project("LootApi") \
    .depend(Patch.Copy("loot_api.dll".format(loot_version, commit_id), os.path.join(config['__build_base_path'], "install", "bin", "loot"))
            .depend(github.Release("loot", "loot", loot_version, "loot-api_{}-0-{}_dev_{}".format(loot_version, commit_id, bitness()),"7z",tree_depth=1)
                    .set_destination("lootapi"))
            )


tl_repo = git.SuperRepository("modorganizer_super")

def gen_userfile_content(project):
    with open("CMakeLists.txt.user.template", 'r') as f:
        res = Formatter().vformat(f.read(), [], FormatDict({
            'build_dir'     : project['edit_path'],
            'environment_id': config['qt_environment_id'],
            'profile_name'  : config['qt_profile_name'],
            'profile_id'    : config['qt_profile_id']
        }))
        return res


cmake_parameters = [
    "-DCMAKE_BUILD_TYPE={}".format(config["build_type"]),
    "-DDEPENDENCIES_DIR={}/build".format(config["__build_base_path"]),
#	boost git version 	"-DBOOST_ROOT={}/build/boostgit",
    "-DBOOST_ROOT={}/build/boost_{}".format(config["__build_base_path"], config["boost_version"].replace(".", "_")),
    "-DCMAKE_INSTALL_PREFIX:PATH={}/install".format(config["__build_base_path"])
]


if config.get('optimize', False):
    cmake_parameters.append("-DOPTIMIZE_LINK_FLAGS=\"/LTCG /INCREMENTAL:NO /OPT:REF /OPT:ICF\"")


usvfs = Project("usvfs")

usvfs.depend(cmake.CMake().arguments(cmake_parameters +
                                     ["-DPROJ_ARCH={}".format("x86" if config['architecture'] == 'x86' else "x64")])
             .install()
            # TODO Not sure why this is required, will look into it at a later stage once we get the rest to build
                             .depend(github.Source(config['Main_Author'], "usvfs", "master")
                                     .set_destination("usvfs"))
                             .depend("AsmJit")
                             .depend("Udis86")
                             .depend("GTest")
                             .depend("fmtlib")
                             .depend("spdlog")
                             .depend("boost")
                     )

usvfs_32 = Project("usvfs_32")
if config['architecture'] == 'x86_64':
    usvfs.depend(cmake.CMake().arguments(cmake_parameters +
                                         ["-DPROJ_ARCH={}".format("x86" if config['architecture'] == 'x86' else "x64")])
                 .install()
                 # TODO Not sure why this is required, will look into it at a later stage once we get the rest to build
                 .depend(github.Source(config['Main_Author'], "usvfs", "master")
                         .set_destination("usvfs"))
                 .depend("AsmJit")
                 .depend("Udis86")
                 .depend("GTest")
                 .depend("fmtlib")
                 .depend("spdlog")
                 .depend("boost")
                 )
else:
    usvfs_32.depend(dummy.Success("usvfs_32"))

for author, git_path, path, branch, dependencies, Build in [
    (config['Main_Author'],               "modorganizer-game_features",     "game_features",     "master",          [],False),
    (config['Main_Author'],               "modorganizer-archive",           "archive",           "master",          ["7zip", "Qt5"],True),
    (config['Main_Author'],               "modorganizer-uibase",            "uibase",            "QT5.7",           ["Qt5", "boost"],True),
    (config['Main_Author'],               "modorganizer-lootcli",           "lootcli",           "master",          ["LootApi", "boost"],True),
    (config['Main_Author'],               "modorganizer-esptk",             "esptk",             "master",          ["boost"],True),
    (config['Main_Author'],               "modorganizer-bsatk",             "bsatk",             "master",          ["zlib","boost"],True),
    (config['Main_Author'],               "modorganizer-nxmhandler",        "nxmhandler",        "master",          ["Qt5"],True),
    (config['Main_Author'],               "modorganizer-helper",            "helper",            "master",          ["Qt5"],True),
    (config['Main_Author'],               "modorganizer-game_gamebryo",     "game_gamebryo",     "new_vfs_library", ["Qt5", "modorganizer-uibase",
                                                                                                                    "modorganizer-game_features", "lz4"],True),
    (config['Main_Author'],               "modorganizer-game_oblivion",     "game_oblivion",     "master",          ["Qt5", "modorganizer-uibase",
                                                                                                                    "modorganizer-game_gamebryo",
                                                                                                                    "modorganizer-game_features"],True),
    (config['Main_Author'],               "modorganizer-game_fallout3",     "game_fallout3",     "master",          ["Qt5", "modorganizer-uibase",
                                                                                                                    "modorganizer-game_gamebryo",
                                                                                                                    "modorganizer-game_features"],True),
    (config['Main_Author'],               "modorganizer-game_fallout4",     "game_fallout4",     "master",          ["Qt5", "modorganizer-uibase",
                                                                                                                    "modorganizer-game_gamebryo",
                                                                                                                    "modorganizer-game_features"],True),
    (config['Main_Author'],               "modorganizer-game_falloutnv",    "game_falloutnv",    "master",          ["Qt5", "modorganizer-uibase",
                                                                                                                    "modorganizer-game_gamebryo",
                                                                                                                    "modorganizer-game_features"],True),
    (config['Main_Author'],               "modorganizer-game_skyrim",       "game_skyrim",       "master",          ["Qt5", "modorganizer-uibase",
                                                                                                                    "modorganizer-game_gamebryo",
                                                                                                                    "modorganizer-game_features"],True),
    ("LePresidente",                      "modorganizer-game_skyrimSE",    "game_skyrimse",     "dev",        ["Qt5", "modorganizer-uibase",
                                                                                                                     "modorganizer-game_gamebryo",
                                                                                                                     "modorganizer-game_features"],True),
    (config['Main_Author'],               "modorganizer-tool_inieditor",    "tool_inieditor",    "master",          ["Qt5", "modorganizer-uibase"],True),
    (config['Main_Author'],               "modorganizer-tool_inibakery",    "tool_inibakery",    "master",          ["modorganizer-uibase"],True),
    (config['Main_Author'],               "modorganizer-tool_configurator", "tool_configurator", "QT5.7",          ["PyQt5"],True),
    (config['Main_Author'],               "modorganizer-preview_base",      "preview_base",      "master",          ["Qt5", "modorganizer-uibase"],True),
    (config['Main_Author'],               "modorganizer-diagnose_basic",    "diagnose_basic",    "master",          ["Qt5", "modorganizer-uibase"],True),
    (config['Main_Author'],               "modorganizer-check_fnis",        "check_fnis",        "master",          ["Qt5", "modorganizer-uibase"],True),
    (config['Main_Author'],               "modorganizer-installer_bain",    "installer_bain",    "QT5.7",          ["Qt5", "modorganizer-uibase"],True),
    (config['Main_Author'],               "modorganizer-installer_manual",  "installer_manual",  "QT5.7",          ["Qt5", "modorganizer-uibase"],True),
    (config['Main_Author'],               "modorganizer-installer_bundle",  "installer_bundle",  "master",          ["Qt5", "modorganizer-uibase"],True),
    (config['Main_Author'],               "modorganizer-installer_quick",   "installer_quick",   "master",          ["Qt5", "modorganizer-uibase"],True),
    (config['Main_Author'],               "modorganizer-installer_fomod",   "installer_fomod",   "master",          ["Qt5", "modorganizer-uibase"],True),
    (config['Main_Author'],               "modorganizer-installer_ncc",     "installer_ncc",     "master",          ["Qt5", "modorganizer-uibase", "NCC"],True),
    (config['Main_Author'],               "modorganizer-bsa_extractor",     "bsa_extractor",     "master",          ["Qt5", "modorganizer-uibase"],True),
    (config['Main_Author'],               "modorganizer-plugin_python",     "plugin_python",     "master",          ["Qt5", "boost", "Python", "modorganizer-uibase",
                                                                                                                    "sip"],True),
    (config['Main_Author'],               "githubpp",                        "githubpp",          "master",          ["Qt5"],True),
    (config['Main_Author'],               "modorganizer",                   "modorganizer",      "QT5.7",           ["Qt5", "boost",
                                                                                                                    "modorganizer-uibase", "modorganizer-archive",
                                                                                                                    "modorganizer-bsatk", "modorganizer-esptk",
                                                                                                                    "modorganizer-game_features",
                                                                                                                    "usvfs","githubpp", "NCC"], True),
    (config['Main_Author'],                 "modorganizer-WixInstaller",    "WixInstaller",      "master",          ["WixToolkit","modorganizer"], False),
]:
    build_step = cmake.CMake().arguments(cmake_parameters).install()

    build_installer = cmake.CMake().arguments(cmake_parameters).install()

    for dep in dependencies:
        build_step.depend(dep)

    project = Project(git_path)

    if Build:
        if not git_path == "modorganizer-WixInstaller":
            project.depend(build_step.depend(github.Source(author, git_path, branch, super_repository=tl_repo)
                                             .set_destination(path)))
        else:
            project.depend(build_installer.depend(github.Source(author, git_path, branch, super_repository=tl_repo)
                                             .set_destination(path)))
    else:
        project.depend(github.Source(author, git_path, branch, super_repository=tl_repo)
                       .set_destination(path))



def python_zip_collect(context):
    import libpatterns
    import glob
    from zipfile import ZipFile

    ip = os.path.join(config['__build_base_path'], "install", "bin")
    bp = python.python['build_path']

    with ZipFile(os.path.join(ip, "python27.zip"), "w") as pyzip:
        for pattern in libpatterns.patterns:
            for f in glob.iglob(os.path.join(bp, pattern)):
                pyzip.write(f, f[len(bp):])

    return True


Project("python_zip") \
    .depend(build.Execute(python_zip_collect)
            .depend("Python")
            )

