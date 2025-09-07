import colorsys
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime
import logging

class PaletteGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Style color rules
        self.style_rules = {
            'japandi': {
                'saturation_range': (0.05, 0.25),
                'lightness_range': (0.7, 0.95),
                'preferred_hues': [30, 45, 60, 200, 220],  # Earth tones and soft blues
                'temperature': 'warm'
            },
            'scandinavian': {
                'saturation_range': (0.1, 0.4),
                'lightness_range': (0.75, 0.95),
                'preferred_hues': [0, 200, 220, 240],  # Whites and cool blues
                'temperature': 'cool'
            },
            'minimalist': {
                'saturation_range': (0.0, 0.15),
                'lightness_range': (0.2, 0.95),
                'preferred_hues': [0, 60, 120, 180, 240, 300],  # Any hue, low saturation
                'temperature': 'neutral'
            },
            'industrial': {
                'saturation_range': (0.1, 0.5),
                'lightness_range': (0.2, 0.7),
                'preferred_hues': [0, 30, 200, 220, 240],  # Grays, browns, steels
                'temperature': 'cool'
            },
            'mediterranean': {
                'saturation_range': (0.3, 0.8),
                'lightness_range': (0.4, 0.8),
                'preferred_hues': [20, 40, 60, 180, 200, 220, 240],  # Earthy and sea colors
                'temperature': 'warm'
            }
        }
        
        # Mood adjustments
        self.mood_adjustments = {
            'calm': {'saturation': -0.2, 'lightness': 0.1},
            'cozy': {'saturation': 0.1, 'lightness': -0.1},
            'luxury': {'saturation': 0.2, 'lightness': -0.2},
            'energetic': {'saturation': 0.3, 'lightness': 0.0}
        }
        
        # Lighting adjustments
        self.lighting_adjustments = {
            'daylight': {'temperature': 0, 'brightness': 0},
            'warm_light': {'temperature': 0.1, 'brightness': -0.05},
            'cool_led': {'temperature': -0.1, 'brightness': 0.05}
        }
        
        # Palette name generators
        self.palette_names = {
            'prefixes': ['Serene', 'Vibrant', 'Dreamy', 'Bold', 'Gentle', 'Rich', 'Fresh', 'Warm', 'Cool', 'Deep'],
            'themes': ['Ocean', 'Forest', 'Sunset', 'Dawn', 'Garden', 'Stone', 'Sand', 'Sky', 'Earth', 'Moonlight'],
            'suffixes': ['Harmony', 'Whisper', 'Embrace', 'Glow', 'Essence', 'Dream', 'Breeze', 'Touch', 'Aura', 'Calm']
        }
    
    def generate_palette(self, dominant_colors, style='scandinavian', mood='calm', lighting='daylight'):
        """Generate a complete palette from dominant colors"""
        try:
            # Select best colors for the style
            base_colors = self._select_style_colors(dominant_colors, style)
            
            # Generate harmony palette from base colors
            if base_colors:
                primary_rgb = base_colors[0]
                h, l, s = colorsys.rgb_to_hls(primary_rgb[0]/255, primary_rgb[1]/255, primary_rgb[2]/255)
                h = h * 360  # Convert to degrees
                harmony_palette = self._generate_harmony_colors(h, s, l, 'complementary')
            else:
                harmony_palette = base_colors
            
            # Apply style, mood, and lighting adjustments
            adjusted_palette = self._apply_style_mood_lighting(
                harmony_palette, style, mood, lighting
            )
            
            # Add color roles and names
            final_palette = self._assign_color_roles(adjusted_palette)
            
            # Generate palette name
            palette_name = self._generate_palette_name(final_palette, mood, style)
            
            return {
                'name': palette_name,
                'colors': final_palette,
                'style': style,
                'mood': mood,
                'lighting': lighting,
                'created_at': self.get_current_timestamp()
            }
            
        except Exception as e:
            self.logger.error(f"Error generating palette: {str(e)}")
            raise
    
    def generate_harmony_palette(self, base_colors, harmony_type, style, mood, lighting):
        """Generate palette based on color harmony theory"""
        try:
            if not base_colors:
                raise ValueError("No base colors provided")
            
            # Convert first color to HSL for harmony calculations
            primary_color = base_colors[0]
            if isinstance(primary_color, dict):
                rgb = primary_color.get('rgb', [128, 128, 128])
            else:
                rgb = primary_color
            
            h, l, s = colorsys.rgb_to_hls(rgb[0]/255, rgb[1]/255, rgb[2]/255)
            h = h * 360  # Convert to degrees
            
            # Generate harmony colors
            harmony_colors = self._generate_harmony_colors(h, s, l, harmony_type)
            
            # Apply adjustments
            adjusted_palette = self._apply_style_mood_lighting(
                harmony_colors, style, mood, lighting
            )
            
            # Add color roles
            final_palette = self._assign_color_roles(adjusted_palette)
            
            # Generate name
            palette_name = self._generate_palette_name(final_palette, mood, style)
            
            return {
                'name': palette_name,
                'colors': final_palette,
                'harmony_type': harmony_type,
                'style': style,
                'mood': mood,
                'lighting': lighting,
                'created_at': self.get_current_timestamp()
            }
            
        except Exception as e:
            self.logger.error(f"Error generating harmony palette: {str(e)}")
            raise
    
    def _generate_harmony_colors(self, h, s, l, harmony_type):
        """Generate colors based on color harmony theory"""
        colors = []
        
        if harmony_type == 'complementary':
            colors = [
                self._hsl_to_rgb(h, s, l),
                self._hsl_to_rgb((h + 180) % 360, s * 0.8, l),
                self._hsl_to_rgb(h, s * 0.3, l + 0.2),
                self._hsl_to_rgb((h + 180) % 360, s * 0.3, l + 0.2),
                self._hsl_to_rgb(h, s * 0.1, l + 0.3)
            ]
        
        elif harmony_type == 'analogous':
            colors = [
                self._hsl_to_rgb(h, s, l),
                self._hsl_to_rgb((h + 30) % 360, s * 0.9, l),
                self._hsl_to_rgb((h - 30) % 360, s * 0.9, l),
                self._hsl_to_rgb((h + 60) % 360, s * 0.7, l + 0.1),
                self._hsl_to_rgb((h - 60) % 360, s * 0.7, l + 0.1)
            ]
        
        elif harmony_type == 'triadic':
            colors = [
                self._hsl_to_rgb(h, s, l),
                self._hsl_to_rgb((h + 120) % 360, s * 0.8, l),
                self._hsl_to_rgb((h + 240) % 360, s * 0.8, l),
                self._hsl_to_rgb(h, s * 0.3, l + 0.2),
                self._hsl_to_rgb((h + 120) % 360, s * 0.3, l + 0.2)
            ]
        
        elif harmony_type == 'tetradic':
            colors = [
                self._hsl_to_rgb(h, s, l),
                self._hsl_to_rgb((h + 90) % 360, s * 0.9, l),
                self._hsl_to_rgb((h + 180) % 360, s * 0.8, l),
                self._hsl_to_rgb((h + 270) % 360, s * 0.9, l),
                self._hsl_to_rgb(h, s * 0.2, l + 0.3)
            ]
        
        elif harmony_type == 'monochromatic':
            colors = [
                self._hsl_to_rgb(h, s, l),
                self._hsl_to_rgb(h, s * 0.8, l + 0.1),
                self._hsl_to_rgb(h, s * 0.6, l + 0.2),
                self._hsl_to_rgb(h, s * 0.4, l + 0.3),
                self._hsl_to_rgb(h, s * 0.2, l + 0.4)
            ]
        
        return colors
    
    def _hsl_to_rgb(self, h, s, l):
        """Convert HSL to RGB"""
        h_norm = h / 360.0
        r, g, b = colorsys.hls_to_rgb(h_norm, l, s)
        return [int(r * 255), int(g * 255), int(b * 255)]
    
    def _select_style_colors(self, dominant_colors, style):
        """Select colors that fit the style"""
        style_rule = self.style_rules.get(style, self.style_rules['scandinavian'])
        selected_colors = []
        
        for color_info in dominant_colors:
            hsl = color_info['hsl']
            saturation = hsl['s'] / 100.0
            lightness = hsl['l'] / 100.0
            
            # Check if color fits style rules
            sat_min, sat_max = style_rule['saturation_range']
            light_min, light_max = style_rule['lightness_range']
            
            if sat_min <= saturation <= sat_max and light_min <= lightness <= light_max:
                selected_colors.append(color_info['rgb'])
        
        # If no colors fit, adjust the most frequent colors
        if not selected_colors:
            selected_colors = [color_info['rgb'] for color_info in dominant_colors[:3]]
        
        return selected_colors
    
    def _apply_style_mood_lighting(self, colors, style, mood, lighting):
        """Apply style, mood, and lighting adjustments to colors"""
        adjusted_colors = []
        
        mood_adj = self.mood_adjustments.get(mood, {'saturation': 0, 'lightness': 0})
        lighting_adj = self.lighting_adjustments.get(lighting, {'temperature': 0, 'brightness': 0})
        
        for rgb in colors:
            # Convert to HSL
            r, g, b = rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0
            h, l, s = colorsys.rgb_to_hls(r, g, b)
            
            # Apply mood adjustments
            s = max(0, min(1, s + mood_adj['saturation']))
            l = max(0, min(1, l + mood_adj['lightness']))
            
            # Apply lighting adjustments
            if lighting_adj['temperature'] > 0:  # Warm light
                h = h + 0.02 if h < 0.98 else h
            elif lighting_adj['temperature'] < 0:  # Cool light
                h = h - 0.02 if h > 0.02 else h
            
            l = max(0, min(1, l + lighting_adj['brightness']))
            
            # Convert back to RGB
            r, g, b = colorsys.hls_to_rgb(h, l, s)
            adjusted_rgb = [int(r * 255), int(g * 255), int(b * 255)]
            adjusted_colors.append(adjusted_rgb)
        
        return adjusted_colors
    
    def _assign_color_roles(self, colors):
        """Assign roles to colors in the palette"""
        roles = ['Primary', 'Secondary', 'Accent', 'Neutral', 'Background']
        palette = []
        
        for i, rgb in enumerate(colors):
            role = roles[i] if i < len(roles) else f'Color {i + 1}'
            
            color_info = {
                'rgb': rgb,
                'hex': self._rgb_to_hex(rgb),
                'hsl': self._rgb_to_hsl(rgb),
                'cmyk': self._rgb_to_cmyk(rgb),
                'role': role,
                'locked': False
            }
            palette.append(color_info)
        
        return palette
    
    def _generate_palette_name(self, colors, mood, style):
        """Generate a creative name for the palette"""
        prefix = random.choice(self.palette_names['prefixes'])
        theme = random.choice(self.palette_names['themes'])
        suffix = random.choice(self.palette_names['suffixes'])
        
        # Add mood or style influence
        if mood == 'luxury':
            prefix = random.choice(['Rich', 'Deep', 'Bold'])
        elif mood == 'calm':
            prefix = random.choice(['Serene', 'Gentle', 'Soft'])
        elif mood == 'energetic':
            prefix = random.choice(['Vibrant', 'Bold', 'Fresh'])
        
        return f"{prefix} {theme} {suffix}"
    
    def adjust_for_lighting(self, colors, lighting_type):
        """Adjust existing colors for different lighting conditions"""
        lighting_adj = self.lighting_adjustments.get(lighting_type, {'temperature': 0, 'brightness': 0})
        adjusted_colors = []
        
        for color in colors:
            rgb = color.get('rgb', [128, 128, 128])
            
            # Convert to HSL
            r, g, b = rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0
            h, l, s = colorsys.rgb_to_hls(r, g, b)
            
            # Apply lighting adjustments
            if lighting_adj['temperature'] > 0:  # Warm light
                h = min(1, h + 0.02)
            elif lighting_adj['temperature'] < 0:  # Cool light
                h = max(0, h - 0.02)
            
            l = max(0, min(1, l + lighting_adj['brightness']))
            
            # Convert back to RGB
            r, g, b = colorsys.hls_to_rgb(h, l, s)
            adjusted_rgb = [int(r * 255), int(g * 255), int(b * 255)]
            
            adjusted_color = color.copy()
            adjusted_color['rgb'] = adjusted_rgb
            adjusted_color['hex'] = self._rgb_to_hex(adjusted_rgb)
            adjusted_colors.append(adjusted_color)
        
        return adjusted_colors
    
    def create_swatch_image(self, colors, palette_name, width=800, height=400):
        """Create a PNG swatch image of the palette"""
        try:
            # Create image
            image = Image.new('RGB', (width, height), color=(255, 255, 255))
            draw = ImageDraw.Draw(image)
            
            # Calculate swatch dimensions
            num_colors = len(colors)
            swatch_width = width // num_colors
            
            # Draw color swatches
            for i, color in enumerate(colors):
                rgb = color.get('rgb', [128, 128, 128])
                x1 = i * swatch_width
                x2 = x1 + swatch_width
                
                # Draw color rectangle
                draw.rectangle((x1, 0, x2, int(height * 0.7)), fill=tuple(rgb))
                
                # Add hex code text
                hex_code = color.get('hex', '#808080')
                text_y = int(height * 0.75)
                
                # Simple text drawing (Pillow default font)
                text_bbox = draw.textbbox((0, 0), hex_code)
                text_width = text_bbox[2] - text_bbox[0]
                text_x = x1 + (swatch_width - text_width) // 2
                
                draw.text((text_x, text_y), hex_code, fill=(0, 0, 0))
                
                # Add role text
                role = color.get('role', f'Color {i+1}')
                role_bbox = draw.textbbox((0, 0), role)
                role_width = role_bbox[2] - role_bbox[0]
                role_x = x1 + (swatch_width - role_width) // 2
                
                draw.text((role_x, text_y + 20), role, fill=(0, 0, 0))
            
            # Add palette name
            name_bbox = draw.textbbox((0, 0), palette_name)
            name_width = name_bbox[2] - name_bbox[0]
            name_x = (width - name_width) // 2
            draw.text((name_x, int(height * 0.85)), palette_name, fill=(0, 0, 0))
            
            # Convert to bytes
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            return buffer.getvalue()
            
        except Exception as e:
            self.logger.error(f"Error creating swatch image: {str(e)}")
            raise
    
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
    
    def get_current_timestamp(self):
        """Get current timestamp"""
        return datetime.now().isoformat()
