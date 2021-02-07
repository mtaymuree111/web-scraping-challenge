# Import dependencies
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt


def scrape_all():
    browser = Browser("chrome", executable_path="chromedriver", headless=True)
    news_title, news_paragraph = mars_news(browser)
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemispheres": hemispheres(browser),
        "last_modified": dt.datetime.now()
    }
    browser.quit()
    return data

def mars_news(browser):
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
    html = browser.html
    soup_data = soup(html, 'html.parser')

    try:
        element = soup_data.select_one("ul.item_list li.slide")
        news_title = element.find("div", class_="content_title").get_text()
        news_paragraph = element.find("div", class_="article_teaser_body").get_text()

    except AttributeError:
        return None, None
    return news_title, news_paragraph

def featured_image(browser):
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)
    full_image = browser.find_by_id('full_image')[0]
    full_image.click()
    browser.is_element_present_by_text('more info', wait_time=1)
    more_info = browser.links.find_by_partial_text('more info')
    more_info.click()

    browser_html_2 = browser.html
    soup_image = soup(browser_html_2, 'html.parser')

    try:
        image_url = soup_image.select_one('figure.lede a img').get("src")

    except AttributeError:
        return None

    image_url_2 = f'https://www.jpl.nasa.gov{image_url}'

    return image_url_2

def mars_facts():
    try:
        df = pd.read_html('http://space-facts.com/mars/')[0]

    except BaseException:
        return None

    df.columns = ['Description', 'Mars']
    df.set_index('Description', inplace=True)

    return df.to_html(classes="table table-striped")


def hemispheres(browser):
    url = (
        "https://astrogeology.usgs.gov/search/"
        "results?q=hemisphere+enhanced&k1=target&v1=Mars"
    )

    browser.visit(url)
    hemisphere_image_urls = []
    for i in range(4):
        browser.find_by_css("a.product-item h3")[i].click()
        hemisphere_data = scrape_hemisphere(browser.html)
        hemisphere_image_urls.append(hemisphere_data)
        browser.back()

    return hemisphere_image_urls


def scrape_hemisphere(html_text):
    hemisphere_soup = soup(html_text, "html.parser")

    try:
        title = hemisphere_soup.find("h2", class_="title").get_text()
        sample = hemisphere_soup.find("a", text="Sample").get("href")

    except AttributeError:
        title = None
        sample = None

    hemispheres = {
        "title": title,
        "img_url": sample
    }

    return hemispheres


if __name__ == "__main__":
    print(scrape_all())