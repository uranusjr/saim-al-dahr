#!/usr/bin/env python
# -*- coding: utf-8 -*-

import doctest

parser = doctest.DocTestParser()


class SphinxDocTestFinder(object):
    """Doctest finder for doctest.DocTestSuite.
    """
    def __init__(self, filename, group):
        super(SphinxDocTestFinder, self).__init__()
        self.filename = filename
        self.group = group

    def find(self, obj, name=None, module=None, globs=None, extraglobs=None):
        """Hook called by the test runner to find tests.

        In reality (within context of Nose and Sphinx), almost all parameters
        provided are not used. Tests are constructed from Sphinx doctest groups
        provided in __init__.
        """
        # Tests are going to be collected here.
        tests = []

        # Based on Sphinx's doctest collecting logic, but instead of running
        # the tests directly, we create DocTest objects and return them for
        # nose to collect and run.
        # Comments here belong to Sphinx if they are "written like this".
        # My own comments "Capitalize the first letter and have a punctuation
        # mark at the end."
        for code in self.group.tests:
            if len(code) == 1:
                # ordinary doctests (code/output interleaved)
                try:
                    test = parser.get_doctest(
                        code[0].code, {}, self.group.name, self.filename,
                        code[0].lineno,
                    )
                except Exception:
                    # TODO: Warn about invalid doctest?
                    continue
                if not test.examples:
                    continue
                for example in test.examples:
                    # apply directive's comparison options
                    new_opt = code[0].options.copy()
                    new_opt.update(example.options)
                    example.options = new_opt
                test.compile_type = 'single'
            else:
                # testcode and output separate
                output = code[1] and code[1].code or ''
                options = code[1] and code[1].options or {}
                # disable <BLANKLINE> processing as it is not needed
                options[doctest.DONT_ACCEPT_BLANKLINE] = True
                # find out if we're testing an exception
                m = parser._EXCEPTION_RE.match(output)
                if m:
                    exc_msg = m.group('msg')
                else:
                    exc_msg = None
                example = doctest.Example(
                    code[0].code, output, exc_msg=exc_msg,
                    lineno=code[0].lineno, options=options,
                )
                # The test's globals will be swapped out later during test
                # setup, so the globs parameter here has no use at all, and an
                # empty dict is enough.
                test = doctest.DocTest(
                    [example], {}, self.group.name, self.filename,
                    code[0].lineno, None,
                )
                test.compile_type = 'exec'
            test.group = self.group
            tests.append(test)

        # Sort tests by names alphabetically, for consistency with
        # doctest.DocTestFinder's behavior.
        tests.sort()
        return tests
