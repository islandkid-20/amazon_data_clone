import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://www.amazon.com/"
}

def get_amazon_search_results(search_term, page=1):
    url = f"https://www.amazon.com/s?k={search_term}&page={page}"
    max_retries = 5
    for attempt in range(max_retries):
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print("Successfully retrieved search results")
            return response.text
        else:
            print(f"Failed to retrieve search results. Status code: {response.status_code}. Attempt {attempt + 1} of {max_retries}")
            time.sleep(2)
    print("Max retries reached. Exiting.")
    return None

def parse_search_results(html):
    soup = BeautifulSoup(html, "html.parser")
    products = []
    for product in soup.find_all("div", {"data-component-type": "s-search-result"}):
        id = product["data-asin"]
        title = product.find("h2", {"class": "a-size-mini a-spacing-none a-color-base s-line-clamp-2"}).text.strip() if product.find("h2", {"class": "a-size-mini a-spacing-none a-color-base s-line-clamp-2"}) else "No title"
        price = product.find("span", {"class": "a-offscreen"}).text if product.find("span", {"class": "a-offscreen"}) else "No price"
        images = product.find("img", {"class": "s-image"})["src"] if product.find("img", {"class": "s-image"}) else "No image"
        products.append({"Product ID": id, "Product Name": title, "Price": price, "Images": images})
    print(f"Parsed {len(products)} products")
    return products

def save_products_to_csv(products, filename):
    df = pd.DataFrame(products)
    df.to_csv(filename, index=False)
    print(f"Saved {len(products)} products to {filename}.")

# Get About this item  from Amazon for each product and append to dataframe
def get_about_this_item(product):
    url = f"https://www.amazon.com/dp/{product['Product ID']}"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            about_this_item = soup.find("div", {"id": "feature-bullets"})
            if about_this_item:
                about_text = " ".join(about_this_item.stripped_strings)
                if about_text.startswith("About this item"):
                    about_text = about_text.replace("About this item", "") 
                product["About this Item"] = about_text
            else:
                product["About this Item"] = "No About this item"
        else:
            product["About this Item"] = "No About this item"
    except Exception as e:
        print(f"Failed to retrieve 'About this item' for {product['Product ID']}: {e}")
        product["About this Item"] = "No About this item"
    return product

def main():
    search_term = input("Enter search term: ")
    html = get_amazon_search_results(search_term)
    if html:
        products = []
        for page in range(2, 6):
            html = get_amazon_search_results(search_term, page=page)
            if html:
                products.extend(parse_search_results(html))
            else:
                break # No more pages to parse
        products = parse_search_results(html)
        products = [get_about_this_item(product) for product in products]
        filename = f"{search_term}.csv"
        save_products_to_csv(products, filename)
        print(f"Saved {len(products)} products to {filename}.")
        time.sleep(5)

if __name__ == "__main__":
    main()
