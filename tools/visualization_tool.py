# tools/visualization_tool.py
from langchain.tools import BaseTool
import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO

class VisualizationTool(BaseTool):
    name: str = "data_visualization"
    description: str = "Visualize analyzed tabular data."

    def _run(self, data_str: str, plot_type: str = "bar", title: str = "Analysis") -> str:
        df = pd.read_csv(StringIO(data_str), sep=r"\s+")

        plt.style.use("ggplot")
        ax = df.plot(kind=plot_type, title=title)
        plt.tight_layout()
        plt.show()

        return "Visualization generated"

    async def _arun(self, *args, **kwargs):
        raise NotImplementedError
