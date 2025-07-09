"""
Advanced Image Search Module for Shadow Roll Bot
Uses multiple APIs and scraping methods to find high-quality character images
"""
import asyncio
import aiohttp
import json
import re
import urllib.parse
from typing import List, Optional, Dict
import logging
from PIL import Image
import io

logger = logging.getLogger(__name__)

class ImageSearchEngine:
    def __init__(self):
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers=self.headers
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    async def search_character_images(self, character_name: str, anime_name: str, limit: int = 10) -> List[str]:
        """Search for character images using multiple sources"""
        all_images = []
        
        # First try anime-specific databases (most reliable)
        try:
            anime_db_images = await self._search_anime_databases(character_name, anime_name)
            all_images.extend(anime_db_images[:3])
        except Exception as e:
            logger.warning(f"Anime database search failed: {e}")
        
        # Then try web search engines
        search_queries = [
            f'{character_name} {anime_name} anime',
            f'{character_name} {anime_name} character',
            f'{character_name} anime',
        ]
        
        for query in search_queries[:2]:  # Limit queries to avoid rate limiting
            try:
                # Try multiple search engines
                google_images = await self._search_google_images(query)
                all_images.extend(google_images[:2])
                
                bing_images = await self._search_bing_images(query)
                all_images.extend(bing_images[:2])
                
                await asyncio.sleep(0.5)  # Shorter delay
                
            except Exception as e:
                logger.warning(f"Search failed for query '{query}': {e}")
                continue
                
        # Remove duplicates and validate
        unique_images = list(dict.fromkeys(all_images))
        validated_images = []
        
        for img_url in unique_images[:limit]:
            if await self._validate_image_quality(img_url):
                validated_images.append(img_url)
                
        return validated_images
        
    async def _search_google_images(self, query: str) -> List[str]:
        """Search Google Images through scraping"""
        try:
            search_url = "https://www.google.com/search"
            params = {
                'q': query,
                'tbm': 'isch',
                'tbs': 'isz:l,itp:photo',  # Large images, photos
                'safe': 'active'
            }
            
            async with self.session.get(search_url, params=params) as response:
                if response.status != 200:
                    return []
                    
                html = await response.text()
                
                # Extract image URLs from Google Images results
                image_urls = []
                
                # Look for image data in script tags
                script_pattern = r'"ou":"([^"]+)"'
                matches = re.findall(script_pattern, html)
                
                for match in matches[:10]:
                    try:
                        url = urllib.parse.unquote(match)
                        if self._is_valid_image_url(url):
                            image_urls.append(url)
                    except:
                        continue
                        
                return image_urls
                
        except Exception as e:
            logger.warning(f"Google Images search failed: {e}")
            return []
            
    async def _search_bing_images(self, query: str) -> List[str]:
        """Search Bing Images through scraping"""
        try:
            search_url = "https://www.bing.com/images/search"
            params = {
                'q': query,
                'qft': '+filterui:imagesize-large+filterui:aspect-tall',  # Large, portrait images
                'FORM': 'IRFLTR'
            }
            
            async with self.session.get(search_url, params=params) as response:
                if response.status != 200:
                    return []
                    
                html = await response.text()
                
                # Extract image URLs from Bing results
                image_urls = []
                
                # Look for murl data
                murl_pattern = r'"murl":"([^"]+)"'
                matches = re.findall(murl_pattern, html)
                
                for match in matches[:10]:
                    try:
                        url = match.replace('\\u002f', '/').replace('\\', '')
                        if self._is_valid_image_url(url):
                            image_urls.append(url)
                    except:
                        continue
                        
                return image_urls
                
        except Exception as e:
            logger.warning(f"Bing Images search failed: {e}")
            return []
            
    async def _search_pinterest(self, query: str) -> List[str]:
        """Search Pinterest for anime character images"""
        try:
            search_url = "https://www.pinterest.com/search/pins/"
            params = {'q': query + ' anime character'}
            
            async with self.session.get(search_url, params=params) as response:
                if response.status != 200:
                    return []
                    
                html = await response.text()
                
                # Pinterest uses a lot of JavaScript, look for image data
                image_urls = []
                
                # Look for Pinterest image URLs
                pin_pattern = r'"url":"([^"]*\.(?:jpg|jpeg|png|webp)[^"]*)"'
                matches = re.findall(pin_pattern, html, re.IGNORECASE)
                
                for match in matches[:8]:
                    try:
                        url = match.replace('\\/', '/')
                        if self._is_valid_image_url(url) and 'pinimg.com' in url:
                            image_urls.append(url)
                    except:
                        continue
                        
                return image_urls
                
        except Exception as e:
            logger.warning(f"Pinterest search failed: {e}")
            return []
            
    async def _search_anime_databases(self, character_name: str, anime_name: str) -> List[str]:
        """Search anime-specific databases"""
        image_urls = []
        
        # Search AniList
        anilist_images = await self._search_anilist(character_name, anime_name)
        image_urls.extend(anilist_images)
        
        # Search Anime Characters Database
        acdb_images = await self._search_anime_characters_db(character_name, anime_name)
        image_urls.extend(acdb_images)
        
        return image_urls
        
    async def _search_anilist(self, character_name: str, anime_name: str) -> List[str]:
        """Search AniList GraphQL API"""
        try:
            query = '''
            query ($search: String) {
                Page(page: 1, perPage: 5) {
                    characters(search: $search) {
                        image {
                            large
                            medium
                        }
                        name {
                            full
                        }
                    }
                }
            }
            '''
            
            variables = {'search': f"{character_name} {anime_name}"}
            
            async with self.session.post(
                'https://graphql.anilist.co',
                json={'query': query, 'variables': variables}
            ) as response:
                if response.status != 200:
                    return []
                    
                data = await response.json()
                characters = data.get('data', {}).get('Page', {}).get('characters', [])
                
                image_urls = []
                for char in characters:
                    if char.get('image', {}).get('large'):
                        image_urls.append(char['image']['large'])
                    elif char.get('image', {}).get('medium'):
                        image_urls.append(char['image']['medium'])
                        
                return image_urls
                
        except Exception as e:
            logger.warning(f"AniList search failed: {e}")
            return []
            
    async def _search_anime_characters_db(self, character_name: str, anime_name: str) -> List[str]:
        """Search Anime Characters Database"""
        try:
            # This would need specific implementation for anime-characters-database.com
            # For now return empty list
            return []
        except:
            return []
            
    def _is_valid_image_url(self, url: str) -> bool:
        """Check if URL looks like a valid image URL"""
        if not url or not url.startswith(('http://', 'https://')):
            return False
            
        # Check file extension
        valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']
        url_lower = url.lower()
        
        # Direct extension check
        if any(url_lower.endswith(ext) for ext in valid_extensions):
            return True
            
        # Check for image in URL path or query parameters
        if any(ext in url_lower for ext in valid_extensions):
            return True
            
        # Check for common image hosting domains
        image_domains = [
            'imgur.com', 'i.imgur.com',
            'pinimg.com', 'pinterest.com',
            'googleusercontent.com',
            'wikimedia.org',
            'anilist.co',
            'myanimelist.net',
            'zerochan.net',
            'safebooru.org'
        ]
        
        return any(domain in url for domain in image_domains)
        
    async def _validate_image_quality(self, url: str) -> bool:
        """Validate image quality and accessibility"""
        try:
            async with self.session.head(url) as response:
                if response.status != 200:
                    return False
                    
                # Check content type
                content_type = response.headers.get('content-type', '')
                if not any(fmt in content_type.lower() for fmt in ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']):
                    return False
                    
                # Check file size (max 15MB)
                content_length = response.headers.get('content-length')
                if content_length and int(content_length) > 15 * 1024 * 1024:
                    return False
                    
                return True
                
        except Exception:
            # If HEAD fails, try a quick GET request
            try:
                async with self.session.get(url) as response:
                    if response.status != 200:
                        return False
                        
                    # Read first chunk to check if it's an image
                    chunk = await response.content.read(1024)
                    
                    # Check image magic bytes
                    if chunk.startswith(b'\xff\xd8\xff'):  # JPEG
                        return True
                    elif chunk.startswith(b'\x89PNG\r\n\x1a\n'):  # PNG
                        return True
                    elif chunk.startswith(b'RIFF') and b'WEBP' in chunk[:20]:  # WebP
                        return True
                        
                    return False
                    
            except Exception:
                return False