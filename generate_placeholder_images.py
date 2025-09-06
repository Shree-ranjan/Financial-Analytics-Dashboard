"""
Generate placeholder images for the screenshots directory
"""

import os
from PIL import Image, ImageDraw, ImageFont

def create_placeholder_image(filename, width=800, height=600, text="Dashboard View"):
    """Create a placeholder image with text"""
    # Create a new image with a blue background
    image = Image.new('RGB', (width, height), color=(26, 115, 232))
    draw = ImageDraw.Draw(image)
    
    # Add text to the image
    try:
        # Try to use a default font
        font = ImageFont.load_default()
    except:
        # Fallback if font loading fails
        font = None
    
    # Calculate text position
    text_width = draw.textlength(text, font=font) if font else len(text) * 10
    text_height = 20  # Approximate height
    
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # Draw text
    draw.text((x, y), text, fill=(255, 255, 255), font=font)
    
    # Add filename at bottom
    footer_text = f"File: {filename}"
    footer_x = (width - draw.textlength(footer_text, font=font) if font else len(footer_text) * 10) // 2
    draw.text((footer_x, height - 30), footer_text, fill=(255, 255, 255), font=font)
    
    # Save image
    image.save(filename)
    print(f"Created placeholder image: {filename}")

def main():
    """Generate placeholder images for dashboard screenshots"""
    # Create screenshots directory if it doesn't exist
    if not os.path.exists("screenshots"):
        os.makedirs("screenshots")
        print("Created 'screenshots' directory")
    
    # Change to screenshots directory
    os.chdir("screenshots")
    
    # Create placeholder images
    screenshots = [
        ("dashboard_overview.png", "Dashboard Overview"),
        ("candlestick_chart.png", "Candlestick Chart with Indicators"),
        ("portfolio_analysis.png", "Portfolio Analysis"),
        ("trading_signals.png", "Trading Signals")
    ]
    
    for filename, text in screenshots:
        create_placeholder_image(filename, text=text)
    
    print("\n✅ Placeholder images created successfully!")
    print("📝 Replace these with actual screenshots of your dashboard")
    print("📁 Images saved in the 'screenshots' directory")

if __name__ == "__main__":
    main()