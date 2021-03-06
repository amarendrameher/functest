#!/usr/bin/env python

# Copyright (c) 2016 Orange and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0

"""Define the class required to fully cover testcase."""

import logging
import unittest

import mock

from functest.core import testcase

__author__ = "Cedric Ollivier <cedric.ollivier@orange.com>"


class TestCaseTesting(unittest.TestCase):
    """The class testing TestCase."""
    # pylint: disable=missing-docstring,too-many-public-methods

    _case_name = "base"
    _project_name = "functest"
    _published_result = "PASS"

    def setUp(self):
        self.test = testcase.TestCase(case_name=self._case_name,
                                      project_name=self._project_name)
        self.test.start_time = "1"
        self.test.stop_time = "2"
        self.test.result = 100
        self.test.details = {"Hello": "World"}

    def test_run_unimplemented(self):
        self.assertEqual(self.test.run(),
                         testcase.TestCase.EX_RUN_ERROR)

    @mock.patch('functest.utils.functest_utils.push_results_to_db',
                return_value=False)
    def _test_missing_attribute(self, mock_function=None):
        self.assertEqual(self.test.push_to_db(),
                         testcase.TestCase.EX_PUSH_TO_DB_ERROR)
        mock_function.assert_not_called()

    def test_missing_project_name(self):
        self.test.project_name = None
        self._test_missing_attribute()

    def test_missing_case_name(self):
        self.test.case_name = None
        self._test_missing_attribute()

    def test_missing_start_time(self):
        self.test.start_time = None
        self._test_missing_attribute()

    def test_missing_stop_time(self):
        self.test.stop_time = None
        self._test_missing_attribute()

    @mock.patch('functest.utils.functest_utils.push_results_to_db',
                return_value=True)
    def test_missing_details(self, mock_function=None):
        self.test.details = None
        self.assertEqual(self.test.push_to_db(),
                         testcase.TestCase.EX_OK)
        mock_function.assert_called_once_with(
            self._project_name, self._case_name, self.test.start_time,
            self.test.stop_time, self._published_result, self.test.details)

    @mock.patch('functest.utils.functest_utils.push_results_to_db',
                return_value=False)
    def test_push_to_db_failed(self, mock_function=None):
        self.assertEqual(self.test.push_to_db(),
                         testcase.TestCase.EX_PUSH_TO_DB_ERROR)
        mock_function.assert_called_once_with(
            self._project_name, self._case_name, self.test.start_time,
            self.test.stop_time, self._published_result, self.test.details)

    @mock.patch('functest.utils.functest_utils.push_results_to_db',
                return_value=True)
    def test_push_to_db(self, mock_function=None):
        self.assertEqual(self.test.push_to_db(),
                         testcase.TestCase.EX_OK)
        mock_function.assert_called_once_with(
            self._project_name, self._case_name, self.test.start_time,
            self.test.stop_time, self._published_result, self.test.details)

    @mock.patch('functest.utils.functest_utils.push_results_to_db',
                return_value=True)
    def test_push_to_db_res_ko(self, mock_function=None):
        self.test.result = 0
        self.assertEqual(self.test.push_to_db(),
                         testcase.TestCase.EX_OK)
        mock_function.assert_called_once_with(
            self._project_name, self._case_name, self.test.start_time,
            self.test.stop_time, 'FAIL', self.test.details)

    @mock.patch('functest.utils.functest_utils.push_results_to_db',
                return_value=True)
    def test_push_to_db_both_ko(self, mock_function=None):
        self.test.result = 0
        self.test.criteria = 0
        self.assertEqual(self.test.push_to_db(),
                         testcase.TestCase.EX_OK)
        mock_function.assert_called_once_with(
            self._project_name, self._case_name, self.test.start_time,
            self.test.stop_time, 'FAIL', self.test.details)

    def test_check_criteria_missing(self):
        self.test.criteria = None
        self.assertEqual(self.test.is_successful(),
                         testcase.TestCase.EX_TESTCASE_FAILED)

    def test_check_result_missing(self):
        self.test.result = None
        self.assertEqual(self.test.is_successful(),
                         testcase.TestCase.EX_TESTCASE_FAILED)

    def test_check_result_failed(self):
        # Backward compatibility
        # It must be removed as soon as TestCase subclasses
        # stop setting result = 'PASS' or 'FAIL'.
        self.test.result = 'FAIL'
        self.assertEqual(self.test.is_successful(),
                         testcase.TestCase.EX_TESTCASE_FAILED)

    def test_check_result_pass(self):
        # Backward compatibility
        # It must be removed as soon as TestCase subclasses
        # stop setting result = 'PASS' or 'FAIL'.
        self.test.result = 'PASS'
        self.assertEqual(self.test.is_successful(),
                         testcase.TestCase.EX_OK)

    def test_check_result_lt(self):
        self.test.result = 50
        self.assertEqual(self.test.is_successful(),
                         testcase.TestCase.EX_TESTCASE_FAILED)

    def test_check_result_eq(self):
        self.test.result = 100
        self.assertEqual(self.test.is_successful(),
                         testcase.TestCase.EX_OK)

    def test_check_result_gt(self):
        self.test.criteria = 50
        self.test.result = 100
        self.assertEqual(self.test.is_successful(),
                         testcase.TestCase.EX_OK)

    def test_check_result_zero(self):
        self.test.criteria = 0
        self.test.result = 0
        self.assertEqual(self.test.is_successful(),
                         testcase.TestCase.EX_TESTCASE_FAILED)

    def test_get_duration_start_ko(self):
        self.test.start_time = None
        self.assertEqual(self.test.get_duration(), "XX:XX")
        self.test.start_time = 0
        self.assertEqual(self.test.get_duration(), "XX:XX")

    def test_get_duration_end_ko(self):
        self.test.stop_time = None
        self.assertEqual(self.test.get_duration(), "XX:XX")
        self.test.stop_time = 0
        self.assertEqual(self.test.get_duration(), "XX:XX")

    def test_get_invalid_duration(self):
        self.test.start_time = 2
        self.test.stop_time = 1
        self.assertEqual(self.test.get_duration(), "XX:XX")

    def test_get_zero_duration(self):
        self.test.start_time = 2
        self.test.stop_time = 2
        self.assertEqual(self.test.get_duration(), "00:00")

    def test_get_duration(self):
        self.test.start_time = 1
        self.test.stop_time = 180
        self.assertEqual(self.test.get_duration(), "02:59")

    def test_str_project_name_ko(self):
        self.test.project_name = None
        self.assertIn("<functest.core.testcase.TestCase object at",
                      str(self.test))

    def test_str_case_name_ko(self):
        self.test.case_name = None
        self.assertIn("<functest.core.testcase.TestCase object at",
                      str(self.test))

    def test_str_pass(self):
        duration = '01:01'
        with mock.patch.object(self.test, 'get_duration',
                               return_value=duration), \
                mock.patch.object(self.test, 'is_successful',
                                  return_value=testcase.TestCase.EX_OK):
            message = str(self.test)
        self.assertIn(self._project_name, message)
        self.assertIn(self._case_name, message)
        self.assertIn(duration, message)
        self.assertIn('PASS', message)

    def test_str_fail(self):
        duration = '00:59'
        with mock.patch.object(self.test, 'get_duration',
                               return_value=duration), \
                mock.patch.object(
                    self.test, 'is_successful',
                    return_value=testcase.TestCase.EX_TESTCASE_FAILED):
            message = str(self.test)
        self.assertIn(self._project_name, message)
        self.assertIn(self._case_name, message)
        self.assertIn(duration, message)
        self.assertIn('FAIL', message)

    def test_create_snapshot(self):
        self.assertEqual(self.test.create_snapshot(),
                         testcase.TestCase.EX_OK)

    def test_clean(self):
        self.assertEqual(self.test.clean(), None)


