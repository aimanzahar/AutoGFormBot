import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath("src"))

import handler


class _SignInBrowser:
    def __init__(self, issue: str) -> None:
        self._issue = issue

    def get_sign_in_message(self) -> str:
        return self._issue


class _FailingProcessor:
    def __init__(self, issue: str) -> None:
        self._browser = _SignInBrowser(issue)

    def get_question(self, start: bool):
        return False

    def get_browser(self) -> _SignInBrowser:
        return self._browser


class HandlerTests(unittest.TestCase):
    def test_obtain_question_shows_auth_guidance_without_bug_banner(self) -> None:
        issue = (
            "This Google Form requires a signed-in Google account.\n"
            "Run the bot with an authenticated Chrome profile first."
        )
        processor = _FailingProcessor(issue)

        message = MagicMock()
        callback_query = MagicMock()
        callback_query.message = message

        update = MagicMock()
        update.callback_query = callback_query
        update.message = None

        context = MagicMock()
        context.user_data = {handler._PROCESSOR: processor}
        context.job_queue.jobs.return_value = []

        with patch.object(handler, "FormProcessor", _FailingProcessor), \
                patch.object(handler, "_show_loading_screen"):
            state = handler._obtain_question(update, context)

        self.assertEqual(state, handler._STOPPING)
        message.reply_text.assert_called_once()
        sent_text = message.reply_text.call_args.args[0]
        self.assertIn("This Google Form requires", sent_text)
        self.assertNotIn("BUG DETECTED IN BOT", sent_text)


if __name__ == "__main__":
    unittest.main()
