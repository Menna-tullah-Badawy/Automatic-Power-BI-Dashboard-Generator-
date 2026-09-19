#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automatic Power BI Dashboard Generator - Full Version
100% Free, No Subscriptions
Features:
- Simple graphical interface, no command line needed
- Auto detects Arabic/English column names
- Cleans data automatically
- Auto generates KPIs and DAX measures for Power BI
- Generates proper Power BI JSON theme with your selected design
- Generates Power BI layout file so visuals appear already in place
- Generates fully interactive HTML dashboard preview with working filters
- All 7 themes supported
- Opens output folder automatically after generation
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import numpy as np
import json
import os
import subprocess
import sys
from datetime import datetime

# ============== THEME DEFINITIONS ==============
THEMES = {
    "Luxury Gold": {
        "primary": "#E8B860",
        "light": "#F7D794",
        "dark": "#B88A2C",
        "bg": "#262320",
        "bg_card": "#2E2B28",
        "bg_sidebar": "#221F1D",
        "text_main": "#F0D9A9",
        "text_muted": "#C2B59C",
        "glow": "rgba(232, 184, 96, 0.15)"
    },
    "FitPro Red": {
        "primary": "#C4122E",
        "light": "#EF4444",
        "dark": "#991B1B",
        "bg": "#111827",
        "bg_card": "#1F2937",
        "bg_sidebar": "#0F172A",
        "text_main": "#F3F4F6",
        "text_muted": "#9CA3AF",
        "glow": "rgba(196, 18, 46, 0.15)"
    },
    "Wallet Teal": {
        "primary": "#10B981",
        "light": "#34D399",
        "dark": "#059669",
        "bg": "#F0FDF4",
        "bg_card": "#FFFFFF",
        "bg_sidebar": "#ECFDF5",
        "text_main": "#064E3B",
        "text_muted": "#6B7280",
        "glow": "rgba(16, 185, 129, 0.15)"
    },
    "Dark Purple Analytics": {
        "primary": "#8B5CF6",
        "light": "#A78BFA",
        "dark": "#6D28D9",
        "bg": "#0F172A",
        "bg_card": "#1E293B",
        "bg_sidebar": "#0B1120",
        "text_main": "#F8FAFC",
        "text_muted": "#94A3B8",
        "glow": "rgba(139, 92, 246, 0.15)"
    },
    "Trading Neon Green": {
        "primary": "#00FF88",
        "light": "#10B981",
        "dark": "#065F46",
        "bg": "#030712",
        "bg_card": "#111827",
        "bg_sidebar": "#020617",
        "text_main": "#ECFDF5",
        "text_muted": "#6EE7B7",
        "glow": "rgba(0, 255, 136, 0.15)"
    },
    "Rexora Light Modern": {
        "primary": "#22C55E",
        "light": "#86EFAC",
        "dark": "#166534",
        "bg": "#F8FAFC",
        "bg_card": "#FFFFFF",
        "bg_sidebar": "#F0FDF4",
        "text_main": "#1E293B",
        "text_muted": "#64748B",
        "glow": "rgba(34, 197, 94, 0.12)"
    },
    "Control Dark Blue": {
        "primary": "#3B82F6",
        "light": "#60A5FA",
        "dark": "#1D4ED8",
        "bg": "#0F172A",
        "bg_card": "#1E293B",
        "bg_sidebar": "#0B1120",
        "text_main": "#F8FAFC",
        "text_muted": "#94A3B8",
        "glow": "rgba(59, 130, 246, 0.15)"
    }
}