class OSGCTestCaseTesting(unittest.TestCase):
    """The class testing OSGCTestCase."""
    # pylint: disable=missing-docstring

    def setUp(self):
        self.test = testcase.OSGCTestCase()

    @mock.patch('functest.utils.openstack_snapshot.main',
                side_effect=Exception)
    def test_create_snapshot_exc(self, mock_method=None):
        self.assertEqual(self.test.create_snapshot(),
                         testcase.TestCase.EX_RUN_ERROR)
        mock_method.assert_called_once_with()

    @mock.patch('functest.utils.openstack_snapshot.main', return_value=-1)
    def test_create_snapshot_ko(self, mock_method=None):
        self.assertEqual(self.test.create_snapshot(),
                         testcase.TestCase.EX_RUN_ERROR)
        mock_method.assert_called_once_with()

    @mock.patch('functest.utils.openstack_snapshot.main', return_value=0)
    def test_create_snapshot_env(self, mock_method=None):
        self.assertEqual(self.test.create_snapshot(),
                         testcase.TestCase.EX_OK)
        mock_method.assert_called_once_with()

    @mock.patch('functest.utils.openstack_clean.main', side_effect=Exception)
    def test_clean_exc(self, mock_method=None):
        self.assertEqual(self.test.clean(), None)
        mock_method.assert_called_once_with()

    @mock.patch('functest.utils.openstack_clean.main', return_value=-1)
    def test_clean_ko(self, mock_method=None):
        self.assertEqual(self.test.clean(), None)
        mock_method.assert_called_once_with()

    @mock.patch('functest.utils.openstack_clean.main', return_value=0)
    def test_clean(self, mock_method=None):
        self.assertEqual(self.test.clean(), None)
        mock_method.assert_called_once_with()


if __name__ == "__main__":
    logging.disable(logging.CRITICAL)
    unittest.main(verbosity=2)
