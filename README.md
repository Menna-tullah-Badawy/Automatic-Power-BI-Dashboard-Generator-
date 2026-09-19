# 🎯 Automatic Power BI Dashboard Generator | 100% Free

Fully automated dashboard builder for Power BI. It cleans your data, analyzes columns, builds KPI metrics, designs the layout, and creates a branded theme automatically. All you do is pick a color theme and point to your data file.

---
## 🚀 How to run in Visual Studio Code:
1.  Open this folder in VS Code
2.  Open terminal (Ctrl+` )
3.  Install required packages once:
    ```bash
    pip install pandas openpyxl
    ```
4.  Run the tool:
    ```bash
    python auto_powerbi_generator.py
    ```
    *(Windows users can also double click `run.bat` directly)*

5.  Follow the prompts:
    - Enter a theme number from 1 to 7
    - Enter your data file path (`.xlsx` or `.csv` format)
    - Wait ~5 seconds for the tool to finish

---
## 🎨 Available Themes:
| ID | Theme Name | Style |
|---|---|---|
| 1 | FitPro_Red_Sports | Red + Black/White (Gym/Sports style) |
| 2 | Wallet_Teal | Soft teal/green (Finance/Wallet style) |
| 3 | Dark_Analytics_Purple | Dark purple/blue/pink (Analytics dark mode) |
| 4 | Trading_Neon_Green | Neon green on black (Trading/Crypto style) |
| 5 | Luxury_Gold | Gold accents on dark (Executive premium style) |
| 6 | Rexora_Light_Green | Light modern green (Light mode CRM/Sales) |
| 7 | Control_Dark_Blue | Dark blue/purple (Admin/Management style) |

---
## ✅ What it does automatically:
1.  **Data Cleaning**: Removes duplicates, fills missing values, fixes date/numeric formatting
2.  **Column Detection**: Automatically identifies dates, metrics, categories, locations, status columns, IDs
3.  **KPI Generation**: Creates relevant cards (Total Sales, Profit, Quantity, Growth %, Average Order Value...)
4.  **Layout Design**: Automatically places visuals in optimal positions:
    - Top KPI card row
    - Time trend line chart
    - Category bar + donut charts
    - Status distribution pie chart
    - Geographic map (if location columns exist)
    - Full details table at bottom
    - Left-side filter/slicer pane
5.  **Theme Generation**: Creates a Power BI-compatible JSON theme with rounded corners, matching colors, and styled cards
6.  **Step-by-step import guide**: Written instructions to import everything into Power BI in 3 clicks

---
## 📁 Output files (in `output_dashboard` folder after running):
1.  `cleaned_data.xlsx`: Your fully cleaned dataset ready for import
2.  `[theme_name]_theme.json`: Power BI custom theme file
3.  `PowerBI_Setup_Guide.txt`: Step by step import instructions for Power BI Desktop
4.  `Data_Analysis_Report.txt`: Automatic summary statistics for your dataset

---
## 🧪 To test with sample data first:
If you don't have your data ready, run this first to generate 2000 rows of sample sales data:
```bash
python create_sample_data.py
```
Then run the generator, and enter `sample_sales_data.xlsx` as your input file.

---
## 📌 Requirements:
- Python 3.8+
- Power BI Desktop (completely free to download from Microsoft official website)
- Your data as Excel (.xlsx) or CSV file

No paid tools, no subscriptions, no API keys required. Works completely offline.
