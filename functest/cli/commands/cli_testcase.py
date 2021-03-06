#!/usr/bin/env python
#
# jose.lausuch@ericsson.com
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
#

""" global variables """

import os
import pkg_resources

import click

import functest.ci.tier_builder as tb
from functest.utils.constants import CONST
import functest.utils.functest_utils as ft_utils
import functest.utils.functest_vacation as vacation


class CliTestcase(object):

    def __init__(self):
        self.tiers = tb.TierBuilder(
            CONST.__getattribute__('INSTALLER_TYPE'),
            CONST.__getattribute__('DEPLOY_SCENARIO'),
            pkg_resources.resource_filename('functest', 'ci/testcases.yaml'))

    def list(self):
        summary = ""
        for tier in self.tiers.get_tiers():
            for test in tier.get_tests():
                summary += (" %s\n" % test.get_name())
        click.echo(summary)

    def show(self, testname):
        description = self.tiers.get_test(testname)
        if description is None:
            click.echo("The test case '%s' does not exist or is not supported."
                       % testname)

        click.echo(description)

    @staticmethod
    def run(testname, noclean=False, report=False):

        flags = ""
        if noclean:
            flags += "-n "
        if report:
            flags += "-r "

        if testname == 'vacation':
            vacation.main()
        elif not os.path.isfile(CONST.__getattribute__('env_active')):
            click.echo("Functest environment is not ready. "
                       "Run first 'functest env prepare'")
        else:
            tests = testname.split(",")
            for test in tests:
                cmd = "run_tests {}-t {}".format(flags, test)
                ft_utils.execute_command(cmd)
