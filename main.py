from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time


class AutoCookie:
    def __init__(self, driver):
        self.driver = driver
        self.cookieBTN = driver.find_element(By.ID, "bigCookie")
        self.purchasing_interval = 5

    def open_options(self):
        option_button = self.driver.find_element(
            By.CSS_SELECTOR, "#prefsButton .subButton")
        option_button.click()

    def save_data(self):
        save_button = self.driver.find_element(By.LINK_TEXT, "Export save")
        save_button.click()
        save_data_el = self.driver.find_element(By.ID, "textareaPrompt")
        save_data = save_data_el.text
        with open("data/save_data", "w") as f:
            f.write(save_data)
        save_data_el.send_keys(Keys.ENTER)

    def load_data(self):
        with open("data/save_data", "r") as f:
            data = f.read()
        save_button = self.driver.find_element(By.LINK_TEXT, "Import save")
        save_button.click()
        text_el = self.driver.find_element(By.ID, "textareaPrompt")
        text_el.send_keys(data)
        text_el.send_keys(Keys.ENTER)
        time.sleep(5)

    def get_products(self):
        base_path = "div.product.unlocked.enabled"
        products = self.driver.find_elements(
            By.CSS_SELECTOR, base_path)
        num_of_products = len(products)

        return_products = []
        for i in range(num_of_products):
            product = {}
            product["btnId"] = f"product{i}"
            return_products.append(product)

        return return_products[::-1]

    def get_upgrades(self):
        base_path = "div.upgrade.enabled"
        upgrades = self.driver.find_elements(
            By.CSS_SELECTOR, base_path)
        num_of_upgrades = len(upgrades)

        return_upgrades = []
        for i in range(num_of_upgrades):
            upgrade = {}
            upgrade["btnId"] = f"upgrade{i}"
            return_upgrades.append(upgrade)

        return return_upgrades[::-1]

    def play(self):
        self.open_options()
        try:
            self.load_data()
        except FileNotFoundError:
            self.save_data()
        last_ts = time.time_ns()
        while True:
            self.cookieBTN.click()
            if (time.time_ns() - last_ts) > 1_000_000_000*self.purchasing_interval:
                last_ts = time.time_ns()

                enough_upgrade_money = True
                enough_product_money = True
                while enough_product_money or enough_upgrade_money:
                    time.sleep(0.1)
                    upgrades = self.get_upgrades()
                    if len(upgrades) > 0:
                        best_upgrade = upgrades[0]
                        best_upgrade_el = self.driver.find_element(
                            By.ID, best_upgrade["btnId"])
                        ActionChains(self.driver).click(
                            best_upgrade_el).perform()
                    else:
                        enough_upgrade_money = False
                    time.sleep(0.1)
                    products = self.get_products()
                    if len(products) > 0:
                        best_product = products[0]
                        best_product_el = self.driver.find_element(
                            By.ID, best_product["btnId"])
                        ActionChains(self.driver).click(
                            best_product_el).perform()
                    else:
                        enough_product_money = False

                self.save_data()


def main():
    driver = webdriver.Firefox()
    driver.get("localhost:2223")
    time.sleep(4)

    lang_select = driver.find_element(By.ID, "langSelect-EN")
    ActionChains(driver).move_to_element(lang_select).click().perform()

    time.sleep(2)

    autoCookie = AutoCookie(driver)
    autoCookie.play()


if __name__ == "__main__":
    main()
