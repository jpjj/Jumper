import datetime
from pathlib import Path
import pandas as pd

from src.solve import solve

path = Path(__file__).parent.parent.parent / "data" / "example.csv"
data = pd.read_csv(path, index_col=0)
parameters = {
    "start_time": datetime.time(6, 0),
    "end_time": datetime.time(20, 0),
}
solution, location_list = solve(data, parameters)
