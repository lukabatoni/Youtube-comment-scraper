import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By # type: ignore
from selenium.webdriver.chrome.options import Options

def init_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0")
    driver = webdriver.Chrome(options=options)
    return driver

def scroll_to_load_comments(driver, scroll_pause_time=2, max_scrolls=10):
    last_height = driver.execute_script("return document.documentElement.scrollHeight")
    for _ in range(max_scrolls):
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(scroll_pause_time)
        new_height = driver.execute_script("return document.documentElement.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def scrape_youtube_comments(video_url, max_comments=10):
    driver = init_driver()
    driver.get(video_url)
    time.sleep(5)

    driver.execute_script("window.scrollTo(0, 600);")
    time.sleep(3)
    scroll_to_load_comments(driver, max_scrolls=5)

    comments_data = []

    time.sleep(5)

    comment_blocks = driver.find_elements(By.XPATH, '//*[@id="comment"]')

    if not comment_blocks:
        print("No comments found. Page might not have loaded correctly.")
        driver.quit()
        return []

    for i, block in enumerate(comment_blocks[:max_comments]):
        try:
            author = block.find_element(By.XPATH, './/*[@id="author-text"]/span').text
            comment = block.find_element(By.XPATH, './/*[@id="content-text"]').text
            time_posted = block.find_element(By.XPATH, './/*[@id="published-time-text"]').text

            comments_data.append({
                "author": author.strip(),
                "comment": comment.strip(),
                "time_posted": time_posted.strip()
            })

        except Exception as e:
            print(f"Error extracting comment {i}: {e}")
            continue

    driver.quit()
    return comments_data


def save_to_csv(data, filename="youtube_comments.csv"):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"Saved {len(data)} comments to {filename}")

if __name__ == "__main__":
    video_url = "https://www.youtube.com/watch?v=2dQXD3hB1Z0"  # Replace with your video URL
    comments = scrape_youtube_comments(video_url, max_comments=10)
    if comments:
        save_to_csv(comments)
