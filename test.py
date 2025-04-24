import pandas as pd

a = pd.read_csv("data/car_price.csv")

a = a.rename(columns={"Gearing Type" : "gearing_type"})
a = a.rename(columns={"Body Color" : "body_color"})
print(a)