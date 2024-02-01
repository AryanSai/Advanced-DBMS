import pandas as pd

df = pd.read_csv('friends.csv')

result = df.query('country == "USA" and name == "John Doe"')

print(result)
