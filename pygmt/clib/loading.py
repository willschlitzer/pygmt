"""
Utility functions to load libgmt as ctypes.CDLL.

The path to the shared library can be found automatically by ctypes or set
through the GMT_LIBRARY_PATH environment variable.
"""
import os
import sys
import ctypes
from ctypes.util import find_library
import subprocess as sp

from ..exceptions import GMTOSError, GMTCLibError, GMTCLibNotFoundError


def load_libgmt():
    """
    Find and load ``libgmt`` as a :py:class:`ctypes.CDLL`.

    By default, will look for the shared library in the directory specified by
    the environment variable ``GMT_LIBRARY_PATH``. If it's not set, will let
    ctypes try to find the library.

    Returns
    -------
    :py:class:`ctypes.CDLL` object
        The loaded shared library.

    Raises
    ------
    GMTCLibNotFoundError
        If there was any problem loading the library (couldn't find it or
        couldn't access the functions).

    """
    lib_fullnames = clib_full_names()
    error = True
    for libname in lib_fullnames:
        try:
            libgmt = ctypes.CDLL(libname)
            check_libgmt(libgmt)
            error = False
            break
        except OSError as err:
            error = err
    if error:
        raise GMTCLibNotFoundError(
            "Error loading the GMT shared library '{}':".format(
                ", ".join(lib_fullnames)
            )
        )
    return libgmt


def clib_names(os_name):
    """
    Return the name of GMT's shared library for the current OS.

    Parameters
    ----------
    os_name : str
        The operating system name as given by ``sys.platform``.

    Returns
    -------
    libnames : list of str
        List of possible names of GMT's shared library.

    """
    if os_name.startswith("linux"):
        libnames = ["libgmt.so"]
    elif os_name == "darwin":  # Darwin is macOS
        libnames = ["libgmt.dylib"]
    elif os_name == "win32":
        libnames = ["gmt.dll", "gmt_w64.dll", "gmt_w32.dll"]
    elif os_name.startswith("freebsd"):  # FreeBSD
        libnames = ["libgmt.so"]
    else:
        raise GMTOSError(f'Operating system "{sys.platform}" not supported.')
    return libnames


def clib_full_names(env=None):
    """
    Return the full path of GMT's shared library for the current OS.

    Parameters
    ----------
    env : dict or None
        A dictionary containing the environment variables. If ``None``, will
        default to ``os.environ``.

    Returns
    -------
    lib_fullnames: list of str
        List of possible full names of GMT's shared library.

    """
    if env is None:
        env = os.environ

    libnames = clib_names(os_name=sys.platform)  # e.g. libgmt.so, libgmt.dylib, gmt.dll

    # list of libraries paths to search, sort by priority from high to low
    lib_fullnames = []

    # Search for libraries in GMT_LIBRARY_PATH if defined.
    libpath = env.get("GMT_LIBRARY_PATH", "")  # e.g. $HOME/miniconda/envs/pygmt/lib
    if libpath:
        for libname in libnames:
            lib_fullnames.append(os.path.join(libpath, libname))

    # Search for the library returned by command "gmt --show-library"
    try:
        lib_fullpath = sp.check_output(
            ["gmt", "--show-library"], encoding="utf-8"
        ).rstrip("\n")
        lib_fullnames.append(lib_fullpath)
    except FileNotFoundError:  # command not found
        pass

    # Search for DLLs in PATH (done by calling "find_library")
    if sys.platform == "win32":
        for libname in libnames:
            libfullpath = find_library(libname)
            if libfullpath:
                lib_fullnames.append(libfullpath)

    # Search for library names in the system default path [the lowest priority]
    lib_fullnames.extend(libnames)

    return lib_fullnames


def check_libgmt(libgmt):
    """
    Make sure that libgmt was loaded correctly.

    Checks if it defines some common required functions.

    Does nothing if everything is fine. Raises an exception if any of the
    functions are missing.

    Parameters
    ----------
    libgmt : :py:class:`ctypes.CDLL`
        A shared library loaded using ctypes.

    Raises
    ------
    GMTCLibError

    """
    # Check if a few of the functions we need are in the library
    functions = ["Create_Session", "Get_Enum", "Call_Module", "Destroy_Session"]
    for func in functions:
        if not hasattr(libgmt, "GMT_" + func):
            msg = f"Error loading libgmt. Couldn't access function GMT_{func}."
            raise GMTCLibError(msg)
