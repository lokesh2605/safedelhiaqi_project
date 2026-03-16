import pandas as pd

df = pd.read_csv("Delhi_AQI_Main_Dataset.csv")

df = df.select_dtypes(include=['number'])

print(df.columns)