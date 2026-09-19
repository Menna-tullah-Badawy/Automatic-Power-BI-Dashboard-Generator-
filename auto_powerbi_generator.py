#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automatic Power BI Dashboard Generator
100% Free, No Subscriptions Required
Features:
- Auto cleans raw data (handles missing values, fixes dates/numbers, removes duplicates)
- Auto detects column types: dates, measures, categories, IDs, locations, status
- Auto generates KPI cards (Total Sales, Profit, Growth %... etc)
- Auto designs dashboard layout based on data structure, no manual work needed
- Exports cleaned data, Power BI theme JSON, and step-by-step import guide
"""

import pandas as pd
import numpy as np
import os
import json
from datetime import datetime

# ============== THEMES CONFIGURATION ==============
THEMES = {
    "1": {
        "name": "FitPro_Red_Sports",
        "primary": "#C4122E",
        "secondary": "#111827",
        "accent": "#DC2626",
        "neutral": "#6B7280",
        "background": "#FFFFFF",
        "success": "#10B981",
        "warning": "#F59E0B",
        "danger": "#EF4444"
    },
    "2": {
        "name": "Wallet_Teal",
        "primary": "#10B981",
        "secondary": "#34D399",
        "accent": "#3B82F6",
        "neutral": "#6B7280",
        "background": "#F8FAFC",
        "success": "#059669",
        "warning": "#FBBF24",
        "danger": "#F87171"
    },
    "3": {
        "name": "Dark_Analytics_Purple",
        "primary": "#8B5CF6",
        "secondary": "#06B6D4",
        "accent": "#EC4899",
        "neutral": "#64748B",
        "background": "#0F172A",
        "text": "#F1F5F9",
        "success": "#22C55E",
        "warning": "#F97316",
        "danger": "#EF4444"
    },
    "4": {
        "name": "Trading_Neon_Green",
        "primary": "#10B981",
        "secondary": "#00FFAA",
        "accent": "#06B6D4",
        "neutral": "#334155",
        "background": "#030712",
        "text": "#ECFDF5",
        "success": "#00FF88",
        "warning": "#FBBF24",
        "danger": "#FF4444"
    },
    "5": {
        "name": "Luxury_Gold",
        "primary": "#D4AF37",
        "secondary": "#F2C96E",
        "accent": "#A67C00",
        "neutral": "#9CA3AF",
        "background": "#1C1917",
        "text": "#FEF3C7",
        "success": "#84CC16",
        "warning": "#F97316",
        "danger": "#DC2626"
    },
    "6": {
        "name": "Rexora_Light_Green",
        "primary": "#92E3A9",
        "secondary": "#34D399",
        "accent": "#8B5CF6",
        "neutral": "#94A3B8",
        "background": "#F8FAFC",
        "text": "#1E293B",
        "success": "#22C55E",
        "warning": "#F59E0B",
        "danger": "#EF4444"
    },
    "7": {
        "name": "Control_Dark_Blue",
        "primary": "#3B82F6",
        "secondary": "#8B5CF6",
        "accent": "#06B6D4",
        "neutral": "#64748B",
        "background": "#0F172A",
        "text": "#F8FAFC",
        "success": "#10B981",
        "warning": "#F97316",
        "danger": "#F43F5E"
    }
}

# ============== AUTO DATA CLEANING FUNCTIONS ==============
def detect_column_types(df):
    """Auto detects column types: dates, numerics, categories, IDs, names, locations, status"""
    col_types = {
        "dates": [],
        "numerics": [],
        "categorical": [],
        "ids": [],
        "names": [],
        "locations": [],
        "status": []
    }
    
    for col in df.columns:
        # First: numeric columns = numbers, skip date check for them
        if pd.api.types.is_numeric_dtype(df[col]):
            if "id" in col.lower() or "code" in col.lower():
                col_types["ids"].append(col)
            else:
                col_types["numerics"].append(col)
            continue
        
        # For text columns: check if it's a date
        sample = df[col].dropna().head(20)
        date_count = 0
        for val in sample:
            try:
                if pd.notna(pd.to_datetime(val, errors='raise')):
                    date_count +=1
            except:
                pass
        if date_count / max(len(sample),1) > 0.7:
            col_types["dates"].append(col)
            continue

        # Text column processing
        unique_count = df[col].nunique()
        total_count = len(df)
        
        # ID/Code detection
        if unique_count / total_count > 0.8 or any(word in col.lower() for word in ["id", "code", "order no", "order id", "invoice"]):
            col_types["ids"].append(col)
            continue
            
        # Location detection
        if any(word in col.lower() for word in ["city", "country", "region", "state", "location", "area", "governorate"]):
            col_types["locations"].append(col)
            continue
            
        # Low unique count = Category / Status
        if unique_count / total_count < 0.15:
            if any(word in col.lower() for word in ["status", "state"]):
                col_types["status"].append(col)
            else:
                col_types["categorical"].append(col)
        # High unique count = Names/People/Products
        else:
            if any(word in col.lower() for word in ["name", "customer", "product", "client", "user", "employee"]):
                col_types["names"].append(col)
            else:
                col_types["categorical"].append(col)
    
    return col_types

def clean_data(df, col_types=None):
    """Auto cleans the dataset"""
    # Trim column names
    df.columns = [str(col).strip() for col in df.columns]
    
    # Remove duplicates
    df = df.drop_duplicates(keep='first')
    
    # Handle missing values
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            if df[col].isna().sum() / len(df) < 0.3:
                df[col] = df[col].fillna(df[col].median())
            else:
                df[col] = df[col].fillna(0)
        else:
            df[col] = df[col].fillna("Unknown")
            df[col] = df[col].astype(str).str.strip()
    
    # Fix date formatting
    if col_types:
        for col in col_types["dates"]:
            try:
                df[col] = pd.to_datetime(df[col], errors='coerce')
                df[col] = df[col].ffill()
            except:
                pass
    
    return df

def generate_kpis(col_types, df):
    """Auto generates relevant KPI metrics based on data type"""
    kpis = []
    
    # Total records KPI
    kpis.append({
        "name": "Total Records",
        "type": "card",
        "value": len(df),
        "format": "#,##0"
    })
    
    # Priority order for numerics (show important metrics first)
    priority_order = ["sales", "revenue", "profit", "total", "amount", "quantity", "price", "cost"]
    sorted_nums = sorted(col_types["numerics"], key=lambda x: next((i for i, p in enumerate(priority_order) if p in x.lower()), 999))
    
    # Pick top 4 important numerics for KPI row
    selected_nums = sorted_nums[:4]
    for num_col in selected_nums:
        total = df[num_col].sum()
        kpis.append({
            "name": f"Total {num_col}",
            "type": "card",
            "field": num_col,
            "aggregation": "sum",
            "format": "#,##0.00" if total > 1000 else "0.00"
        })
        
        # Calculate growth % if date column exists
        if len(col_types["dates"]) > 0:
            date_col = col_types["dates"][0]
            df_sorted = df.sort_values(date_col)
            half = len(df_sorted) // 2
            if half > 0:
                prev = df_sorted.iloc[:half][num_col].sum()
                curr = df_sorted.iloc[half:][num_col].sum()
                if prev != 0:
                    growth = ((curr - prev) / prev) * 100
                    kpis.append({
                        "name": f"{num_col} Growth",
                        "type": "growth_indicator",
                        "value": f"{growth:+.1f}%",
                        "color": "#22C55E" if growth >= 0 else "#EF4444"
                    })
    
    # Average order value
    main_num = [n for n in selected_nums if any(word in n.lower() for word in ["sales", "revenue", "total", "amount", "profit"])]
    if main_num:
        avg_val = df[main_num[0]].mean()
        kpis.append({
            "name": f"Average {main_num[0]} per record",
            "type": "card",
            "field": main_num[0],
            "aggregation": "average",
            "value": round(avg_val, 2),
            "format": "#,##0.00"
        })
    
    return kpis

def generate_dashboard_layout(col_types, df):
    """Auto generates dashboard layout/visuals structure based on data type"""
    layout = {
        "sections": []
    }
    
    # 1. Top KPI row (always first)
    layout["sections"].append({
        "name": "Key Performance Indicators",
        "type": "kpi_row",
        "position": "top",
        "elements": "auto_generated_kpis"
    })
    
    # 2. Date column = Line chart for time trend
    if len(col_types["dates"]) > 0 and len(col_types["numerics"]) > 0:
        main_metric = next((n for n in col_types["numerics"] if any(w in n.lower() for w in ["sales", "revenue", "profit", "total"])), col_types["numerics"][0])
        layout["sections"].append({
            "name": f"{main_metric} Trend over {col_types['dates'][0]}",
            "type": "line_chart",
            "x_axis": col_types["dates"][0],
            "y_axis": col_types["numerics"][:3],
            "position": "left_large"
        })
    
    # 3. Categorical columns = Bar / Donut chart for distribution
    valid_cats = [c for c in col_types["categorical"] 
                  if c not in col_types["ids"] 
                  and not any(word in c.lower() for word in ["name", "product", "customer", "client", "user"])]
    if len(valid_cats) > 0:
        cat_col = valid_cats[0]
        prefered_num = None
        for num in col_types["numerics"]:
            if any(word in num.lower() for word in ["sales", "revenue", "profit", "total", "amount"]):
                prefered_num = num
                break
        if not prefered_num and col_types["numerics"]:
            prefered_num = col_types["numerics"][-1]
            
        if prefered_num:
            layout["sections"].append({
                "name": f"{prefered_num} by {cat_col}",
                "type": "bar_chart",
                "x_axis": cat_col,
                "y_axis": prefered_num,
                "position": "right_small"
            })
            
            layout["sections"].append({
                "name": f"{prefered_num} Share",
                "type": "donut_chart",
                "category": cat_col,
                "value": prefered_num,
                "position": "right_small"
            })
    
    # 4. Status column = Pie chart for status distribution
    if len(col_types["status"]) > 0:
        layout["sections"].append({
            "name": f"Distribution by {col_types['status'][0]}",
            "type": "pie_chart",
            "category": col_types["status"][0],
            "value": prefered_num if prefered_num else "count",
            "position": "middle_left"
        })
    
    # 5. Location column = Map
    if len(col_types["locations"]) > 0:
        layout["sections"].append({
            "name": "Geographic Distribution",
            "type": "filled_map",
            "location": col_types["locations"][0],
            "value": prefered_num if prefered_num else "count",
            "position": "middle_right"
        })
    
    # 6. Bottom details table (always last)
    table_fields = col_types["dates"][:1] + col_types["names"][:2] + col_types["categorical"][:1] + col_types["numerics"][:3] + col_types["status"][:1]
    layout["sections"].append({
        "name": "Detailed Data Table",
        "type": "table",
        "fields": table_fields,
        "position": "bottom_full"
    })
    
    # 7. Filter pane
    valid_filters = [c for c in col_types["categorical"] 
                     if c not in col_types["ids"]
                     and not any(word in c.lower() for word in ["name", "product", "customer", "client", "user"])]
    name_filters = [c for c in col_types["categorical"] 
                    if any(word in c.lower() for word in ["name", "product", "customer", "client", "user"])][:2]
    layout["filters"] = col_types["dates"][:1] + valid_filters[:3] + col_types["status"][:2] + col_types["locations"][:2] + name_filters
    
    return layout

def create_powerbi_theme(theme_choice):
    """Creates a Power BI compatible JSON theme file with selected colors"""
    theme = THEMES[theme_choice]
    
    pbi_theme = {
        "name": theme["name"],
        "dataColors": [theme["primary"], theme["accent"], theme["secondary"], 
                       theme["success"], theme["warning"], theme["danger"],
                       "#8B5CF6", "#06B6D4", "#F97316"],
        "background": theme["background"],
        "foreground": theme.get("text", "#1E293B"),
        "tableAccent": theme["primary"],
        "visualStyles": {
            "*": {
                "*": {
                    "*": [{
                        "fontFamily": "Segoe UI",
                        "fontSize": 11
                    }]
                },
                "card": {
                    "*": [{
                        "categoryLabels": [{"color": {"solid": {"color": theme["neutral"]}}}],
                        "dataLabels": [{"color": {"solid": {"color": theme["primary"]}}, "fontSize": 18, "bold": True}],
                        "background": [{"transparency": 0, "color": {"solid": {"color": theme["background"]}}}],
                        "border": [{"show": True, "color": {"solid": {"color": theme["primary"]+"20"}}, "radius": 12}],
                        "padding": [15]
                    }]
                },
                "lineChart": {
                    "*": [{
                        "legend": [{"show": True, "color": {"solid": {"color": theme.get("text", "#1E293B")}}}],
                        "categoryAxis": [{"color": {"solid": {"color": theme["neutral"]}}}],
                        "valueAxis": [{"color": {"solid": {"color": theme["neutral"]}}}],
                        "background": [{"transparency":0, "color": {"solid": {"color": theme["background"]}}}],
                        "border": [{"show":True, "radius": 12, "color": {"solid": {"color": theme["primary"]+"15"}}}]
                    }]
                },
                "barChart": {
                    "*": [{
                        "background": [{"transparency":0, "color": {"solid": {"color": theme["background"]}}}],
                        "border": [{"show":True, "radius":12, "color": {"solid": {"color": theme["primary"]+"15"}}}]
                    }]
                },
                "donutChart": {
                    "*": [{
                        "background": [{"transparency":0, "color": {"solid": {"color": theme["background"]}}}],
                        "border": [{"show":True, "radius":12, "color": {"solid": {"color": theme["primary"]+"15"}}}]
                    }]
                },
                "pieChart": {
                    "*": [{
                        "background": [{"transparency":0, "color": {"solid": {"color": theme["background"]}}}],
                        "border": [{"show":True, "radius":12, "color": {"solid": {"color": theme["primary"]+"15"}}}]
                    }]
                },
                "filledMap": {
                    "*": [{
                        "background": [{"transparency":0, "color": {"solid": {"color": theme["background"]}}}],
                        "border": [{"show":True, "radius":12, "color": {"solid": {"color": theme["primary"]+"15"}}}]
                    }]
                },
                "tableEx": {
                    "*": [{
                        "background": [{"transparency":0, "color": {"solid": {"color": theme["background"]}}}],
                        "border": [{"show":True, "radius":12, "color": {"solid": {"color": theme["primary"]+"15"}}}]
                    }]
                }
            },
            "page": {
                "*": {
                    "background": [{
                        "color": {"solid": {"color": theme["background"]}}
                    }],
                    "outspace": [{"color": {"solid": {"color": theme["background"]}}}]
                }
            }
        }
    }
    
    return pbi_theme

def auto_generate_dashboard(input_file_path, theme_choice, output_dir="output_dashboard"):
    """Main function: runs the full generation process automatically"""
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Read input data
    print(f"[1/7] Reading file: {input_file_path}")
    if input_file_path.endswith('.xlsx') or input_file_path.endswith('.xls'):
        df = pd.read_excel(input_file_path)
    elif input_file_path.endswith('.csv'):
        for encoding in ['utf-8', 'latin1', 'cp1252']:
            try:
                df = pd.read_csv(input_file_path, encoding=encoding)
                break
            except:
                continue
    else:
        print("ERROR: Unsupported file format. Use .xlsx or .csv only")
        return None
    
    # 2. Detect column types
    print("[2/7] Auto detecting column types...")
    col_types = detect_column_types(df)
    
    print(f"✅ Detected columns:")
    print(f"   - Date columns: {col_types['dates']}")
    print(f"   - Numeric/Measure columns: {col_types['numerics']}")
    print(f"   - Category columns: {col_types['categorical']}")
    print(f"   - Status columns: {col_types['status']}")
    print(f"   - Location columns: {col_types['locations']}")
    
    # 3. Clean data
    print("[3/7] Auto cleaning dataset...")
    df_clean = clean_data(df, col_types)
    
    # 4. Generate KPIs
    print("[4/7] Auto generating KPI metrics...")
    kpis = generate_kpis(col_types, df_clean)
    print(f"✅ Generated {len(kpis)} key performance indicators")
    
    # 5. Generate dashboard layout
    print("[5/7] Auto designing dashboard layout...")
    layout = generate_dashboard_layout(col_types, df_clean)
    print(f"✅ Dashboard layout ready with {len(layout['sections'])} sections")
    
    # 6. Export cleaned data
    print("[6/7] Exporting cleaned data...")
    clean_data_path = os.path.join(output_dir, "cleaned_data.xlsx")
    df_clean.to_excel(clean_data_path, index=False)
    print(f"✅ Saved cleaned data to: {clean_data_path}")
    
    # 7. Export Power BI theme
    print("[7/7] Exporting Power BI theme...")
    theme = create_powerbi_theme(theme_choice)
    theme_path = os.path.join(output_dir, f"{THEMES[theme_choice]['name']}_theme.json")
    with open(theme_path, "w", encoding="utf-8") as f:
        json.dump(theme, f, indent=2)
    print(f"✅ Saved Power BI theme to: {theme_path}")
    
    # Save setup guide
    guide_path = os.path.join(output_dir, "PowerBI_Setup_Guide.txt")
    with open(guide_path, "w", encoding="utf-8") as f:
        f.write("="*60 + "\n")
        f.write("Power BI Dashboard Setup Guide - 5 Easy Steps\n")
        f.write("="*60 + "\n\n")
        f.write(f"Selected Theme: {THEMES[theme_choice]['name']}\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write("-"*60 + "\n")
        f.write("Steps to import into Power BI Desktop (Free):\n")
        f.write("-"*60 + "\n")
        f.write("1. Open Power BI Desktop (free download from Microsoft website)\n")
        f.write("2. Click Get Data > Excel > Select `cleaned_data.xlsx`\n")
        f.write("3. Go to View > Themes > Browse for themes > Select the JSON theme file\n")
        f.write("4. Add visuals to the canvas in this order:\n\n")
        
        f.write(f"📊 Top Row (KPI Cards):\n")
        for kpi in kpis[:6]:
            if 'field' in kpi:
                f.write(f"  • Card visual for: {kpi['name']}\n")
            else:
                f.write(f"  • {kpi['name']}: {kpi['value']}\n")
        
        f.write(f"\n📈 Main Visuals:\n")
        for section in layout["sections"]:
            if section["type"] != "kpi_row":
                f.write(f"  • {section['name']} -> Visual type: {section['type']}\n")
        
        f.write("\n🔍 Add these slicers/filters to the left pane:\n")
        for filter_col in layout["filters"]:
            f.write(f"  • Filter for: {filter_col}\n")
        
        f.write("\n💡 All KPIs and metrics calculate automatically in Power BI when you drag columns onto visuals!\n")
        f.write("\n🎉 Done! Your branded dashboard is ready to use.")
    
    print(f"✅ Saved setup guide to: {guide_path}")
    
    # Save data analysis report
    report_path = os.path.join(output_dir, "Data_Analysis_Report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("="*60 + "\n")
        f.write("Auto Data Analysis Report\n")
        f.write("="*60 + "\n\n")
        f.write(f"Total Rows: {len(df_clean):,}\n")
        f.write(f"Total Columns: {len(df_clean.columns)}\n\n")
        f.write("-"*60 + "\n")
        f.write("Columns by type:\n")
        for typ, cols in col_types.items():
            if cols:
                f.write(f"\n{typ.title()}:\n")
                for c in cols:
                    f.write(f"  - {c}\n")
        
        f.write("\n" + "-"*60 + "\n")
        f.write("Quick Statistics:\n")
        for num_col in col_types["numerics"]:
            f.write(f"\n{num_col}:\n")
            f.write(f"  • Sum: {df_clean[num_col].sum():,.2f}\n")
            f.write(f"  • Average: {df_clean[num_col].mean():,.2f}\n")
            f.write(f"  • Min: {df_clean[num_col].min():,.2f}\n")
            f.write(f"  • Max: {df_clean[num_col].max():,.2f}\n")
    
    print(f"✅ Saved analysis report to: {report_path}")
    
    print("\n" + "="*60)
    print("🎉 SUCCESS! All files generated!")
    print(f"📂 Output folder: {output_dir}")
    print("="*60)
    
    return {
        "clean_data_path": clean_data_path,
        "theme_path": theme_path,
        "guide_path": guide_path,
        "col_types": col_types,
        "kpis": kpis,
        "layout": layout
    }

if __name__ == "__main__":
    import sys
    print("="*60)
    print("Automatic Power BI Dashboard Generator")
    print("="*60)
    print("\nAvailable themes:")
    for k, v in THEMES.items():
        print(f"  [{k}] {v['name']}")
    
    # Check if args passed from command line
    if len(sys.argv) >=3:
        theme_choice = sys.argv[1]
        input_path = sys.argv[2]
    else:
        theme_choice = input("\nEnter theme number: ").strip()
        input_path = input("Enter data file path (Excel/CSV): ").strip()
    
    if theme_choice not in THEMES:
        print("Invalid selection, using default theme 7: Control_Dark_Blue")
        theme_choice = "7"
    
    if not os.path.exists(input_path):
        print(f"ERROR: File not found: {input_path}")
        input("Press Enter to exit...")
        exit(1)
    
    auto_generate_dashboard(input_path, theme_choice)
    if len(sys.argv) <3:
        input("\nPress Enter to exit...")
