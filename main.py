import requests
import sys
from playwright.sync_api import Playwright, sync_playwright, expect
import os.path


def run(playwright: Playwright, current_ip) -> None:
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.customercontrolpanel.de/")
    page.get_by_placeholder("Customer number").fill("168881")
    page.get_by_placeholder("Password").fill("nw37_des8yt2up:z")
    page.get_by_role("button", name="Log in").click()
    page.wait_for_load_state("load")
    page.get_by_role("link", name=" Domains").click()
    page.wait_for_load_state("load")
    page.get_by_role("link", name="").click()
    page.wait_for_load_state("load")
    page.get_by_text("DNS", exact=True).click()
    page.wait_for_load_state("load")
    page.locator("input[name=\"record\\[64022085\\]\\[destination\\]\"]").fill(current_ip)
    page.locator("input[name=\"record\\[43525548\\]\\[destination\\]\"]").fill(current_ip)
    page.locator("input[name=\"record\\[78404034\\]\\[destination\\]\"]").fill(current_ip)
    page.get_by_role("button", name="DNS Records speichern").click()
    page.wait_for_load_state("load")
    page.get_by_role("button", name="ok").click()
    print("IP successfully changed.")

    # time.sleep(100) <- for debugging
    page.wait_for_load_state("load")
    page.get_by_role("link", name=" Abmelden").click()
    page.wait_for_load_state("load")

    # ---------------------
    context.close()
    browser.close()


def write_to_file(current_ip):
    with open("current_ip.txt", "w") as f:
        f.write(current_ip)


def get_external_ip():
    current_ip = requests.get('https://ifconfig.co/ip')
    if current_ip.status_code == 200:
        return current_ip.text.strip()
    sys.exit(1)


def compare_ip() -> None:
    current_ip: str = get_external_ip()
    if os.path.isfile("current_ip.txt"):
        with open("current_ip.txt", "r") as f:
            old_ip: str = f.readline().strip()
        if old_ip != current_ip:
            # Update file
            write_to_file(current_ip)
            print("Mismatching ips! Changing now...")
            # Update entries in ccp
            with sync_playwright() as playwright:
                run(playwright, current_ip)
        else:
            print("Your ip is already up to date! No changes required.")
    else:
        write_to_file(current_ip)
        with sync_playwright() as playwright:
            run(playwright, current_ip)


if __name__ == '__main__':
    compare_ip()
