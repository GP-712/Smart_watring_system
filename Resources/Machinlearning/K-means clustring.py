import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, calinski_harabasz_score
import matplotlib.pyplot as plt
from pandas.plotting import scatter_matrix



# load the dataet
df = pd.read_csv(".......data31.csv")

# drop any rows with empty or missing values 
df = df.dropna() 
df.info()

# split the data 80% for training and 20% for testing.
train = df.iloc[:int(len(df)*0.8)]  
test = df.iloc[int(len(df)*0.8):] 

# crreate a scaler object 
scaler = StandardScaler()

# scale the data 
train_scaled = scaler.fit_transform(train[['temp', 'humid', 'soil', 'soil_temp', 'salt']])
test_scaled = scaler.transform(test[['temp', 'humid', 'soil', 'soil_temp', 'salt']])

#training the model
kmeans = KMeans(n_clusters=2)
kmeans.fit(train_scaled)

#check the model performance 
silhouette_score = silhouette_score(test_scaled, kmeans.predict(test_scaled))
calinski_harabasz_score = calinski_harabasz_score(test_scaled, kmeans.predict(test_scaled))

print("Silhouette score:", silhouette_score)
print("Calinski-Harabasz score:", calinski_harabasz_score)

#scatter plot
predictions = kmeans.predict(test_scaled)
plt.scatter(test['soil'], test['salt'], c=predictions, cmap='viridis')
plt.xlabel('Soil Moisture')
plt.ylabel('salt')

plt.show()


#plot matrix
predictions = kmeans.predict(test_scaled)



scatter_matrix(test[['temp', 'humid', 'soil', 'soil_temp', 'salt']], c=predictions, figsize=(15, 15), diagonal='hist', cmap='viridis')


plt.show()









