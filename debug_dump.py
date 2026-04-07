"""Debug script to dump question element HTML from a Google Form."""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time

FORM_URL = os.environ.get("FORM_URL", "https://docs.google.com/forms/d/e/1FAIpQLSeHlr17mCe0VQwbxCKdRTx_heGU3O2obxqDIf87oCP2yf6aSw/viewform")

options = webdriver.ChromeOptions()
options.binary_location = os.environ.get("GOOGLE_CHROME_BIN", "")
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--incognito")

service = Service(executable_path=os.environ.get("CHROMEDRIVER_PATH", ""))
driver = webdriver.Chrome(service=service, options=options)
driver.implicitly_wait(10)

print(f"Loading: {FORM_URL}")
driver.get(FORM_URL)
time.sleep(5)

print(f"Current URL: {driver.current_url}")
print(f"Page title: {driver.title}")
print()

# Try multiple selectors for question containers
selectors = [
    ("CLASS_NAME", "freebirdFormviewerComponentsQuestionBaseRoot"),
    ("CSS_SELECTOR", "div[role='listitem']"),
    ("CSS_SELECTOR", "div[data-params]"),
    ("CSS_SELECTOR", "[data-item-id]"),
    ("CSS_SELECTOR", ".Qr7Oae"),  # known modern class
]

for method, sel in selectors:
    by = getattr(By, method)
    elements = driver.find_elements(by, sel)
    print(f"Selector ({method}, {sel!r}): found {len(elements)} elements")
    for i, el in enumerate(elements):
        outer = el.get_attribute("outerHTML")
        # Truncate for readability
        if len(outer) > 2000:
            outer = outer[:2000] + "... [TRUNCATED]"
        print(f"\n--- Element {i} ({method}: {sel}) ---")
        print(outer)
    print()

# Also dump all input elements
inputs = driver.find_elements(By.CSS_SELECTOR, "input, textarea, select")
print(f"\nAll input/textarea/select elements: {len(inputs)}")
for i, inp in enumerate(inputs):
    tag = inp.tag_name
    typ = inp.get_attribute("type") or ""
    name = inp.get_attribute("name") or ""
    aria = inp.get_attribute("aria-label") or ""
    cls = inp.get_attribute("class") or ""
    role = inp.get_attribute("role") or ""
    print(f"  [{i}] <{tag} type='{typ}' name='{name}' aria-label='{aria}' role='{role}' class='{cls[:100]}'>")

# Dump role-based elements
for role in ["checkbox", "radio", "listbox", "option", "textbox", "combobox"]:
    els = driver.find_elements(By.CSS_SELECTOR, f"[role='{role}']")
    if els:
        print(f"\nElements with role='{role}': {len(els)}")
        for i, el in enumerate(els[:5]):
            aria = el.get_attribute("aria-label") or ""
            cls = el.get_attribute("class") or ""
            data_val = el.get_attribute("data-value") or el.get_attribute("data-answer-value") or ""
            print(f"  [{i}] aria-label='{aria}' data-value='{data_val}' class='{cls[:120]}'")

driver.quit()
print("\nDone.")
