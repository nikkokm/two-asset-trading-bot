############################
#     Functions to
# train the model(s) and
#  compute Kelly weight
############################

import pandas as pd
from sklearn.model_selection import TimeSeriesSplit
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import numpy as np


def compute_label(df):
    #df['buy_momentum'] = np.where(df['VTV_trailing_return'] < df['PDP_trailing_return'], 1, 0)
    df['buy_momentum'] = np.where(df['VTV_trailing_return'] < df['MTUM_trailing_return'], 1, 0)
    return df


def train_model_in_sample(df): #  take the df with ETF prices, returns, features and everything else
    feature_columns = [8, 9, 10, 11, 12, 13, 14]
    label_column = [15]
    X = df[df.columns[feature_columns]].values
    y = df[df.columns[label_column]].values.ravel()
    tscv = TimeSeriesSplit()
    model = LogisticRegression(max_iter=1000)
    df['predicted_label'] = np.nan
    logreg_result = np.array([])
    logreg_proba = np.array([])

    initial_y_test_index = 0

    for train_index, test_index in tscv.split(X):

        if initial_y_test_index == 0:
            initial_y_test_index = test_index[0]

        X_train, X_test = X[train_index], X[test_index]
        y_train, y_test = y[train_index], y[test_index]
        model.fit(X_train, y_train)
        prediction = model.predict(X_test)
        p = model.predict_proba(X_test)[:, 1]
        logreg_proba = np.append(logreg_proba, p)
        logreg_result = np.append(logreg_result, prediction)

    logreg_result = logreg_result.astype(int)

    model_result = pd.DataFrame({
        'Model Probability': logreg_proba,
        'Model Result': logreg_result
    }, index=df.index[initial_y_test_index:])

    print('Model Accuracy Score: ' + str(accuracy_score(y[initial_y_test_index:], logreg_result)))

    return model_result


def get_trade(df, data):  # df: database.csv, data: output from get_features()
    feature_columns = [8, 9, 10, 11, 12, 13, 14]
    label_column = [15]
    X = df[df.columns[feature_columns]].values
    y = df[df.columns[label_column]].values.ravel()
    model = LogisticRegression(max_iter=1000)
    model.fit(X, y)  # fit model on all the
    data = data.reshape(1,-1)
    prediction = model.predict(data)
    prediction = prediction[0]
    weight = model.predict_proba(data)[:, 1]
    weight = weight[0]

    # re-scale the probability to a portfolio weight. Not elegant, but whatever
    if weight >= 0.5:
        weight = weight - 0.5

    elif weight < 0.5:
        if weight == 0.4:
            weight = 0.1
        elif weight == 0.3:
            weight = 0.2
        elif weight == 0.2:
            weight = 0.3
        elif weight < 0.3:
            weight = 0.4
#        weight = weight * (-1)

    return prediction, weight
