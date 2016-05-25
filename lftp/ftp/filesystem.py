"""
This module contains UnifiedFilesystem and related functions, which provide a
unified view of the content stored across multiple filesystems.
"""

from __future__ import unicode_literals

import os
import re
import errno

from functools import wraps

from pyftpdlib.filesystems import AbstractedFS, FilesystemError

from ..utils.string import to_unicode


def normpaths(*paths):
    """ Join `paths` and normalize the result """
    return os.path.normpath(os.path.join(*paths))



def raise_path_error(path):
    raise OSError(errno.ENOENT, 'No such file or directory {}'.format(path), path)


class UnifiedFilesystem(AbstractedFS):
    """
    This class provides a unified view of a filesystem, made up of
    all files and directories present at :py:attr:`basepaths`. This is
    intended to be set as :py:attr:`abstracted_fs` for
    :py:mod:`pyftpdlib.handlers.FTPHandler`

    This class overrides relevant filesystem related operations of
    :py:class:`AbstractedFS` to provide the unified view.
    """
    VIRTUAL_ROOT = '.'

    basepaths = []

    blacklist = None

    def __init__(self, *args, **kwargs):
        super(UnifiedFilesystem, self).__init__(*args, **kwargs)

        if self.blacklist:
            self._blacklist_rx = [
                re.compile(patt, re.IGNORECASE) for patt in self.blacklist]

    def virtualize_path(func):
        """
        This decorator ensures that the `path` argument passed to the wrapped
        functions are converted to virtual paths if original `path` passed is
        an absolute path.
        """
        @wraps(func)
        def wrapper(self, path, *args, **kwargs):
            path = to_unicode(path)
            if os.path.isabs(path):
                virtual_path = self.get_virtual_path(path)
            else:
                virtual_path = path
            return func(self, virtual_path, *args, **kwargs)
        return wrapper

    def stdlib_wrapper(stdlib_func, exception=True):
        """
        This decorator provides a handy way to call stdlib functions which
        accept one path argument.
        """
        def decorator(func):
            @wraps(func)
            def wrapper(self, path, *args, **kwargs):
                for basepath in self.basepaths:
                    full_path = normpaths(basepath, path)
                    if os.path.exists(full_path):
                        return stdlib_func(full_path)
                if exception:
                    raise_path_error(path)
            return wrapper
        return decorator

    @virtualize_path
    def validpath(self, path):
        """
        Checks whether the path exists under any of the :py:attr:`basespaths`

        If the path is a symbolic link, it is resolved to check its final
        destination.

        Paths which escape out of :py:attr:`basepaths` are considered to be
        invalid.
        """
        for basepath in self.basepaths:
            fullpath = os.path.realpath(normpaths(basepath, path))
            if not fullpath.endswith(os.sep):
                fullpath += os.sep
            if not basepath.endswith(os.sep):
                basepath += os.sep
            basepath = os.path.realpath(basepath)
            if fullpath[0:len(basepath)] == basepath:
                return True
        return False

    @virtualize_path
    def open(self, path, mode):
        """
        Wrapper for `open`, which resolves `path` by extracting the virtual
        path and generating the actual path.
        """
        for basepath in self.basepaths:
            fullpath = normpaths(basepath, path)
            if os.path.isfile(fullpath):
                return open(fullpath, mode)
        raise_path_error(path)

    @virtualize_path
    def chdir(self, path):
        """
        Change the current directory for the user, extracting the virtual path
        and moving to the actual path.
        """
        for basepath in self.basepaths:
            fullpath = normpaths(basepath, path)
            if os.path.isdir(fullpath) and not self.is_blacklisted(path):
                super(UnifiedFilesystem, self).chdir(fullpath)
                return
        raise_path_error(path)

    def listdir(self, path):
        """
        Returns a list of files present at ``path``. The virtual path is
        extracted and the all the entries present under all
        :py:attr:`basepaths` are listed.

        The listing is not ordered in any particular order and does not contain
        '.' or '..'
        """
        virtual_path = self.get_virtual_path(path)
        listing = []
        exists = False
        for basepath in self.basepaths:
            full_path = normpaths(basepath, virtual_path)
            if os.path.exists(full_path):
                exists = True
                # Filter out blacklisted entries from directory listing
                entries = [p for p in os.listdir(full_path)
                           if not self.is_blacklisted(os.path.join(virtual_path, p))]
                listing.extend(entries)
        # The :py:attr:`basepaths` directories should not raise an exception
        if virtual_path != self.VIRTUAL_ROOT and not exists:
            raise_path_error(path)
        # Ensure unique listing entries by creating a set from listing and
        # converting it back to a list
        listing = list(set(listing))
        return listing

    @virtualize_path
    @stdlib_wrapper(os.stat)
    def stat(self, path):
        """
        Wrapper for :py:func:`os.stat`, which resolves `path` by extracting the
        virtual path and generating the actual path.
        """
        pass

    @virtualize_path
    @stdlib_wrapper(os.lstat)
    def lstat(self, path):
        """
        Wrapper for :py:func:`os.lstat`, which resolves `path` by extracting
        the virtual path and generating the actual path.
        """
        pass

    @virtualize_path
    @stdlib_wrapper(os.readlink)
    def readlink(self, path):
        """
        Wrapper for :py:func:`os.readlink`, which resolves `path` by extracting
        the virtual path and generating the actual path.
        """
        pass

    @virtualize_path
    @stdlib_wrapper(os.path.isfile, exception=False)
    def isfile(self, path):
        """
        Wrapper for :py:func:`os.path.isfile`, which resolves `path` by
        extracting the virtual path and generating the actual path.
        """
        pass

    @virtualize_path
    @stdlib_wrapper(os.path.islink, exception=False)
    def islink(self, path):
        """
        Wrapper for :py:func:`os.path.islink`, which resolves `path` by
        extracting the virtual path and generating the actual path.
        """
        pass

    def isdir(self, path):
        """
        Wrapper for :py:func:`os.path.isdir`, which resolves `path` by
        extracting the virtual path and generating the actual path.
        """
        if path in self.basepaths:
            return True
        else:
            return self._isdir(path)

    @virtualize_path
    @stdlib_wrapper(os.path.isdir, exception=False)
    def _isdir(self, path):
        """
        Wrapper for :py:func:`os.path.isdir`, which resolves `path` by
        extracting the virtual path and generating the actual path.
        """
        pass

    @virtualize_path
    @stdlib_wrapper(os.path.getsize)
    def getsize(self, path):
        """
        Wrapper for :py:func:`os.path.getsize`, which resolves `path` by
        extracting the virtual path and generating the actual path.
        """
        pass

    @virtualize_path
    @stdlib_wrapper(os.path.getmtime)
    def getmtime(self, path):
        """
        Wrapper for :py:func:`os.path.getmtime`, which resolves `path` by
        extracting the virtual path and generating the actual path.
        """
        pass

    def mkdir(self, path):
        raise FilesystemError('Unsupported operation')

    def rmdir(self, path):
        raise FilesystemError('Unsupported operation')

    def remove(self, path):
        raise FilesystemError('Unsupported operation')

    def rename(self, src, dst):
        raise FilesystemError('Unsupported operation')

    def chmod(self, path, mode):
        raise FilesystemError('Unsupported operation')

    def mkstemp(suffix='', prefix='', dir=None, mode='wb'):
        raise FilesystemError('Unsupported operation')

    def get_virtual_path(self, path):
        """
        Checks `path` against each :py:attr:`basepaths` and extracts the
        virtual path, i.e. the path relative to matched basepath, or None.
        """
        for basepath in self.basepaths:
            if os.path.commonprefix([path, basepath]) == basepath:
                # Get the rest of the path, discarding till basepath and `/`
                rest_path = path[len(basepath) + 1:]
                return rest_path or self.VIRTUAL_ROOT
        return None

    def is_blacklisted(self, virtual_path):
        """ Returns `True` if `virtual_path` matches the blacklisted paths """

        if not self.blacklist:
            return False
        # Strip out any leading path component characters
        if virtual_path.startswith(self.VIRTUAL_ROOT):
            virtual_path = virtual_path[1:]
        virtual_path = virtual_path.lstrip('/')

        return any((p.search(virtual_path) for p in self._blacklist_rx))
