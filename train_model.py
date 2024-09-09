import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from joblib import dump

# splitting data for train and test pieces
df = pd.read_csv('data/preproc_matches.csv')
X, y = df.drop('winner', axis=1), df['winner']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=52)
X_train.shape, X_test.shape

# scaling the data
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
dump(scaler, 'data/joblib/scaler.joblib')

# fitting the logistic regression
logreg = LogisticRegression()
logreg.fit(X_train_scaled, y_train)
dump(logreg, 'data/joblib/logistic_regression_model.joblib')
