"""
This module contains UnifiedFilesystem and related functions, which provide a
unified view of the content stored across multiple filesystems.
"""

from __future__ import unicode_literals

import os

from functools import wraps

from pyftpdlib.filesystems import AbstractedFS, FilesystemError

from ..utils.string import to_unicode


def prepare_filesystem_class(basepaths):
    """
    Generate a new type based on :py:class:`UnifiedFilesystem` and the
    specified `basepaths`
    """
    return type(b'FunctionalUnifiedFilesystem', (UnifiedFilesystem,),
                {'basepaths': basepaths})


def normpaths(*paths):
    """ Join `paths` and normalize the result """
    return os.path.normpath(os.path.join(*paths))


class UnifiedFilesystem(AbstractedFS):
    """
    This class provides a unified view of a filesystem, made up of
    all files and directories present at :py:attr:`basepaths`. This is
    intended to be set as :py:attr:`abstracted_fs` for
    :py:mod:`pyftpdlib.handlers.FTPHandler`

    This class overrides relevant filesystem related operations of
    :py:class:`AbstractedFS` to provide the unified view.
    """
    basepaths = []

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

    def stdlib_wrapper(stdlib_func):
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
                raise OSError('No such file or directory {}'.format(path))
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
        raise OSError(u'No such file or directory: {}'.format(path))

    @virtualize_path
    def chdir(self, path):
        """
        Change the current directory for the user, extracting the virtual path
        and moving to the actual path.
        """
        for basepath in self.basepaths:
            fullpath = normpaths(basepath, path)
            if os.path.isdir(fullpath):
                super(UnifiedFilesystem, self).chdir(fullpath)
                return
        raise OSError(u'No such file or directory: {}'.format(path))

    @virtualize_path
    def listdir(self, path):
        """
        Returns a list of files present at ``path``. The virtual path is
        extracted and the all the entries present under all
        :py:attr:`basepaths` are listed.

        The listing is not ordered in any particular order and does not contain
        '.' or '..'
        """
        listing = []
        exists = False
        for basepath in self.basepaths:
            full_path = normpaths(basepath, path)
            if os.path.exists(full_path):
                exists = True
                listing.extend(os.listdir(full_path))
        if not exists:
            raise OSError(u'No such file or directory: {}'.format(path))
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
    @stdlib_wrapper(os.path.isfile)
    def isfile(self, path):
        """
        Wrapper for :py:func:`os.path.isfile`, which resolves `path` by
        extracting the virtual path and generating the actual path.
        """
        pass

    @virtualize_path
    @stdlib_wrapper(os.path.islink)
    def islink(self, path):
        """
        Wrapper for :py:func:`os.path.islink`, which resolves `path` by
        extracting the virtual path and generating the actual path.
        """
        pass

    @virtualize_path
    @stdlib_wrapper(os.path.isdir)
    def isdir(self, path):
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
                return rest_path or '.'
        return None
