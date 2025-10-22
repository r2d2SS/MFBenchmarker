"""
Modern web scraper for cigar price data collection
Improved version with async support, error handling, and proper logging
"""
import asyncio
import aiohttp
import logging
from datetime import date
from typing import List, Dict, Optional
from dataclasses import dataclass
from bs4 import BeautifulSoup
import re
import time

from django.conf import settings
from api.models import ScrapedData, Competitor, Product, ExchangeRate


logger = logging.getLogger(__name__)


@dataclass
class ScrapedProduct:
    """Data class for scraped product information"""
    name: str
    product_type: str
    price: float
    competitor_code: str
    extraction_date: date = date.today()


class BaseScraper:
    """Base scraper class with common functionality"""
    
    def __init__(self, competitor_code: str, base_url: str):
        self.competitor_code = competitor_code
        self.base_url = base_url
        self.session = None
        self.delay = getattr(settings, 'SCRAPER_CONFIG', {}).get('delay', 1)
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def fetch_page(self, url: str) -> Optional[str]:
        """Fetch a single page with error handling"""
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    content = await response.text()
                    await asyncio.sleep(self.delay)  # Rate limiting
                    return content
                else:
                    logger.warning(f"HTTP {response.status} for {url}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    def parse_page(self, html: str, url: str) -> List[ScrapedProduct]:
        """Parse HTML content - to be implemented by subclasses"""
        raise NotImplementedError
    
    async def scrape_urls(self, urls: List[str]) -> List[ScrapedProduct]:
        """Scrape multiple URLs and return products"""
        products = []
        
        for url in urls:
            try:
                html = await self.fetch_page(url)
                if html:
                    page_products = self.parse_page(html, url)
                    products.extend(page_products)
                    logger.info(f"Scraped {len(page_products)} products from {url}")
            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
        
        return products


class IHavanasScraper(BaseScraper):
    """Scraper for iHavanas.com"""
    
    def __init__(self):
        super().__init__('IH', 'https://www.ihavanas.com')
    
    def parse_page(self, html: str, url: str) -> List[ScrapedProduct]:
        """Parse iHavanas product page"""
        products = []
        soup = BeautifulSoup(html, 'html.parser')
        
        try:
            name_boxes = soup.find_all(class_="product_name")
            price_boxes = soup.find_all(class_="current_price")
            box_types = soup.find_all(string=re.compile("Box"))
            
            for name_box, box_type, price_box in zip(name_boxes, box_types, price_boxes):
                try:
                    name = name_box.string.strip() if name_box.string else ""
                    product_type = box_type.strip() if box_type else ""
                    price_str = price_box.string
                    
                    if price_str and len(price_str) > 3:
                        price = float(price_str[3:])  # Remove currency symbol
                        
                        products.append(ScrapedProduct(
                            name=name,
                            product_type=product_type,
                            price=price,
                            competitor_code=self.competitor_code
                        ))
                except (ValueError, AttributeError) as e:
                    logger.warning(f"Error parsing iHavanas product: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error parsing iHavanas page {url}: {e}")
        
        return products


class COHScraper(BaseScraper):
    """Scraper for Cigars of Habanos"""
    
    def __init__(self):
        super().__init__('CH', 'https://www.cigarsofhabanos.com')
    
    def parse_page(self, html: str, url: str) -> List[ScrapedProduct]:
        """Parse COH product page"""
        products = []
        soup = BeautifulSoup(html, 'html.parser')
        
        try:
            tds = soup.find('td', valign="top", style="padding-left:8px;")
            if not tds:
                return products
            
            tbody = tds.find('table', width="100%", border="0", cellspacing="0", cellpadding="0")
            if not tbody:
                return products
            
            for td in tbody.find_all('td', align="left", valign="top"):
                try:
                    name_elem = td.find('span', class_=re.compile("^product"))
                    type_elem = td.find(string=re.compile("Box"))
                    price_elem = td.find(class_="pricetxt")
                    
                    if name_elem and price_elem:
                        name = name_elem.string[1:] if name_elem.string else ""
                        product_type = type_elem[1:] if type_elem else ""
                        
                        price_strong = price_elem.find('strong')
                        if price_strong and price_strong.string:
                            price = float(price_strong.string.split('$')[1])
                            
                            products.append(ScrapedProduct(
                                name=name,
                                product_type=product_type,
                                price=price,
                                competitor_code=self.competitor_code
                            ))
                
                except (ValueError, AttributeError, IndexError) as e:
                    logger.warning(f"Error parsing COH product: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error parsing COH page {url}: {e}")
        
        return products


class NeptuneScraper(BaseScraper):
    """Scraper for Neptune Cigar"""
    
    def __init__(self):
        super().__init__('NT', 'https://www.neptunecigar.com')
    
    def parse_page(self, html: str, url: str) -> List[ScrapedProduct]:
        """Parse Neptune product page"""
        products = []
        soup = BeautifulSoup(html, 'html.parser')
        
        try:
            for product_div in soup.find_all('div', class_="product_item"):
                try:
                    name_elem = product_div.find('h2', itemprop="name")
                    
                    if name_elem:
                        name = name_elem.string.strip() if name_elem.string else ""
                        
                        # Get all price/box combinations
                        boxes = product_div.find_all(class_="product_table_cells lbup")
                        prices = product_div.find_all('span', itemprop="price")
                        
                        for box, price in zip(boxes, prices):
                            try:
                                product_type = box.string.strip() if box.string else ""
                                price_str = price.string
                                
                                if price_str and '$' in price_str:
                                    price_val = float(price_str.split('$')[1])
                                    
                                    products.append(ScrapedProduct(
                                        name=name,
                                        product_type=product_type,
                                        price=price_val,
                                        competitor_code=self.competitor_code
                                    ))
                            except (ValueError, AttributeError, IndexError):
                                # Try without product type
                                try:
                                    if price_str and '$' in price_str:
                                        price_val = float(price_str.split('$')[1])
                                        
                                        products.append(ScrapedProduct(
                                            name=name,
                                            product_type="",
                                            price=price_val,
                                            competitor_code=self.competitor_code
                                        ))
                                except (ValueError, AttributeError):
                                    continue
                
                except Exception as e:
                    logger.warning(f"Error parsing Neptune product: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error parsing Neptune page {url}: {e}")
        
        return products


class ScraperManager:
    """Main scraper manager to coordinate all scrapers"""
    
    def __init__(self):
        self.scrapers = {
            'IH': IHavanasScraper(),
            'CH': COHScraper(), 
            'NT': NeptuneScraper()
        }
        self.urls = {
            'IH': self._get_ihavanas_urls(),
            'CH': self._get_coh_urls(),
            'NT': self._get_neptune_urls()
        }
    
    def _get_ihavanas_urls(self) -> List[str]:
        """Get iHavanas URLs to scrape"""
        return [
            "https://www.ihavanas.com/details.php?ptype=cigars&pid=Acid",
            "https://www.ihavanas.com/details.php?ptype=cigars&pid=Cohiba",
            "https://www.ihavanas.com/details.php?ptype=cigars&pid=Montecristo",
            "https://www.ihavanas.com/details.php?ptype=cigars&pid=Romeo%20Y%20Julieta",
            "https://www.ihavanas.com/details.php?ptype=cigars&pid=Partagas",
            # Add more URLs as needed
        ]
    
    def _get_coh_urls(self) -> List[str]:
        """Get COH URLs to scrape"""
        return [
            "https://www.cigarsofhabanos.com/cigars-cohiba",
            "https://www.cigarsofhabanos.com/cigars-montecristo", 
            "https://www.cigarsofhabanos.com/cigars-partagas",
            "https://www.cigarsofhabanos.com/cigars-romeo-y-julieta",
            # Add more URLs as needed
        ]
    
    def _get_neptune_urls(self) -> List[str]:
        """Get Neptune URLs to scrape"""
        return [
            "https://www.neptunecigar.com/cohiba-cigar",
            "https://www.neptunecigar.com/montecristo-cigar",
            "https://www.neptunecigar.com/partagas-cigar",
            "https://www.neptunecigar.com/romeo-y-julieta-cigar",
            # Add more URLs as needed
        ]
    
    async def scrape_all(self) -> Dict[str, List[ScrapedProduct]]:
        """Scrape all competitors"""
        results = {}
        start_time = time.time()
        
        logger.info("Starting scraping process...")
        
        for competitor_code, scraper in self.scrapers.items():
            logger.info(f"Scraping {competitor_code}...")
            
            async with scraper:
                urls = self.urls.get(competitor_code, [])
                products = await scraper.scrape_urls(urls)
                results[competitor_code] = products
                
                logger.info(f"Completed {competitor_code}: {len(products)} products")
        
        elapsed = time.time() - start_time
        total_products = sum(len(products) for products in results.values())
        logger.info(f"Scraping completed in {elapsed:.2f}s. Total products: {total_products}")
        
        return results
    
    async def save_to_database(self, scraped_results: Dict[str, List[ScrapedProduct]]):
        """Save scraped data to database"""
        logger.info("Saving data to database...")
        
        saved_count = 0
        
        for competitor_code, products in scraped_results.items():
            try:
                competitor = Competitor.objects.get(code=competitor_code)
                
                for product_data in products:
                    # Try to match with existing product
                    matching_product = Product.objects.filter(
                        name__icontains=product_data.name[:20]
                    ).first()
                    
                    scraped_obj = ScrapedData.objects.create(
                        extraction_date=product_data.extraction_date,
                        product=matching_product,
                        product_name=product_data.name,
                        product_type=product_data.product_type,
                        competitor=competitor,
                        price=product_data.price
                    )
                    saved_count += 1
            
            except Competitor.DoesNotExist:
                logger.error(f"Competitor {competitor_code} not found in database")
            except Exception as e:
                logger.error(f"Error saving {competitor_code} data: {e}")
        
        logger.info(f"Saved {saved_count} records to database")
        return saved_count


async def run_scraper():
    """Main function to run the scraper"""
    manager = ScraperManager()
    
    try:
        # Scrape all sites
        results = await manager.scrape_all()
        
        # Save to database
        saved_count = await manager.save_to_database(results)
        
        # Update exchange rates
        from api.utils import update_exchange_rates
        update_exchange_rates()
        
        logger.info(f"Scraping process completed successfully. {saved_count} records saved.")
        return True
        
    except Exception as e:
        logger.error(f"Scraping process failed: {e}")
        return False


if __name__ == "__main__":
    import django
    import os
    
    # Setup Django environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Benchmarker.settings')
    django.setup()
    
    # Run the scraper
    asyncio.run(run_scraper())