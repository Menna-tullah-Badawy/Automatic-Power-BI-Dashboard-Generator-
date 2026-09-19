#!/usr/bin/env python3
import os

themes = {
    "fitpro_red": {
        "name": "FitPro Red Sports",
        "primary": "#C4122E",
        "light": "#EF4444",
        "dark": "#991B1B",
        "bg_main": "#111827",
        "bg_card": "#1F2937",
        "bg_sidebar": "#0F172A",
        "text_main": "#F3F4F6",
        "text_muted": "#9CA3AF"
    },
    "wallet_teal": {
        "name": "Wallet Teal Soft",
        "primary": "#10B981",
        "light": "#34D399",
        "dark": "#059669",
        "bg_main": "#F0FDF4",
        "bg_card": "#FFFFFF",
        "bg_sidebar": "#ECFDF5",
        "text_main": "#064E3B",
        "text_muted": "#6B7280"
    },
    "dark_purple": {
        "name": "Dark Purple Analytics",
        "primary": "#8B5CF6",
        "light": "#A78BFA",
        "dark": "#6D28D9",
        "bg_main": "#0F172A",
        "bg_card": "#1E293B",
        "bg_sidebar": "#0B1120",
        "text_main": "#F8FAFC",
        "text_muted": "#94A3B8"
    },
    "trading_neon": {
        "name": "Trading Neon Green",
        "primary": "#00FF88",
        "light": "#10B981",
        "dark": "#065F46",
        "bg_main": "#030712",
        "bg_card": "#111827",
        "bg_sidebar": "#020617",
        "text_main": "#ECFDF5",
        "text_muted": "#6EE7B7"
    },
    "rexora_light": {
        "name": "Rexora Light Green Modern",
        "primary": "#92E3A9",
        "light": "#BBF7D0",
        "dark": "#166534",
        "bg_main": "#F8FAFC",
        "bg_card": "#FFFFFF",
        "bg_sidebar": "#F0FDF4",
        "text_main": "#1E293B",
        "text_muted": "#64748B"
    },
    "control_blue": {
        "name": "Control Dark Blue",
        "primary": "#3B82F6",
        "light": "#60A5FA",
        "dark": "#1D4ED8",
        "bg_main": "#0F172A",
        "bg_card": "#1E293B",
        "bg_sidebar": "#0B1120",
        "text_main": "#F8FAFC",
        "text_muted": "#94A3B8"
    }
}

# Read the gold template
with open("luxury_gold_dashboard.html", "r", encoding="utf-8") as f:
    gold_template = f.read()

for theme_key, t in themes.items():
    output = gold_template
    # Replace gold colors with theme colors
    replacements = [
        ("#E8B860", t["primary"]),
        ("#F7D794", t["light"]),
        ("#B88A2C", t["dark"]),
        ("#262320", t["bg_main"]),
        ("#2E2B28", t["bg_card"]),
        ("#221F1D", t["bg_sidebar"]),
        ("#F0D9A9", t["text_main"]),
        ("#C2B59C", t["text_muted"]),
        ("Luxury Gold Dashboard - Exact Match", t["name"])
    ]
    for old, new in replacements:
        output = output.replace(old, new)
    
    filename = f"{theme_key}_dashboard.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(output)
    print(f"✅ Generated {t['name']}: {filename}")

print("\n🎉 All 7 theme dashboards generated successfully!")
