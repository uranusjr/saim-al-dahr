#!/usr/bin/env python
# -*- coding: utf-8 -*-

import doctest
import os

import six
from nose.plugins import Plugin

from .finders import SphinxDocTestFinder
from .sphinx import collect_sphinx_doctests


class CodeExecutor(object):
    """Global code executor to patch doctest's compile function dynamically.

    Based on the monkey-patching approach in Sphinx's doctest plugin.
    """
    compile_type = 'single'

    def compile(self, code, name, type, flags, dont_inherit):
        return compile(code, name, self.compile_type, flags, dont_inherit)


executor = CodeExecutor()


class DocTestCase(doctest.DocTestCase):
    """Custom DocTestCast that does not clear globals after tests are run.

    Built-in doctest's implemetation clears test's globals on tear down. We
    override the method to prevent that.
    """
    def tearDown(self):
        if self._dt_tearDown is not None:
            self._dt_tearDown(self._dt_test)


class SphinxDoctest(Plugin):
    """The plugin object to be registered into Nose.
    """
    name = 'sphinx'
    enabled = True

    def options(self, parser, env):
        """Setup command-line options to parse.

        Overriden from Plugin.
        """
        super(SphinxDoctest, self).options(parser, env)
        parser.add_option(
            '--sphinx-doc-dir', dest='sphinx_doc_dir',
            default=env.get('NOSE_SPHINX_DOC_DIR', 'docs'),
            help=('Root directory of the Sphinx documentation. Default is '
                  '"docs". [NOSE_SPHINX_DOC_DIR]'),
        )
        parser.add_option(
            '--sphinx-conf-dir', dest='sphinx_conf_dir',
            default=env.get('NOSE_SPHINX_CONF_DIR', None),
            help=('Directory of the Sphinx documentation containing '
                  '"conf.py". Defaults to the Sphinx root directory. '
                  '[NOSE_SPHINX_CONF_DIR]'),
        )
        parser.add_option(
            '--sphinx-build-dir', dest='sphinx_build_dir',
            default=env.get('NOSE_SPHINX_BUILD_DIR', '_build'),
            help=('Path to the Sphinx build directory, relative to the root '
                  'documentation directory. Default is "_build". '
                  '[NOSE_SPHINX_BUILD_DIR]'),
        )

    def configure(self, options, config):
        """Configure the plugin from parsed command-line options.

        Overriden from Plugin.
        """
        self.srcdir = options.sphinx_doc_dir
        self.confdir = options.sphinx_conf_dir
        if self.confdir is None:
            self.confdir = self.srcdir
        self.builddir = os.path.join(self.srcdir, options.sphinx_build_dir)

    def begin(self):
        """Run before start of "the" test.

        Overriden from Plugin.
        """
        # Monkey-patch doctest's compile to provide more functionality.
        # Based on Sphinx's implementation.
        try:
            self.old_compile = doctest.compile
        except AttributeError:
            pass
        doctest.compile = executor.compile

        # Monkey-patch doctest's DocTestCase to prevent globals being cleared.
        # See DocTestCase's implementation.
        self.DocTestCase = doctest.DocTestCase
        doctest.DocTestCase = DocTestCase

    def finalize(self, result):
        """Run after end of "the" test.

        Overriden from Plugin.
        """
        # See begin().
        try:
            doctest.compile = self.old_compile
        except AttributeError:
            del doctest.compile
        doctest.DocTestCase = self.DocTestCase

    def wantDirectory(self, dirname):
        """Specify directories we want.

        Overriden from Plugin. We want directories that contain a valid Sphinx
        doc tree. No preferences about others.
        """
        if self._path_has_sphinx(dirname):
            return True
        return None

    def loadTestsFromDir(self, path):
        """Load tests from Sphinx subdirectory in the given directory.

        Overriden from Plugin.
        """
        # We only run for directories we really want.
        if not self.wantDirectory(path):
            return

        groups = collect_sphinx_doctests(**self._get_sphinx_dirs(path))

        for docname, group in groups:
            # All tests in a group share their global context.
            group.globs = {}

            def build_setup_teardown(fname, group, before=False, after=False):

                def func(test):
                    # All tests in a group share their global context.
                    test.globs = group.globs

                    # Set type for the monkey-patched compile function.
                    executor.compile_type = test.compile_type

                    # Run setup/cleanup in the current context.
                    for setup_code in group.setup:
                        code_name = '<{kind} {docname}:{name}>'.format(
                            kind=fname, docname=docname, name=group.name,
                        )
                        six.exec_(
                            compile(setup_code.code, code_name, 'exec', 0, 1),
                            test.globs,
                        )

                func.__name__ = fname
                return func

            suite = doctest.DocTestSuite(
                test_finder=SphinxDocTestFinder(docname, group),
                setUp=build_setup_teardown('setup', group),
                tearDown=build_setup_teardown('teardown', group),
            )
            yield suite

    def _get_sphinx_dirs(self, path):
        """Resolve Sphinx directories with the given path.
        """
        return {
            key: os.path.join(os.path.abspath(path), getattr(self, key))
            for key in ('srcdir', 'confdir', 'builddir',)
        }

    def _path_has_sphinx(self, path):
        """Check for Sphinx directories in path.
        """
        sphinx_dirs = self._get_sphinx_dirs(path)
        return all(os.path.exists(p) for p in sphinx_dirs.values())
