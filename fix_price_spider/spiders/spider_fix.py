import re
import time
from typing import Dict, Optional, Union

import scrapy
from scrapy.http import HtmlResponse, TextResponse

from fix_price_spider.items import FixpriceParserItem
from fix_price_spider.settings import ALLOWED_DOMAINS, START_URLS


class FixpriceSpider(scrapy.Spider):
    """Паук для парсинга сайта FixPrice."""

    name = "fixprice"
    allowed_domains = ALLOWED_DOMAINS
    start_urls = START_URLS

    def parse(self, response):
        """Извлечение ссылок на продукты и переход на страницы товаров."""
        product_links = response.css('a.title::attr(href)').getall()
        for link in product_links:
            full_link = response.urljoin(link)
            yield response.follow(full_link, callback=self.parse_product)

        next_page = response.css('a.pagination-next::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        else:
            pagination_links = response.css(
                'div.pagination a.number::attr(href)').getall()
            for page_link in pagination_links:
                yield response.follow(page_link, callback=self.parse)

    def parse_product(self, response):
        """Парсинг данных продукта и формирование словаря item_data."""
        item_data = {
            "timestamp": int(time.time()),
            "RPC": self.extract_rpc(response),
            "url": response.url,
            "title": self.extract_title(response),
            "brand": self.extract_brand(response),
            "marketing_tags": self.extract_marketing_tags(response),
            "section": self.extract_section(response),
            "price_data": self.extract_price_data(response),
            "stock": self.extract_stock(response),
            "assets": self.extract_assets(response),
            "metadata": self.extract_metadata(response),
            "variants": self.extract_variants(response),
        }

        yield FixpriceParserItem(item_data)

    def extract_rpc(self, response):
        """Извлечение уникального кода."""
        return response.css('span.value::text').get(default='').strip()

    def extract_title(self, response):
        """Извлечение заголовка товара."""
        title = response.css('h1.title::text').get(default='').strip()
        color = response.css('span.color *::text').get(default='').strip()
        volume = response.css('span.volume *::text').get(default='').strip()

        parts = [title]
        if color:
            parts.append(color)
        if volume:
            parts.append(volume)

        return ', '.join(parts)

    def extract_brand(self, response):
        """Извлечение бренда товара."""
        return response.css(
            '.properties p:nth-child(1) .value a::text'
        ).get(default='').strip()

    def extract_marketing_tags(self, response):
        """Извлечение маркетинговых тегов товара."""
        return response.css('p.special-auth::text').getall() or []

    def extract_section(self, response):
        """Извлечение иерархии разделов."""
        return [
            section.strip()
            for section in response.css('div.breadcrumbs span::text').extract()
            if section.strip()
        ]

    def extract_price_data(self, response):
        """Извлечение цен товара и процента скидки."""
        special_price_json = response.xpath(
            "//script[contains(text(), 'specialPrice')]/text()").get()
        special_price = self.extract_price(special_price_json)
        original_price = self.extract_original_price(response)
        sale_tag = self.calculate_discount(original_price, special_price)
        current_price = special_price or original_price

        return {
            "current": current_price,
            "original": original_price,
            "sale_tag": sale_tag,
        }

    def extract_price(
            self,
            special_price_json: Optional[str]
    ) -> Optional[float]:
        """Извлечение акционной цены из JSON."""
        if special_price_json:
            match = re.search(r'price:"([^"]+)"', special_price_json)
            if match:
                return float(match.group(1))
        return None

    def extract_original_price(
            self,
            response: Union[HtmlResponse, TextResponse]
    ) -> Optional[float]:
        """Извлечение оригинальной цены товара."""
        price_meta = response.css(
            'div.price-quantity-block > div > meta[itemprop="price"]')
        if price_meta:
            return float(price_meta.attrib.get("content", "0"))
        return None

    def calculate_discount(
            self,
            original_price: Optional[float], special_price: Optional[float]
    ) -> Optional[str]:
        """Вычесление процента скидки."""
        if original_price and special_price and original_price > special_price:
            discount = ((original_price - special_price) /
                        original_price) * 100
            return f"Скидка {discount:.2f}%"
        return None

    def extract_stock(self, response):
        """Извлекает информацию о наличие."""
        availability = response.css(
            'meta[itemprop="availability"]::attr(content)').get()
        in_stock = availability == "https://schema.org/InStock"
        count = 0

        return {
            "in_stock": in_stock,
            "count": count,
        }

    def extract_assets(self, response):
        """Извлечение мультимедиа."""
        return {
            "main_image": response.css(
                'div.product-images img.normal::attr(src)'
            ).get(default="Нет изображения"),
            "set_images": response.css(
                'div.product-images link[itemprop="contentUrl"]::attr(href)'
            ).getall(),
            "view_zoom": response.css(
                'div.product-images img.zoom::attr(src)'
            ).getall(),
            "video": self.extract_video(response)
        }

    def extract_video(self, response):
        """Извлечение ссылки на видео о товаре."""
        video_src = response.css('iframe#rt-player::attr(src)').get()
        if video_src:
            return [video_src]
        return []

    def extract_metadata(
            self,
            response: Union[HtmlResponse, TextResponse]
    ) -> Dict[str, Optional[str]]:
        """Извлечение метаданных о товаре."""
        metadata = {
            "__description": response.css(
                '.product-details .description::text'
            ).get(default='').strip()
        }
        for prop in response.css('div.properties p.property'):
            key = prop.css('span.title::text').get()
            value = prop.css('span.value::text').get()
            if key and value:
                metadata[key.strip()] = value.strip()
        return metadata

    def extract_variants(self, response):
        """Извлечение вариантов товара."""
        variant_images = response.css('img.thumbs-image::attr(src)').getall()
        return len(variant_images) if variant_images else 1
