import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt


data = pd.read_csv("........../data1.csv")


data = data.dropna() 


scaler = StandardScaler()
scaled_data = scaler.fit_transform(data[['temp', 'humid', 'soil', 'soil_temp', 'salt']])


kmeans = KMeans(n_clusters=2)
kmeans.fit(scaled_data)


data['cluster'] = kmeans.predict(scaled_data)

plt.scatter(data['soil'], data['humid'], c=data['cluster'])
plt.xlabel('Soil')
plt.ylabel('Humidity')
plt.show()
