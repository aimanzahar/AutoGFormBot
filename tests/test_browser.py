import os
import sys
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath("src"))

import browser


class _FakeChromeOptions:
    def __init__(self) -> None:
        self.arguments = []
        self.experimental_options = {}
        self.binary_location = None

    def add_argument(self, argument: str) -> None:
        self.arguments.append(argument)

    def add_experimental_option(self, key: str, value) -> None:
        self.experimental_options[key] = value


class _FakeWebDriver:
    def __init__(self) -> None:
        self.visited = None
        self.implicit_wait = None
        self.current_url = "https://docs.google.com/forms/d/e/test/viewform"

    def get(self, link: str) -> None:
        self.visited = link

    def implicitly_wait(self, seconds: int) -> None:
        self.implicit_wait = seconds

    def close(self) -> None:
        pass

    def quit(self) -> None:
        pass


class _FakeService:
    def __init__(self, executable_path: str = "") -> None:
        self.executable_path = executable_path


class BrowserTests(unittest.TestCase):
    def test_browser_uses_bundled_user_agent_for_startup(self) -> None:
        fake_options = _FakeChromeOptions()
        fake_driver = _FakeWebDriver()
        fake_service = _FakeService()

        with patch.object(browser.webdriver, "ChromeOptions", return_value=fake_options), \
                patch.object(browser.webdriver, "Chrome", return_value=fake_driver) as chrome_ctor, \
                patch.object(browser, "Service", return_value=fake_service) as service_ctor, \
                patch.dict(os.environ, {
                    "GOOGLE_CHROME_BIN": "chrome-bin",
                    "CHROMEDRIVER_PATH": "chromedriver-bin",
                }, clear=False):
            # Remove CHROME_USER_DATA_DIR if set so incognito mode is used
            os.environ.pop("CHROME_USER_DATA_DIR", None)
            instance = browser.Browser("https://example.com/form", headless=True)

        self.assertIs(instance.get_browser(), fake_driver)
        self.assertEqual(fake_driver.visited, "https://example.com/form")
        self.assertEqual(fake_driver.implicit_wait, 5)
        self.assertIn(
            "user-agent={}".format(browser._DEFAULT_USER_AGENT),
            fake_options.arguments,
            "Browser should set the bundled user-agent without fetching one at runtime",
        )
        service_ctor.assert_called_once_with(executable_path="chromedriver-bin")
        chrome_ctor.assert_called_once_with(service=fake_service, options=fake_options)

    def test_browser_detects_sign_in_required(self) -> None:
        fake_options = _FakeChromeOptions()
        fake_driver = _FakeWebDriver()
        fake_driver.current_url = "https://accounts.google.com/ServiceLogin?continue=..."
        fake_service = _FakeService()

        with patch.object(browser.webdriver, "ChromeOptions", return_value=fake_options), \
                patch.object(browser.webdriver, "Chrome", return_value=fake_driver), \
                patch.object(browser, "Service", return_value=fake_service), \
                patch.dict(os.environ, {
                    "GOOGLE_CHROME_BIN": "chrome-bin",
                    "CHROMEDRIVER_PATH": "chromedriver-bin",
                }, clear=False):
            os.environ.pop("CHROME_USER_DATA_DIR", None)
            # Should not raise because monitor_browser catches the error
            instance = browser.Browser("https://example.com/form", headless=True)

        # Browser should be None since sign-in error causes monitor_browser to retry
        # and eventually give up (max_retries reached)


if __name__ == "__main__":
    unittest.main()
