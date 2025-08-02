from utils import sanitize_filename
from PIL import Image
import os
from driver_setup import random_delay

USER_AGENTS = [
    # Add several real mobile user agents here
    "Mozilla/5.0 (Linux; Android 13; Pixel 7) ...",
    "Mozilla/5.0 (Linux; Android 12; Pixel 6) ...",
    # etc.
]

def setup_mobile_driver():
    print("Setting up mobile driver...")
    options = uc.ChromeOptions()
    user_agent = random.choice(USER_AGENTS)
    print(f"Selected User Agent: {user_agent}")
    options.add_argument(f"user-agent={user_agent}")
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    # Randomize window size
    width = random.randint(390, 430)
    height = random.randint(800, 950)
    print(f"Setting window size: {width}x{height}")
    options.add_argument(f"--window-size={width},{height}")
    mobile_emulation = {
        "deviceMetrics": { "width": width, "height": height, "pixelRatio": 2.0 },
        "userAgent": user_agent
    }
    options.add_experimental_option("mobileEmulation", mobile_emulation)
    driver = uc.Chrome(options=options)
    print("Mobile driver setup complete")
    return driver

def capture_long_screenshot(driver, keyword, save_path):
    try:
        print(f"\nStarting screenshot capture for keyword: {keyword}")
        search_url = f"https://www.flipkart.com/search?q={keyword.replace(' ', '+')}"
        print(f"Navigating to URL: {search_url}")
        driver.get(search_url)
        random_delay(1.2, 2.7)

        temp_files = []

        # 1️⃣  Grab three viewport-sized screenshots
        for i in range(2):
            print(f"Capturing screenshot {i+1} of 2")
            if i == 1:  # for shots 1 and 2 scroll first
                print("Scrolling before capture...")
                driver.execute_script("window.scrollBy(0, window.innerHeight-100);")
                random_delay(0.5, 1.2)
            elif i > 1:
                driver.execute_script("window.scrollBy(0, window.innerHeight);")
                random_delay(0.5, 1.2)
            filename = f"temp{i+1}.png"
            print(f"Saving temporary screenshot: {filename}")
            driver.save_screenshot(filename)
            temp_files.append(filename)

        # 2️⃣  Load images, crop 10 % off the second one, and stash in a list
        print("\nProcessing captured images...")
        images = []
        for idx, path in enumerate(temp_files):
            print(f"Processing image {idx+1}: {path}")
            img = Image.open(path)
            if idx == 1:  # second screenshot (0-based index)
                h = img.height
                crop_top = int(h * 0.1)  # Remove 10% from top
                crop_bottom = int(h * 0.75)  # Remove 70% from bottom
                print(f"Cropping second image - original height: {h}, keeping from {crop_top}px to {h - crop_bottom}px")
                img = img.crop((0, crop_top, img.width, h - crop_bottom))
            images.append(img)
            print(f"Image {idx+1} dimensions: {img.width}x{img.height}")

        # 3️⃣  Stitch
        print("\nStitching images together...")
        total_height = sum(img.height for img in images)
        print(f"Total stitched height: {total_height}")
        stitched_img = Image.new('RGB', (images[0].width, total_height))
        y_offset = 0
        for img in images:
            print(f"Adding image at offset: {y_offset}")
            stitched_img.paste(img, (0, y_offset))
            y_offset += img.height

        # 4️⃣  Save & clean up
        filename = sanitize_filename(keyword) + ".png"
        screenshot_path = os.path.join(save_path, filename)
        print(f"\nSaving final screenshot to: {screenshot_path}")
        stitched_img.save(screenshot_path)

        print("Cleaning up temporary files...")
        for f in temp_files:
            if os.path.exists(f):
                os.remove(f)
                print(f"Removed: {f}")
            else:
                print(f"File not found, can't remove: {f}")

        print("Screenshot capture completed successfully")
        return "Success", filename, ""
    except Exception as e:
        print(f"\nERROR during screenshot capture: {str(e)}")
        return "Failed", "", str(e)