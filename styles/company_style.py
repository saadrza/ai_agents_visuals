# styles/company_style.py
import matplotlib.pyplot as plt

def apply_company_style():
    # Start with a clean base
    plt.style.use("ggplot")
    
    # Add custom corporate branding overrides
    plt.rcParams.update({
        "figure.figsize": (10, 6),
        "axes.titlesize": 14,
        "axes.labelsize": 12,
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica"], # Cleaner fonts
        # Custom color cycle (Blue, Orange, Green)
        "axes.prop_cycle": plt.cycler(color=['#0052CC', '#FF5500', '#36B37E']),
        "figure.facecolor": "white",
        "axes.facecolor": "#F4F5F7"
    })