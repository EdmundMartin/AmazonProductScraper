import asyncio

from lxml import html as htmlparser


def parse_product_review(dom):
    item = dom.cssselect('span.reviewCountTextLinkedHistogram')
    if item:
        return item[0].text_content().replace('\n', '').strip()
    else:
        return ''


def parse_product_title(dom):
    item = dom.cssselect('h1#title span')
    if item:
        return item[0].text_content().replace('\n', '').strip()
    else:
        return ''


def parse_product_price(dom):
    item = dom.cssselect('.a-color-price')
    if item:
        return item[0].text_content().replace('\n', '').strip()
    else:
        return ''

async def amazon_uk_product_parser(response_obj):
    if response_obj.get('response'):
        dom = htmlparser.fromstring(response_obj.get('response'))
        product_review = parse_product_review(dom)
        product_title = parse_product_title(dom)
        product_price = parse_product_price(dom)
        new_data = {'product_review': product_review, 'product_title': product_title, 'product_price': product_price}
        response_obj.update(new_data)
        return response_obj
    return response_obj

