"""
Script to help replace placeholder images with actual screenshots
"""

import os
import shutil

def replace_screenshot(placeholder_name, actual_path):
    """Replace a placeholder image with an actual screenshot"""
    if os.path.exists(actual_path):
        try:
            shutil.copy2(actual_path, f"screenshots/{placeholder_name}")
            print(f"✅ Replaced {placeholder_name} with actual screenshot")
            return True
        except Exception as e:
            print(f"❌ Error replacing {placeholder_name}: {e}")
            return False
    else:
        print(f"❌ Actual screenshot not found at {actual_path}")
        return False

def main():
    """Main function to guide screenshot replacement"""
    print("📸 Screenshot Replacement Tool")
    print("=" * 40)
    print("This tool helps you replace placeholder images with actual screenshots.")
    print("\nCurrent placeholders:")
    placeholders = [
        "dashboard_overview.png",
        "candlestick_chart.png", 
        "portfolio_analysis.png",
        "trading_signals.png"
    ]
    
    for i, placeholder in enumerate(placeholders, 1):
        print(f"{i}. {placeholder}")
    
    print("\nTo replace screenshots:")
    print("1. Capture actual screenshots of your running dashboard")
    print("2. Save them with the names shown above")
    print("3. Provide the full path to each screenshot when prompted")
    print("4. The tool will replace the placeholders automatically")
    
    input("\nPress Enter to continue...")
    
    print("\n📝 Enter the full path to each actual screenshot (or press Enter to skip):")
    
    for placeholder in placeholders:
        actual_path = input(f"\nPath to {placeholder} (or Enter to skip): ").strip()
        if actual_path:
            replace_screenshot(placeholder, actual_path)
    
    print("\n✅ Screenshot replacement process completed!")
    print("📝 Check the screenshots directory to verify the replacements")

if __name__ == "__main__":
    main()