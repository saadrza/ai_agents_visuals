# styles/company_style.py
import matplotlib.pyplot as plt

def apply_company_style():
    plt.style.use("ggplot")
    plt.rcParams.update({
        "figure.figsize": (10, 6),
        "axes.titlesize": 14,
        "axes.labelsize": 12
    })
