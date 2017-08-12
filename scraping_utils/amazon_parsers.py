import asyncio

from lxml import html as htmlparser

async def amazon_uk_product_parser(response_obj):

    if response_obj.get('html'):

        dom = htmlparser.fromstring(response_obj.get('html'))

