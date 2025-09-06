# 📸 Screenshot Guide for Financial Analytics Dashboard

This guide explains how to capture and manage screenshots for the Financial Analytics Dashboard documentation.

## 📋 Overview

Screenshots are essential for showcasing the dashboard's features and functionality in the README and other documentation. This project provides tools to help you capture, organize, and maintain high-quality screenshots.

## 🛠️ Tools Provided

1. **[capture_screenshots.py](../capture_screenshots.py)** - Opens the dashboard in your browser for easy screenshot capture
2. **[generate_placeholder_images.py](../generate_placeholder_images.py)** - Creates placeholder images for documentation
3. **[replace_screenshots.py](../replace_screenshots.py)** - Helps replace placeholder images with actual screenshots
4. **[screenshots/](../screenshots/)** - Directory containing all dashboard screenshots

## 📷 Capturing Screenshots

### Method 1: Using the Capture Tool

1. Start the dashboard:
   ```bash
   python -m streamlit run src/dashboard/main_dashboard.py
   ```

2. Run the capture tool in another terminal:
   ```bash
   python capture_screenshots.py
   ```

3. The dashboard will open in your default browser
4. Capture screenshots of the following views:
   - Main dashboard overview
   - Candlestick chart with indicators
   - Portfolio analysis section
   - Trading signals section

### Method 2: Manual Capture

1. Start the dashboard:
   ```bash
   python -m streamlit run src/dashboard/main_dashboard.py
   ```

2. Navigate to `http://localhost:8501` in your browser
3. Use your system's screenshot tool to capture the required views

## 📁 Screenshot Organization

All screenshots should be saved in the [screenshots/](../screenshots/) directory with these specific names:

- `dashboard_overview.png` - Main dashboard showing real-time stock data and technical indicators
- `candlestick_chart.png` - Interactive candlestick chart with RSI, Moving Averages, and Bollinger Bands
- `portfolio_analysis.png` - Portfolio performance tracking with multiple stocks
- `trading_signals.png` - Automated trading signals based on technical analysis

## 🔄 Replacing Placeholder Images

The project comes with placeholder images generated automatically. To replace them with actual screenshots:

1. Run the replacement tool:
   ```bash
   python replace_screenshots.py
   ```

2. Provide the full path to each actual screenshot when prompted
3. The tool will automatically replace the placeholders

## 🎨 Best Practices

### Image Quality
- Use high-resolution images (1920x1080 or higher)
- Save in PNG format for best quality
- Ensure text is readable and charts are clear

### Content Guidelines
- Remove any sensitive information before capturing
- Show real (or realistic) financial data
- Capture all key dashboard features
- Update screenshots when UI changes are made

### Consistency
- Use the same browser and zoom level for all screenshots
- Maintain consistent window sizes
- Capture the same time period/data where possible

## 📚 Documentation Integration

Screenshots are automatically displayed in the README.md file. When you replace placeholder images with actual screenshots, the documentation will automatically update to show your real dashboard views.

## 🔧 Troubleshooting

### Dashboard Not Loading
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check that the dashboard is running: `python -m streamlit run src/dashboard/main_dashboard.py`
- Verify the URL: `http://localhost:8501`

### Screenshot Tool Issues
- Make sure you have a default browser configured
- Check that Python PIL/Pillow is installed: `pip install Pillow`
- Ensure you have write permissions to the screenshots directory

### Image Quality Problems
- Increase browser zoom level before capturing
- Use a high-DPI display for better screenshot quality
- Consider using professional screenshot tools for better results

## 🚀 Professional Showcase

High-quality screenshots are crucial for showcasing this project on professional platforms like:
- LinkedIn
- GitHub README
- Portfolio websites
- Technical interviews
- Conference presentations

Well-crafted screenshots can significantly improve the visual appeal and professional impact of your project documentation.