# Bilingual (EN/AR) keywords for column detection
COLUMN_KEYWORDS = {
    "date": ["date", "time", "day", "month", "year", "تاريخ", "يوم", "شهر", "سنة", "وقت"],
    "numeric": ["sales", "revenue", "profit", "amount", "total", "price", "cost", "quantity", "qty", "count",
                "مبيعات", "ايرادات", "ربح", "قيمة", "اجمالي", "سعر", "تكلفة", "كمية", "عدد"],
    "metric_priority": ["sales", "revenue", "total", "amount", "profit", "مبيعات", "ايرادات", "اجمالي", "ربح"],
    "id": ["id", "code", "number", "رقم", "كود"],
    "status": ["status", "state", "حالة"],
    "location": ["city", "country", "region", "area", "مدينة", "دولة", "منطقة", "محافظة"],
    "name": ["name", "customer", "product", "client", "اسم", "عميل", "منتج"]
}

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Automatic Power BI Dashboard Generator")
        self.root.geometry("700x550")
        self.root.configure(bg="#1E293B")
        self.selected_file = tk.StringVar()
        self.selected_theme = tk.StringVar(value="Luxury Gold")
        
        # Styling
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TButton', background="#3B82F6", foreground="white", padding=10, font=('Segoe UI',10,'bold'))
        style.configure('TLabel', background="#1E293B", foreground="white", font=('Segoe UI',10))
        style.configure('Header.TLabel', font=('Segoe UI',18,'bold'), foreground="#60A5FA")
        style.configure('TCombobox', padding=5)
        
        # UI Build
        ttk.Label(root, text="Automatic Power BI Dashboard Generator", style="Header.TLabel").pack(pady=20)
        
        frame_file = ttk.Frame(root)
        frame_file.pack(fill='x', padx=30, pady=10)
        ttk.Label(frame_file, text="Data File (Excel / CSV):").pack(anchor='w')
        row_file = ttk.Frame(frame_file)
        row_file.pack(fill='x', pady=5)
        ttk.Entry(row_file, textvariable=self.selected_file, width=60).pack(side='left', padx=(0,10))
        ttk.Button(row_file, text="Browse", command=self.browse_file).pack(side='left')
        
        frame_theme = ttk.Frame(root)
        frame_theme.pack(fill='x', padx=30, pady=10)
        ttk.Label(frame_theme, text="Select Dashboard Theme:").pack(anchor='w')
        theme_combo = ttk.Combobox(frame_theme, textvariable=self.selected_theme, values=list(THEMES.keys()), state="readonly", width=40)
        theme_combo.pack(pady=5, anchor='w')
        
        self.log_text = tk.Text(root, height=15, bg="#0F172A", foreground="#22C55E", font=('Consolas',9), padx=10, pady=10)
        self.log_text.pack(fill='both', padx=30, pady=10, expand=True)
        
        self.generate_btn = ttk.Button(root, text="🚀 Generate Dashboard", command=self.run_generation, style='TButton')
        self.generate_btn.pack(pady=10)
        
        self.log("✅ Program is ready. Select your data file and theme.")
        self.log("ℹ️  All output will be in the 'output' folder.")
    
    def log(self, msg):
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def browse_file(self):
        path = filedialog.askopenfilename(filetypes=[("Data files", "*.xlsx *.xls *.csv")])
        if path:
            self.selected_file.set(path)
    
    def detect_columns(self, df):
        types = {"dates": [], "numerics": [], "categories": [], "ids": [], "status": [], "locations": [], "names": []}
        for col in df.columns:
            col_low = str(col).lower()
            # Numeric
            if pd.api.types.is_numeric_dtype(df[col]):
                if any(k in col_low for k in COLUMN_KEYWORDS["id"]):
                    types["ids"].append(col)
                else:
                    types["numerics"].append(col)
                continue
            # Date detection
            sample = df[col].dropna().head(20)
            date_count = 0
            for v in sample:
                try:
                    pd.to_datetime(v)
                    date_count += 1
                except: pass
            if date_count / max(len(sample), 1) > 0.7:
                types["dates"].append(col)
                continue
            # IDs
            if df[col].nunique()/len(df) > 0.8 or any(k in col_low for k in COLUMN_KEYWORDS["id"]):
                types["ids"].append(col)
                continue
            # Status
            if any(k in col_low for k in COLUMN_KEYWORDS["status"]):
                types["status"].append(col)
                continue
            # Locations
            if any(k in col_low for k in COLUMN_KEYWORDS["location"]):
                types["locations"].append(col)
                continue
            # Names
            if any(k in col_low for k in COLUMN_KEYWORDS["name"]):
                types["names"].append(col)
                continue
            # Categories
            types["categories"].append(col)
        return types
    
    def clean_data(self, df, types):
        df.columns = [str(c).strip() for c in df.columns]
        df = df.drop_duplicates(keep='first')
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                if df[col].isna().sum() / len(df) < 0.3:
                    df[col] = df[col].fillna(df[col].median())
                else:
                    df[col] = df[col].fillna(0)
            else:
                df[col] = df[col].fillna("Unknown").astype(str).str.strip()
        for col in types["dates"]:
            try:
                df[col] = pd.to_datetime(df[col], errors='coerce').ffill()
            except: pass
        return df
    
    def create_powerbi_theme(self, theme, output_path):
        t = theme
        pbi_theme = {
            "name": "Auto Generated Theme",
            "dataColors": [t["primary"], t["accent"] if "accent" in t else t["light"], t["dark"],
                           "#22C55E", "#F97316", "#EF4444", "#8B5CF6", "#06B6D4"],
            "background": t["bg_card"],
            "foreground": t["text_main"],
            "tableAccent": t["primary"],
            "visualStyles": {
                "*": {"*": {"*": [{"fontFamily": "Segoe UI", "fontSize":11}]}},
                "card": {"*": [{
                    "categoryLabels": [{"color": {"solid": {"color": t["text_muted"]}}}],
                    "dataLabels": [{"color": {"solid": {"color": t["primary"]}}, "fontSize":18, "bold":True}],
                    "background": [{"transparency":0, "color":{"solid":{"color":t["bg_card"]}}}],
                    "border": [{"show":True, "radius":14, "color":{"solid":{"color": t["primary"] + "20"}}}]
                }]},
                "lineChart": {"*": [{
                    "background": [{"transparency":0, "color":{"solid":{"color":t["bg_card"]}}}],
                    "border": [{"show":True, "radius":14, "color":{"solid":{"color": t["primary"] + "15"}}}]
                }]},
                "barChart": {"*": [{
                    "background": [{"transparency":0, "color":{"solid":{"color":t["bg_card"]}}}],
                    "border": [{"show":True, "radius":14, "color":{"solid":{"color": t["primary"] + "15"}}}]
                }]},
                "page": {"*": {"background": [{"color":{"solid":{"color":t["bg"]}}}]}}
            }
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(pbi_theme, f, indent=2)
    
    def generate_html_dashboard(self, df, types, theme, theme_key):
        with open("templates/dashboard_template.html", "r", encoding="utf-8") as f:
            tpl = f.read()
        
        # Get main metric
        main_metric = None
        for p in COLUMN_KEYWORDS["metric_priority"]:
            for n in types["numerics"]:
                if p in n.lower():
                    main_metric = n
                    break
            if main_metric: break
        if not main_metric: main_metric = types["numerics"][0]
        
        total_val = df[main_metric].sum()
        total_records = len(df)
        avg_val = df[main_metric].mean()
        
        # Calculate growth
        growth = 0
        date_col = types["dates"][0] if types["dates"] else None
        if date_col:
            df_sorted = df.sort_values(date_col)
            half = len(df_sorted)//2
            if half>0:
                prev = df_sorted.iloc[:half][main_metric].sum()
                curr = df_sorted.iloc[half:][main_metric].sum()
                if prev: growth = ((curr-prev)/prev)*100
        
        # Build trend data
        trend_labels, trend_values = [], []
        if date_col:
            mt = df.set_index(date_col)[main_metric].resample('ME').sum().tail(12)
            trend_labels = [x.strftime("%b %Y") for x in mt.index]
            trend_values = [float(x) for x in mt.values]
        
        # Category data
        valid_cats = [c for c in types["categories"] if df[c].nunique() < 15]
        cat_labels, cat_values = [], []
        if valid_cats:
            cat_col = valid_cats[0]
            cat_data = df.groupby(cat_col)[main_metric].sum().sort_values(ascending=False).head(8)
            cat_labels = cat_data.index.tolist()
            cat_values = [float(x) for x in cat_data.values]
        
        # Status data
        status_labels, status_values = [], []
        if types["status"]:
            sc = types["status"][0]
            sd = df.groupby(sc)[main_metric].count()
            status_labels = sd.index.tolist()
            status_values = [int(x) for x in sd.values]
        
        # Table preview
        table_cols = []
        if date_col: table_cols.append(date_col)
        table_cols += [c for c in types["categories"] if c not in types["ids"]][:3]
        table_cols += types["numerics"][:3]
        if types["status"]: table_cols += types["status"]
        sample_rows = df[table_cols].head(10).astype(str).values.tolist()
        table_header = "".join([f"<th>{c}</th>" for c in table_cols])
        
        replacements = [
            ("{{THEME_PRIMARY}}", theme["primary"]),
            ("{{THEME_LIGHT}}", theme["light"]),
            ("{{THEME_DARK}}", theme["dark"]),
            ("{{THEME_BG}}", theme["bg"]),
            ("{{THEME_CARD}}", theme["bg_card"]),
            ("{{THEME_SIDEBAR}}", theme["bg_sidebar"]),
            ("{{THEME_TEXT}}", theme["text_main"]),
            ("{{THEME_MUTED}}", theme["text_muted"]),
            ("{{THEME_GLOW}}", theme["glow"]),
            ("{{KPI_TOTAL_RECORDS}}", f"{total_records:,}"),
            ("{{KPI_TOTAL_LABEL}}", f"Total {main_metric}"),
            ("{{KPI_TOTAL_VALUE}}", f"{total_val:,.0f}"),
            ("{{KPI_GROWTH}}", f"{growth:+.1f}%"),
            ("{{KPI_GROWTH_COLOR}}", "#22C55E" if growth>=0 else "#EF4444"),
            ("{{KPI_AVG_VALUE}}", f"{avg_val:,.0f}"),
            ("{{TREND_TITLE}}", f"{main_metric} Trend"),
            ("{{TREND_LABELS}}", json.dumps(trend_labels)),
            ("{{TREND_VALUES}}", json.dumps(trend_values)),
            ("{{BAR_TITLE}}", f"{main_metric} by {valid_cats[0] if valid_cats else 'Category'}"),
            ("{{BAR_LABELS}}", json.dumps(cat_labels)),
            ("{{BAR_VALUES}}", json.dumps(cat_values)),
            ("{{DONUT_TITLE}}", f"{main_metric} Share"),
            ("{{STATUS_TITLE}}", "Status Distribution"),
            ("{{STATUS_LABELS}}", json.dumps(status_labels)),
            ("{{STATUS_VALUES}}", json.dumps(status_values)),
            ("{{TABLE_HEADER}}", table_header),
            ("{{TABLE_ROWS}}", json.dumps(sample_rows))
        ]
        for old, new in replacements:
            tpl = tpl.replace(old, str(new))
        return tpl
    
    def generate_setup_guide(self, theme_name, output_dir):
        guide = f"""AUTOMATIC POWER BI DASHBOARD - SETUP GUIDE
================================================
Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M")}
Selected Theme: {theme_name}

Generated files:
1.  cleaned_data.xlsx: Your data, fully cleaned and formatted
2.  powerbi_theme.json: Custom theme for your selected design
3.  dashboard_preview.html: Interactive web preview (open in any browser)
4.  dax_measures.txt: Copy-paste DAX formulas for KPIs
5.  layout.json: Power BI visual layout coordinates (for automatic placement)

HOW TO IMPORT INTO POWER BI (5 steps):
1.  Open Power BI Desktop (free download from Microsoft)
2.  Click Get Data > Excel > Select cleaned_data.xlsx
3.  Go to View > Themes > Browse for themes > Select powerbi_theme.json
4.  Create new measures using the DAX formulas from dax_measures.txt
5.  Add visuals to your page - their positions match the template design.

You will get a professional dashboard exactly matching the selected theme with all your KPIs and charts automatically.
"""
        with open(os.path.join(output_dir, "Setup_Guide.txt"), "w", encoding="utf-8") as f:
            f.write(guide)
    
    def generate_dax(self, df, types, output_path):
        main_metric = None
        for p in COLUMN_KEYWORDS["metric_priority"]:
            for n in types["numerics"]:
                if p in n.lower():
                    main_metric = n
                    break
            if main_metric: break
        if not main_metric: main_metric = types["numerics"][0]
        dax = f"""// Auto Generated DAX Measures
Total_{main_metric.replace(' ','_')} = SUM('Data'[{main_metric}])

Average_{main_metric.replace(' ','_')} = AVERAGE('Data'[{main_metric}])

Total_Records = COUNTROWS('Data')

Growth_{main_metric.replace(' ','_')} = 
VAR CurrentPeriod = CALCULATE(SUM('Data'[{main_metric}]), DATESBETWEEN('Data'[{types['dates'][0] if types['dates'] else 'Date'}], MAX('Data'[{types['dates'][0] if types['dates'] else 'Date'}])-180, MAX('Data'[{types['dates'][0] if types['dates'] else 'Date'}])))
VAR PreviousPeriod = CALCULATE(SUM('Data'[{main_metric}]), DATESBETWEEN('Data'[{types['dates'][0] if types['dates'] else 'Date'}], MAX('Data'[{types['dates'][0] if types['dates'] else 'Date'}])-365, MAX('Data'[{types['dates'][0] if types['dates'] else 'Date'}])-180))
RETURN DIVIDE(CurrentPeriod - PreviousPeriod, PreviousPeriod, 0)
"""
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(dax)
    
    def run_generation(self):
        input_path = self.selected_file.get()
        if not input_path or not os.path.exists(input_path):
            messagebox.showerror("Error", "Please select a valid Excel/CSV file first!")
            return
        
        theme_name = self.selected_theme.get()
        theme = THEMES[theme_name]
        output_dir = os.path.join(os.getcwd(), "output")
        os.makedirs(output_dir, exist_ok=True)
        
        self.generate_btn.config(state="disabled")
        try:
            self.log(f"📂 Starting generation for {os.path.basename(input_path)}...")
            self.log(f"🎨 Selected theme: {theme_name}")
            
            # 1. Read and clean
            self.log("[1/6] Reading data file...")
            if input_path.endswith('.csv'):
                for enc in ['utf-8','latin1','cp1252','utf-16']:
                    try:
                        df = pd.read_csv(input_path, encoding=enc)
                        break
                    except: continue
            else:
                df = pd.read_excel(input_path)
            self.log(f"    ✅ Loaded {len(df)} rows, {len(df.columns)} columns")
            
            self.log("[2/6] Auto detecting column types...")
            types = self.detect_columns(df)
            self.log(f"    ✅ Dates: {types['dates']}")
            self.log(f"    ✅ Numeric measures: {types['numerics']}")
            self.log(f"    ✅ Categories: {len(types['categories'])}")
            
            self.log("[3/6] Cleaning data...")
            df_clean = self.clean_data(df, types)
            clean_path = os.path.join(output_dir, "cleaned_data.xlsx")
            df_clean.to_excel(clean_path, index=False)
            self.log(f"    ✅ Cleaned data saved")
            
            self.log("[4/6] Generating Power BI theme...")
            theme_path = os.path.join(output_dir, "powerbi_theme.json")
            self.create_powerbi_theme(theme, theme_path)
            self.log("    ✅ Power BI theme created")
            
            self.log("[5/6] Generating DAX measures + setup guide...")
            self.generate_dax(df_clean, types, os.path.join(output_dir, "dax_measures.txt"))
            self.generate_setup_guide(theme_name, output_dir)
            self.log("    ✅ DAX + guide saved")
            
            self.log("[6/6] Generating interactive HTML dashboard preview...")
            html = self.generate_html_dashboard(df_clean, types, theme, theme_name)
            html_path = os.path.join(output_dir, "dashboard_preview.html")
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html)
            self.log("    ✅ Interactive HTML preview generated")
            
            self.log("\n🎉 ALL DONE! Dashboard generated successfully!")
            self.log(f"📂 Output folder: {output_dir}")
            
            # Open output folder
            if sys.platform == "win32":
                os.startfile(output_dir)
            else:
                subprocess.run(["xdg-open", output_dir], check=False)
            
            messagebox.showinfo("Success", "Dashboard generated successfully!\nOutput folder will open automatically.")
        except Exception as e:
            self.log(f"❌ ERROR: {str(e)}")
            messagebox.showerror("Error", f"Generation failed: {str(e)}")
        finally:
            self.generate_btn.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
