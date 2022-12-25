import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, calinski_harabasz_score
import matplotlib.pyplot as plt


df = pd.read_csv("C:/Users/zerox/Downloads/data1.csv")

df.info()
df = df.dropna() 


train = df.iloc[:int(len(df)*0.8)]  
test = df.iloc[int(len(df)*0.8):] 


scaler = StandardScaler()
train_scaled = scaler.fit_transform(train[['temp', 'humid', 'soil', 'soil_temp', 'salt']])
test_scaled = scaler.transform(test[['temp', 'humid', 'soil', 'soil_temp', 'salt']])


kmeans = KMeans(n_clusters=2)
kmeans.fit(train_scaled)


silhouette_score = silhouette_score(test_scaled, kmeans.predict(test_scaled))
calinski_harabasz_score = calinski_harabasz_score(test_scaled, kmeans.predict(test_scaled))

print("Silhouette score:", silhouette_score)
print("Calinski-Harabasz score:", calinski_harabasz_score)


predictions = kmeans.predict(test_scaled)

plt.scatter(test['soil'], test['temp'], c=predictions, cmap='viridis')
plt.xlabel('Soil Moisture')
plt.ylabel('temp')
plt.title('K-means Clustering')
plt.show()





