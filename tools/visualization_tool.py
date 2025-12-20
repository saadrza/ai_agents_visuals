# tools/visualization_tool.py
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO
from typing import Optional

# [Integration] Import your custom style function
from styles.company_style import apply_company_style 

class VisualizationInput(BaseModel):
    data_str: str = Field(description="CSV formatted string of data to plot")
    plot_type: str = Field(description="Type of plot: 'bar', 'line', 'scatter', 'hist', 'box'")
    title: str = Field(description="Title of the chart")
    x_column: Optional[str] = Field(description="Column name for X axis")
    y_column: Optional[str] = Field(description="Column name for Y axis")
    save_path: str = Field(description="File path to save the image (e.g., 'plot.png')")

class VisualizationTool(BaseTool):
    name: str = "data_visualization"
    description: str = """
    Visualize data. Input MUST be a CSV string. 
    Supported plots: bar, line, scatter, hist.
    ALWAYS provide a 'save_path' ending in .png.
    """
    args_schema: type[BaseModel] = VisualizationInput

    def _run(self, data_str: str, plot_type: str = "line", title: str = "Data Visualization",
             x_column: Optional[str] = None, y_column: Optional[str] = None, 
             save_path: Optional[str] = "output_plot.png", *args, **kwargs):
        
        # [Requirement] Apply the Company Style 
        apply_company_style()

        try:
            # Parse Data
            try: 
                df = pd.read_csv(StringIO(data_str), sep=",")
            except: 
                df = pd.read_csv(StringIO(data_str), sep=None, engine='python')

            if df.empty: return "Error: Data is empty"
            
            # Create Plot
            fig, ax = plt.subplots()
            
            # Logic for different plot types
            if plot_type == "scatter" and x_column and y_column:
                ax.scatter(df[x_column], df[y_column])
                ax.set_xlabel(x_column); ax.set_ylabel(y_column)
            elif x_column and y_column:
                df.plot(x=x_column, y=y_column, kind=plot_type, ax=ax)
            else:
                numeric_cols = df.select_dtypes(include=['number']).columns
                df[numeric_cols].plot(kind=plot_type, ax=ax)
            
            ax.set_title(title)
            plt.tight_layout()
            
            # Save
            plt.savefig(save_path, dpi=150)
            plt.close()
            return f"Success: Chart saved to {save_path}"

        except Exception as e:
            return f"Visualization Error: {str(e)}"