import os
import sys
import unittest
from collections import deque
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath("src"))

import processor


class _LazySignInBrowser:
    def __init__(self) -> None:
        self.refreshed = False

    def refresh_sign_in_status(self) -> bool:
        self.refreshed = True
        return True

    def requires_sign_in(self) -> bool:
        return False


class FormProcessorTests(unittest.TestCase):
    def test_get_question_stops_when_form_requires_sign_in(self) -> None:
        instance = processor.FormProcessor.__new__(processor.FormProcessor)
        instance._BROWSER = _LazySignInBrowser()
        instance._CURRENT = None
        instance._QUESTIONS = deque()

        self.assertFalse(instance.get_question(start=True))
        self.assertTrue(instance._BROWSER.refreshed)

    def test_answer_question_stops_when_form_requires_sign_in(self) -> None:
        instance = processor.FormProcessor.__new__(processor.FormProcessor)
        instance._BROWSER = _LazySignInBrowser()
        instance._CURRENT = MagicMock()
        instance._QUESTIONS = deque()

        self.assertFalse(instance.answer_question("hello"))
        self.assertTrue(instance._BROWSER.refreshed)
        instance._CURRENT.answer.assert_not_called()


if __name__ == "__main__":
    unittest.main()
