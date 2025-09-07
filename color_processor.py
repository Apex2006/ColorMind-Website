import numpy as np
from PIL import Image
import colorsys
from sklearn.cluster import KMeans
import logging

class ColorProcessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def extract_dominant_colors(self, image, num_colors=6, max_size=300):
        """Extract dominant colors from an image using K-Means clustering"""
        try:
            # Resize image for faster processing
            image = self._resize_image(image, max_size)
            
            # Convert to RGB if not already
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert image to numpy array
            image_array = np.array(image)
            pixels = image_array.reshape(-1, 3)
            
            # Remove very dark and very light pixels (noise)
            pixels = self._filter_extreme_colors(pixels)
            
            # Apply K-Means clustering
            kmeans = KMeans(n_clusters=num_colors, random_state=42, n_init=10)
            kmeans.fit(pixels)
            
            # Get cluster centers (dominant colors)
            colors = kmeans.cluster_centers_.astype(int)
            
            # Get cluster sizes for color importance
            labels = kmeans.labels_
            color_counts = np.bincount(labels)
            
            # Sort colors by frequency
            color_frequency_pairs = list(zip(colors, color_counts))
            color_frequency_pairs.sort(key=lambda x: x[1], reverse=True)
            
            # Format colors with additional information
            dominant_colors = []
            for i, (color, count) in enumerate(color_frequency_pairs):
                color_info = {
                    'rgb': color.tolist(),
                    'hex': self._rgb_to_hex(color),
                    'hsl': self._rgb_to_hsl(color),
                    'cmyk': self._rgb_to_cmyk(color),
                    'frequency': float(count / len(labels)),
                    'rank': i + 1
                }
                dominant_colors.append(color_info)
            
            return dominant_colors
            
        except Exception as e:
            self.logger.error(f"Error extracting colors: {str(e)}")
            raise
    
    def _resize_image(self, image, max_size):
        """Resize image maintaining aspect ratio"""
        width, height = image.size
        if max(width, height) > max_size:
            if width > height:
                new_width = max_size
                new_height = int(height * max_size / width)
            else:
                new_height = max_size
                new_width = int(width * max_size / height)
            
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        return image
    
    def _filter_extreme_colors(self, pixels, dark_threshold=30, light_threshold=225):
        """Remove very dark and very light pixels"""
        # Calculate brightness for each pixel
        brightness = np.mean(pixels, axis=1)
        
        # Filter pixels
        mask = (brightness > dark_threshold) & (brightness < light_threshold)
        filtered_pixels = pixels[mask]
        
        # If too few pixels remain, use original
        if len(filtered_pixels) < len(pixels) * 0.1:
            return pixels
        
        return filtered_pixels
    
    def _rgb_to_hex(self, rgb):
        """Convert RGB to HEX"""
        return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))
    
    def _rgb_to_hsl(self, rgb):
        """Convert RGB to HSL"""
        r, g, b = rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        return {
            'h': int(h * 360),
            's': int(s * 100),
            'l': int(l * 100)
        }
    
    def _rgb_to_cmyk(self, rgb):
        """Convert RGB to CMYK"""
        r, g, b = rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0
        
        k = 1 - max(r, g, b)
        if k == 1:
            return {'c': 0, 'm': 0, 'y': 0, 'k': 100}
        
        c = (1 - r - k) / (1 - k)
        m = (1 - g - k) / (1 - k)
        y = (1 - b - k) / (1 - k)
        
        return {
            'c': int(c * 100),
            'm': int(m * 100),
            'y': int(y * 100),
            'k': int(k * 100)
        }
    
    def get_color_temperature(self, rgb):
        """Estimate color temperature (warm/cool)"""
        r, g, b = rgb
        # Simple heuristic: more red/yellow = warm, more blue = cool
        warmth = (r + (g * 0.5)) - b
        return 'warm' if warmth > 0 else 'cool'
    
    def calculate_contrast_ratio(self, color1, color2):
        """Calculate contrast ratio between two colors"""
        def get_luminance(rgb):
            r, g, b = [x / 255.0 for x in rgb]
            r = r / 12.92 if r <= 0.03928 else pow((r + 0.055) / 1.055, 2.4)
            g = g / 12.92 if g <= 0.03928 else pow((g + 0.055) / 1.055, 2.4)
            b = b / 12.92 if b <= 0.03928 else pow((b + 0.055) / 1.055, 2.4)
            return 0.2126 * r + 0.7152 * g + 0.0722 * b
        
        l1 = get_luminance(color1)
        l2 = get_luminance(color2)
        
        lighter = max(l1, l2)
        darker = min(l1, l2)
        
        return (lighter + 0.05) / (darker + 0.05)
