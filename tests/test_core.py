import io
import os
import sys
import unittest

from null_device_redirector import suppress_output


class SuppressOutputTests(unittest.TestCase):
    def test_stdout_is_redirected_to_devnull(self):
        with suppress_output():
            self.assertIsInstance(sys.stdout, io.IOBase)
            self.assertEqual(sys.stdout.name, os.devnull)
            print("this must not appear on stdout")

    def test_stderr_is_redirected_to_devnull(self):
        with suppress_output():
            self.assertEqual(sys.stderr.name, os.devnull)
            print("this must not appear on stderr", file=sys.stderr)

    def test_stdout_restored_after_block(self):
        original = sys.stdout
        with suppress_output():
            pass
        self.assertIs(sys.stdout, original)

    def test_stderr_restored_after_block(self):
        original = sys.stderr
        with suppress_output():
            pass
        self.assertIs(sys.stderr, original)

    def test_restoration_on_exception(self):
        original_out = sys.stdout
        original_err = sys.stderr

        class Marker(Exception):
            pass

        with self.assertRaises(Marker):
            with suppress_output():
                raise Marker("boom")

        self.assertIs(sys.stdout, original_out)
        self.assertIs(sys.stderr, original_err)

    def test_nested_blocks_restore_inner_then_outer(self):
        outer = sys.stdout

        with suppress_output():
            inner = sys.stdout
            self.assertIsNot(inner, outer)
            with suppress_output():
                self.assertIsNot(sys.stdout, inner)
                self.assertIsNot(sys.stdout, outer)
            self.assertIs(sys.stdout, inner)
        self.assertIs(sys.stdout, outer)

    def test_returns_context_manager_instance(self):
        cm = suppress_output()
        self.assertIs(cm.__enter__(), cm)

    def test_devnull_streams_are_distinct_between_blocks(self):
        first_handles = []
        with suppress_output() as cm1:
            first_handles.append(cm1._null)
        with suppress_output() as cm2:
            self.assertIsNot(cm2._null, first_handles[0])
        self.assertTrue(first_handles[0].closed)

    def test_single_fd_shared_between_stdout_and_stderr(self):
        with suppress_output() as cm:
            self.assertIs(sys.stdout, sys.stderr)
            self.assertIs(cm._null, sys.stdout)

    def test_pre_captured_reference_is_not_redirected(self):
        # Demonstrating the documented edge: a reference taken before entering the
        # block still writes to the original stdout because it was bound to the
        # stream object, not the module attribute.
        original_stdout = sys.stdout
        with suppress_output():
            self.assertIsNot(sys.stdout, original_stdout)
            self.assertIs(original_stdout, original_stdout)  # unchanged binding

    def test_double_exit_is_safe(self):
        with suppress_output() as cm:
            pass
        # Manually invoking __exit__ again must not raise or corrupt state.
        cm.__exit__(None, None, None)
