import os
import sys
import unittest
import warnings
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath("src"))

import handler


class StartUpdaterTests(unittest.TestCase):
    def test_defaults_to_polling_when_webhook_url_is_missing(self) -> None:
        updater = MagicMock()

        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("WEBHOOK_URL", None)
            os.environ.pop("PORT", None)
            handler._start_updater(updater, "token-123")

        updater.start_polling.assert_called_once_with()
        updater.start_webhook.assert_not_called()

    def test_uses_webhook_when_webhook_url_is_configured(self) -> None:
        updater = MagicMock()

        with patch.dict(os.environ, {"WEBHOOK_URL": "https://example.com/", "PORT": "9000"}, clear=False):
            handler._start_updater(updater, "token-123")

        updater.start_webhook.assert_called_once_with(
            listen="0.0.0.0",
            port=9000,
            url_path="token-123",
            webhook_url="https://example.com/token-123"
        )
        updater.start_polling.assert_not_called()

    def test_main_does_not_emit_conversationhandler_callback_warning(self) -> None:
        updater = MagicMock()
        updater.dispatcher = MagicMock()

        with patch.dict(os.environ, {"TELEGRAM_TOKEN": "token-123"}, clear=False), \
                patch.object(handler, "Updater", return_value=updater), \
                patch.object(handler, "_start_updater"):
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                handler.main()

        messages = [str(warning.message) for warning in caught]
        self.assertFalse(
            any("If 'per_message=False', 'CallbackQueryHandler' will not be tracked" in message
                for message in messages),
            "main() should not emit the known ConversationHandler callback-tracking warning",
        )


if __name__ == "__main__":
    unittest.main()
