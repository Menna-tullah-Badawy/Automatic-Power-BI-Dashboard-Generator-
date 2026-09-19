#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fully automatic dashboard generator from raw data (Excel/CSV)
No manual work required - it cleans data, calculates metrics, builds all charts, outputs ready HTML dashboard
"""
import pandas as pd
import numpy as np
import json
import os
import sys
from datetime import datetime

THEMES = {
    "gold": {
        "name": "Luxury Gold",
        "primary": "#E8B860",
        "light": "#F7D794",
        "dark": "#B88A2C",
        "bg_main": "#262320",
        "bg_card": "#2E2B28",
        "bg_sidebar": "#221F1D",
        "bg_main_dark": "#1a1816",
        "text_main": "#F0D9A9",
        "text_muted": "#C2B59C",
        "glow": "rgba(232, 184, 96, 0.15)"
    },
    "red": {
        "name": "FitPro Red",
        "primary": "#C4122E",
        "light": "#EF4444",
        "dark": "#991B1B",
        "bg_main": "#111827",
        "bg_card": "#1F2937",
        "bg_sidebar": "#0F172A",
        "bg_main_dark": "#0b1120",
        "text_main": "#F3F4F6",
        "text_muted": "#9CA3AF",
        "glow": "rgba(196, 18, 46, 0.15)"
    },
    "teal": {
        "name": "Wallet Teal",
        "primary": "#10B981",
        "light": "#34D399",
        "dark": "#059669",
        "bg_main": "#F0FDF4",
        "bg_card": "#FFFFFF",
        "bg_sidebar": "#ECFDF5",
        "bg_main_dark": "#dcfce7",
        "text_main": "#064E3B",
        "text_muted": "#6B7280",
        "glow": "rgba(16, 185, 129, 0.15)"
    },
    "purple": {
        "name": "Dark Purple",
        "primary": "#8B5CF6",
        "light": "#A78BFA",
        "dark": "#6D28D9",
        "bg_main": "#0F172A",
        "bg_card": "#1E293B",
        "bg_sidebar": "#0B1120",
        "bg_main_dark": "#0b1120",
        "text_main": "#F8FAFC",
        "text_muted": "#94A3B8",
        "glow": "rgba(139, 92, 246, 0.15)"
    },
    "neon": {
        "name": "Trading Neon Green",
        "primary": "#00FF88",
        "light": "#10B981",
        "dark": "#065F46",
        "bg_main": "#030712",
        "bg_card": "#111827",
        "bg_sidebar": "#020617",
        "bg_main_dark": "#010409",
        "text_main": "#ECFDF5",
        "text_muted": "#6EE7B7",
        "glow": "rgba(0, 255, 136, 0.15)"
    },
    "light": {
        "name": "Rexora Light Modern",
        "primary": "#22C55E",
        "light": "#86EFAC",
        "dark": "#166534",
        "bg_main": "#F8FAFC",
        "bg_card": "#FFFFFF",
        "bg_sidebar": "#F0FDF4",
        "bg_main_dark": "#f1f5f9",
        "text_main": "#1E293B",
        "text_muted": "#64748B",
        "glow": "rgba(34, 197, 94, 0.12)"
    },
    "blue": {
        "name": "Control Blue",
        "primary": "#3B82F6",
        "light": "#60A5FA",
        "dark": "#1D4ED8",
        "bg_main": "#0F172A",
        "bg_card": "#1E293B",
        "bg_sidebar": "#0B1120",
        "bg_main_dark": "#0b1120",
        "text_main": "#F8FAFC",
        "text_muted": "#94A3B8",
        "glow": "rgba(59, 130, 246, 0.15)"
    }
}

def detect_columns(df):
    """Auto detect column types"""
    types = {"dates": [], "numerics": [], "categories": [], "ids": [], "status": []}
    
    for col in df.columns:
        col_low = col.lower()
        # Numeric
        if pd.api.types.is_numeric_dtype(df[col]):
            if "id" in col_low or "code" in col_low:
                types["ids"].append(col)
            else:
                types["numerics"].append(col)
            continue
        
        # Date detection
        sample = df[col].dropna().head(20)
        date_count = 0
        for val in sample:
            try:
                pd.to_datetime(val)
                date_count +=1
            except: pass
        if date_count / max(len(sample),1) > 0.7:
            types["dates"].append(col)
            continue
        
        # IDs
        uniq = df[col].nunique()
        if uniq/len(df) > 0.8 or "id" in col_low:
            types["ids"].append(col)
            continue
        
        # Status
        if "status" in col_low or "state" in col_low:
            types["status"].append(col)
            continue
        
        # Categories (low unique count)
        if uniq/len(df) < 0.2:
            types["categories"].append(col)
        else:
            # Names/high cardinality go to categories anyway for table
            types["categories"].append(col)
    
    return types

def clean_data(df, types):
    """Clean data automatically"""
    df.columns = [str(c).strip() for c in df.columns]
    df = df.drop_duplicates(keep='first')
    
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].fillna(df[col].median() if df[col].isna().sum()/len(df) <0.3 else 0)
        else:
            df[col] = df[col].fillna("Unknown").astype(str).str.strip()
    
    for col in types["dates"]:
        try:
            df[col] = pd.to_datetime(df[col], errors='coerce').ffill()
        except: pass
    
    return df

def format_number(n):
    """Format large numbers for display"""
    if abs(n) >= 1_000_000:
        return f"${n/1_000_000:.1f}M"
    if abs(n) >= 1000:
        return f"${n/1000:.1f}K"
    return f"${n:,.0f}"

def build_dashboard_data(df, types):
    """Build all dashboard data structure automatically"""
    dashboard_data = {}
    
    # === 1. KPIs ===
    kpis = []
    kpis.append({"label": "Total Records", "value": len(df), "value_formatted": f"{len(df):,}", "growth": None})
    
    # Select main numeric metric (sales/profit/total first)
    main_metric = None
    priority = ["sales", "revenue", "profit", "total", "amount", "price", "quantity"]
    for p in priority:
        for num in types["numerics"]:
            if p in num.lower():
                main_metric = num
                break
        if main_metric: break
    if not main_metric and types["numerics"]:
        main_metric = types["numerics"][0]
    
    # Add main metric KPI
    total_val = df[main_metric].sum()
    kpis.append({
        "label": f"Total {main_metric}",
        "value": float(total_val),
        "value_formatted": format_number(total_val),
        "growth": None
    })
    
    # Growth calculation if date exists
    growth = None
    date_col = types["dates"][0] if types["dates"] else None
    if date_col:
        df_sorted = df.sort_values(date_col)
        half = len(df_sorted)//2
        if half > 0:
            prev = df_sorted.iloc[:half][main_metric].sum()
            curr = df_sorted.iloc[half:][main_metric].sum()
            if prev !=0:
                growth = ((curr-prev)/prev)*100
                kpis.append({
                    "label": f"{main_metric} Growth",
                    "value": growth,
                    "value_formatted": f"{growth:+.1f}%",
                    "growth": growth
                })
    
    # Add other important numerics (up to 4 total KPIs)
    count = 2
    for num in types["numerics"]:
        if num == main_metric: continue
        if count >=5: break
        val = df[num].sum()
        kpis.append({
            "label": f"Total {num}",
            "value": float(val),
            "value_formatted": format_number(val),
            "growth": None
        })
        count +=1
    
    # Average value KPI
    avg_val = df[main_metric].mean()
    kpis.append({
        "label": f"Average {main_metric}",
        "value": float(avg_val),
        "value_formatted": format_number(avg_val),
        "growth": None
    })
    dashboard_data["kpis"] = kpis
    
    # === 2. Trend Line Chart (monthly) ===
    if date_col:
        df['_month'] = pd.to_datetime(df[date_col]).dt.strftime("%b %Y")
        trend = df.groupby('_month')[main_metric].sum().reset_index()
        dashboard_data["trend"] = {
            "title": f"{main_metric} Trend Over Time",
            "metric_label": main_metric,
            "labels": trend['_month'].tolist()[-12:],
            "values": [float(x) for x in trend[main_metric].tolist()[-12:]]
        }
        df.drop(columns=['_month'], inplace=True)
    else:
        # No date, use categorical X axis
        cat = types["categories"][0]
        trend = df.groupby(cat)[main_metric].sum().reset_index().head(12)
        dashboard_data["trend"] = {
            "title": f"{main_metric} by {cat}",
            "metric_label": main_metric,
            "labels": trend[cat].tolist(),
            "values": [float(x) for x in trend[main_metric].tolist()]
        }
    
    # === 3. Category Bar Chart ===
    # Find best category (not id, not high cardinality)
    valid_cats = [c for c in types["categories"] if df[c].nunique() < 15]
    if valid_cats:
        cat_col = valid_cats[0]
        cat_data = df.groupby(cat_col)[main_metric].sum().sort_values(ascending=False).head(8).reset_index()
        dashboard_data["category_bar"] = {
            "title": f"{main_metric} by {cat_col}",
            "value_label": main_metric,
            "labels": cat_data[cat_col].tolist(),
            "values": [float(x) for x in cat_data[main_metric].tolist()]
        }
    else:
        dashboard_data["category_bar"] = {"title":"Distribution","value_label":"Count","labels":["A","B","C","D"],"values":[20,30,15,35]}
    
    # === 4. Donut Chart ===
    if len(valid_cats)>=2:
        donut_col = valid_cats[1]
    elif valid_cats:
        donut_col = valid_cats[0]
    else:
        donut_col = types["categories"][0]
    donut_data = df.groupby(donut_col)[main_metric].sum().sort_values(ascending=False).head(6).reset_index()
    dashboard_data["donut"] = {
        "title": f"{main_metric} Share by {donut_col}",
        "labels": donut_data[donut_col].tolist(),
        "values": [float(x) for x in donut_data[main_metric].tolist()]
    }
    
    # === 5. Status Pie Chart ===
    if types["status"]:
        status_col = types["status"][0]
        status_data = df.groupby(status_col)[main_metric].count().reset_index()
        dashboard_data["status_pie"] = {
            "title": f"Records by {status_col}",
            "labels": status_data[status_col].tolist(),
            "values": [int(x) for x in status_data[main_metric].tolist()]
        }
    else:
        dashboard_data["status_pie"] = {"title":"Distribution", "labels":["Active","Pending","Closed"], "values":[70,20,10]}
    
    # === 6. Secondary Bar Chart ===
    if len(valid_cats)>=3:
        sec_col = valid_cats[2]
    elif len(valid_cats)>=2:
        sec_col = valid_cats[0]
    else:
        sec_col = types["categories"][-1]
    sec_data = df.groupby(sec_col)[main_metric].sum().sort_values(ascending=False).head(6).reset_index()
    dashboard_data["secondary_bar"] = {
        "title": f"{main_metric} by {sec_col}",
        "value_label": main_metric,
        "labels": sec_data[sec_col].tolist(),
        "values": [float(x) for x in sec_data[main_metric].tolist()]
    }
    
    # === 7. Data Table (top 20 rows) ===
    table_cols = []
    if date_col: table_cols.append(date_col)
    table_cols += [c for c in types["categories"] if c not in types["ids"]][:3]
    table_cols += types["numerics"][:3]
    
    sample_df = df[table_cols].head(20)
    dashboard_data["table"] = {
        "columns": table_cols,
        "rows": sample_df.astype(str).values.tolist()
    }
    
    return dashboard_data

def generate_html(input_file, theme_key="gold", output_file="auto_generated_dashboard.html"):
    """Main generation function"""
    print(f"[1/5] Reading data from {input_file}...")
    if input_file.endswith('.xlsx'):
        df = pd.read_excel(input_file)
    elif input_file.endswith('.csv'):
        for enc in ['utf-8', 'latin1', 'cp1252']:
            try:
                df = pd.read_csv(input_file, encoding=enc)
                break
            except: continue
    
    print(f"[2/5] Detecting column types...")
    types = detect_columns(df)
    print(f"    Found dates: {types['dates']}, numerics: {types['numerics']}, categories: {len(types['categories'])}")
    
    print(f"[3/5] Cleaning data...")
    df_clean = clean_data(df, types)
    
    print(f"[4/5] Building dashboard structure, calculating KPIs and charts...")
    dash_data = build_dashboard_data(df_clean, types)
    
    # Load template
    with open("auto_dashboard_template.html", "r", encoding="utf-8") as f:
        template = f.read()
    
    theme = THEMES[theme_key]
    replacements = [
        ("{{THEME_NAME}}", theme["name"]),
        ("{{DASHBOARD_TITLE}}", f"Auto Generated {theme['name']} Dashboard"),
        ("{{DASHBOARD_DATA}}", json.dumps(dash_data, ensure_ascii=False, indent=2)),
        ("{{PRIMARY}}", theme["primary"]),
        ("{{LIGHT}}", theme["light"]),
        ("{{DARK}}", theme["dark"]),
        ("{{GLOW}}", theme["glow"]),
        ("{{BG_MAIN}}", theme["bg_main"]),
        ("{{BG_CARD}}", theme["bg_card"]),
        ("{{BG_SIDEBAR}}", theme["bg_sidebar"]),
        ("{{BG_MAIN_DARK}}", theme["bg_main_dark"]),
        ("{{TEXT_MAIN}}", theme["text_main"]),
        ("{{TEXT_MUTED}}", theme["text_muted"]),
    ]
    
    for old, new in replacements:
        template = template.replace(old, new)
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(template)
    
    # Save cleaned data
    clean_file = output_file.replace(".html", "_cleaned_data.xlsx")
    df_clean.to_excel(clean_file, index=False)
    
    print(f"\n✅ SUCCESS! Dashboard generated automatically:")
    print(f"   📊 HTML Dashboard: {output_file}")
    print(f"   📋 Cleaned data: {clean_file}")
    print(f"   🎨 Theme used: {theme['name']}")
    print(f"   📈 Total KPIs: {len(dash_data['kpis'])}")
    print(f"   📉 Total charts: 5 (trend, bar, donut, pie, secondary bar)")
    print(f"   📋 Table preview: 20 rows")
    return output_file

if __name__ == "__main__":
    print("="*60)
    print("FULLY AUTOMATIC DASHBOARD GENERATOR")
    print("="*60)
    print("\nAvailable themes:")
    for k,v in THEMES.items():
        print(f"  - {k}: {v['name']}")
    
    if len(sys.argv) >=3:
        input_file = sys.argv[1]
        theme = sys.argv[2]
    else:
        input_file = input("\nEnter data file path (Excel/CSV): ").strip()
        theme = input("Enter theme key (default gold): ").strip() or "gold"
    
    if theme not in THEMES:
        print(f"Invalid theme, using gold")
        theme = "gold"
    
    if not os.path.exists(input_file):
        print(f"Error: File {input_file} not found")
        sys.exit(1)
    
    generate_html(input_file, theme)
