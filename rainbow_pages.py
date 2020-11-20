#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from lxml import html
import unicodecsv as csv
import argparse
import requests.packages.urllib3


def parse_listing(keyword, place):

    requests.packages.urllib3.disable_warnings()
    """

    Function to process Rainbow Pages listing page
    : param keyword: search query
    : param place : place name

    """
    # url = "https://www.yellowpages.com/search?search_terms={0}&geo_location_terms={1}".format(keyword, place)
    url = "https://rainbowpages.lk/search.php?action=search&searchId=&searchType=&s={0}&l={1}".format(keyword, place)

    print("retrieving ", url)

    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
               'Accept-Encoding': 'gzip, deflate',
               'Accept-Language': 'en-US,en;q=0.5',
               'Cache-Control': 'max-age=0',
               'Connection': 'keep-alive',
               'Host': 'rainbowpages.lk',
               'Referer': 'https://rainbowpages.lk/',
               'TE': 'Trailers',
               'Upgrade-Insecure-Requests': '1',
               'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36'
               }




    # Adding retries
    for retry in range(10):
        try:
            response = requests.get(url, verify=False, headers=headers)
            print("parsing page")
            if response.status_code == 200:
                print("Request 200")
                parser = html.fromstring(response.content)
                # making links absolute
                base_url = "https://rainbowpages.lk/"
                manula = parser.make_links_absolute(base_url)
                print("Request pass absolute")
                XPATH_LISTINGS = "/html/body/div[1]/div/div/div/div[1]/div/div/div/div/div/div/div[@class='single-product']  "
                listings = parser.xpath(XPATH_LISTINGS)
                scraped_results = []

                for results in listings:
                    XPATH_BUSINESS_NAME = ".//h4[@class='media-heading']//text()"
                    XPATH_BUSSINESS_PAGE = ".//h4[@class='media-heading']//@href"
                    XPATH_TELEPHONE = ".//div//p[2]//text()"
                    XPATH_ADDRESS = ".//div//p[1]//text()"
                    # XPATH_STREET = ".//div[@class='street-address']//text()"
                    # XPATH_LOCALITY = ".//div[@class='locality']//text()"
                    # XPATH_REGION = ".//div[@class='info']//div//p[@itemprop='address']//span[@itemprop='addressRegion']//text()"
                    # XPATH_ZIP_CODE = ".//div[@class='info']//div//p[@itemprop='address']//span[@itemprop='postalCode']//text()"
                    # XPATH_RANK = ".//div[@class='info']//h2[@class='n']/text()"
                    # XPATH_CATEGORIES = ".//div[@class='info']//div[contains(@class,'info-section')]//div[@class='categories']//text()"
                    # XPATH_WEBSITE = ".//div[@class='info']//div[contains(@class,'info-section')]//div[@class='links']//a[contains(@class,'website')]/@href"
                    # XPATH_RATING = ".//div[@class='info']//div[contains(@class,'info-section')]//div[contains(@class,'result-rating')]//span//text()"

                    raw_business_name = results.xpath(XPATH_BUSINESS_NAME)
                    raw_business_telephone = results.xpath(XPATH_TELEPHONE)
                    raw_business_page = results.xpath(XPATH_BUSSINESS_PAGE)
                    # raw_categories = results.xpath(XPATH_CATEGORIES)
                    # raw_website = results.xpath(XPATH_WEBSITE)
                    # raw_rating = results.xpath(XPATH_RATING)
                    raw_address = results.xpath(XPATH_ADDRESS)
                    # raw_street = results.xpath(XPATH_STREET)
                    # raw_locality = results.xpath(XPATH_LOCALITY)
                    # raw_region = results.xpath(XPATH_REGION)
                    # raw_zip_code = results.xpath(XPATH_ZIP_CODE)
                    # raw_rank = results.xpath(XPATH_RANK)

                    business_name = ''.join(raw_business_name).strip() if raw_business_name else None
                    telephone = ''.join(raw_business_telephone).strip() if raw_business_telephone else None
                    business_page = ''.join(raw_business_page).strip() if raw_business_page else None
                    business_address = ''.join(raw_address).strip() if raw_address else None
                    # rank = ''.join(raw_rank).replace('.\xa0', '') if raw_rank else None
                    # category = ','.join(raw_categories).strip() if raw_categories else None
                    # website = ''.join(raw_website).strip() if raw_website else None
                    # rating = ''.join(raw_rating).replace("(", "").replace(")", "").strip() if raw_rating else None
                    # street = ''.join(raw_street).strip() if raw_street else None
                    # locality = ''.join(raw_locality).replace(',\xa0', '').strip() if raw_locality else None
                    # locality, locality_parts = locality.split(',')
                    # _, region, zipcode = locality_parts.split(' ')

                    business_details = {
                        'business_name': business_name,
                        'telephone': telephone,
                        'business_page': business_page,
                        'business_address': business_address
                        # 'rank': rank,
                        # 'category': category,
                        # 'website': website,
                        # 'rating': rating,
                        # 'street': street,
                        # 'locality': locality,
                        # 'region': region,
                        # 'zipcode': zipcode,
                        # 'listing_url': response.url
                    }
                    scraped_results.append(business_details)

                return scraped_results

            elif response.status_code == 404:
                print("Could not find a location matching", place)
                # no need to retry for non existing page
                break
            else:
                print("Failed to process page")
                return []

        except:
            print("Failed to process page")
            return []


if __name__ == "__main__":

    argparser = argparse.ArgumentParser()
    argparser.add_argument('keyword', help='Search Keyword')
    argparser.add_argument('place', help='Place Name')

    args = argparser.parse_args()
    keyword = args.keyword
    place = args.place

    scraped_data = parse_listing(keyword, place)

    if scraped_data:
        print("Writing scraped data to %s-%s-rainbowpages-scraped-data.csv" % (keyword, place))
        with open('%s-%s-rainbowpages-scraped-data.csv' % (keyword, place), 'wb') as csvfile:
            fieldnames = ['business_name', 'telephone', 'business_page', 'business_address']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            for data in scraped_data:
                writer.writerow(data)
