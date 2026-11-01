from dotenv import load_dotenv
from helpers.training import complete_training
from playwright.sync_api import Page, expect
import uuid
import pytest
import time
load_dotenv()

@pytest.mark.parametrize(
    "training_name",
    [
        "link-train-Sit",
        "link-train-Down",
        "link-train-Stay",
        "link-train-Come",
        "link-train-Place",
        "link-train-Leave-20It",
    ],
)

#def test_tranings(page: Page, login, training_name):
def test_tranings(page: Page, user_with_dog, training_name):
    page.get_by_test_id("nav-desktop-train").click()
    page.get_by_test_id(training_name).click()
    complete_training(page)



