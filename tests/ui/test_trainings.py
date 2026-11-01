from helpers.training import complete_training
from playwright.sync_api import Page
import pytest

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

def test_trainings(page: Page, user_with_dog, training_name):
    page.get_by_test_id("nav-desktop-train").click()
    page.get_by_test_id(training_name).click()
    complete_training(page)



