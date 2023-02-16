# About this folder 
This folder contain the model we developed during this project. You can use this model to predict if there's waster wastage or not(in other words it can tell you when to turn off the pump).

# How to use
### Step 1: Load the Model 

```python
import joblib
import 

model = joblib.load('my_model.joblib')
```

### Step 2: Prepare the data

```python
import pandas as pd
import numpy as np
# You can use one of the csv files in this folder
df = pd.read_csv('data.csv')
data = df[['temp', 'humid', 'soil', 'soil_temp', 'salt']]
data_array = data.to_numpy()
```

### Step 3: Make predictions 

```python
# Make a prediction
prediction = model.predict(data_array)

# Print the prediction
print(prediction)
```
  The result of the print operation is a an array of the predictions eaither 0 or 1. For some reason the model assigned 0 = There is water wastage and 1 = There is no water wastage.
# Prerequisites
- Python v3
- NumPy
- Pandas
- joblib
