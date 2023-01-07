import pandas as pd

db = pd.read_csv('Resources/database.csv')
row = pd.Series({'name': 'louis', 'score': 50})
new_db = pd.concat([db, pd.DataFrame([row], columns=row.index)])
print(new_db.head())