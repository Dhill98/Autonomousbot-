# ml_navigation.py

from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
# this data is to train the ML algorithm
training_data = [
    [5],
    [10],
    [15],
    [18],
    [25],
    [30],
    [45],
    [60],
    [80]
]

training_labels = [
    "STOP",
    "STOP",
    "STOP",
    "STOP",
    "CAUTION",
    "CAUTION",
    "PASS",
    "PASS",
    "PASS"
]

model = DecisionTreeClassifier(random_state=42)

model.fit(training_data, training_labels)

test_distances =[
    [35],
    [100],
    [2],
    [12],
    [67]
]
test_predictions = model.predict(test_distances)

for distance, prediction in zip(test_distances, test_predictions):
    print(f"ML  TEST Prediction: {test_predictions} | Distance: {distance[0]} cm ")

# not used during training  
data =[
    [8],
    [17],
    [38],
    [50],
    [75]
]
actual_predict = model.predict(data)

actual_labels = ["STOP","STOP","CAUTION","PASS","PASS"]
for distance, prediction in zip(data, actual_predict):
    accuracy=accuracy_score(actual_labels, actual_predict)
    print(f"ML REAL Prediction: {actual_predict} | Distance: {distance[0]} cm ")