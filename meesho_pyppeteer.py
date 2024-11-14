# import asyncio
#
# from pyppeteer import launch
#
#
# async def open_url():
#     # Launch a new browser
#     browser = await launch(executablePath=r"C:\Program Files\Google\Chrome\Application\chrome.exe", headless=False)  # Set headless=True if you want to run it without opening a visible browser
#     page = await browser.newPage()
#
#     # Open the URL
#     await page.goto('https://www.meesho.com')
#
#     # Wait for a few seconds to keep the browser open
#     await asyncio.sleep(5)
#
#     # Close the browser
#     await browser.close()
#
#
# # Run the async function
# asyncio.get_event_loop().run_until_complete(open_url())
