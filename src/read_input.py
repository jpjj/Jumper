from copy import deepcopy
import pandas as pd


def float_to_iso(time: float) -> str:
    if time[0:2] == "0,":
        # 0,375 should become 09:00:00
        time = float(time.replace(",", ".")) * 24 * 3600
        return (
            str(int(time // 3600)).zfill(2)
            + ":"
            + str(int((time % 3600) // 60)).zfill(2)
            + ":"
            + str(int(time % 60)).zfill(2)
        )
    else:
        # 9:00 should become 09:00:00
        return time


def read_input(file):
    for sep in [",", ";"]:
        new_file = deepcopy(file)
        try:
            data = pd.read_csv(
                new_file,
                sep=sep,
                index_col=0,
                converters={
                    "Open (HH:MM:SS)": float_to_iso,
                    "Close (HH:MM:SS)": float_to_iso,
                },
            )
            print(sep)
            return data
        except Exception as e:
            print(e)
