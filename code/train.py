# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license.

from sklearn.metrics import mean_squared_error
from azureml.core.run import Run
import os
import numpy as np
from sklearn import __version__ as sklearnver
from packaging.version import Version
if Version(sklearnver) < Version("0.23.0"):
    from sklearn.externals import joblib
else:
    import joblib

import pandas as pd
from xgboost import XGBClassifier
from xgboost import DMatrix
import xgboost as xgb
from sklearn.model_selection import train_test_split, cross_val_score, cross_val_predict
from sklearn.metrics import make_scorer, precision_recall_curve, recall_score, precision_score, classification_report
from sklearn.preprocessing import LabelEncoder
from xgboost import plot_importance

df = pd.read_csv('../assets/augmented_credit_data.csv').dropna()
print(len(df))
os.makedirs('./outputs', exist_ok=True)

# encode string class values as integers
df.insert(5,'Age Group', pd.cut(df.Age,bins=[0,2,17,65,99], labels=['Toddler/baby','Child','Adult','Elderly']))
df.insert(5,'Credit Group', pd.cut(df['Credit amount'], bins=[0,1000,2500,5000,7500,20000], labels=['< 1000','1000-2500','2500-5000','5000-7500','>7500']))
df.insert(5,'Credit Duration', pd.cut(df['Duration'], bins=[0,10,20,30,40,50,100], labels=['< 10','10-20','20-30','30-40','40-50','50-100']))

label_encoder = LabelEncoder()
for label in ['Risk', 'Sex', 'Housing', 'Purpose', 'Saving accounts', 'Checking account', 'Age Group', 'Credit Group', 'Credit Duration']:
    df[label] = label_encoder.fit(df[label]).transform(df[label])

dtrain = DMatrix(X_train, label=y_train)
dtest = DMatrix(X_test, label=y_test)

param = {
    'max_depth': 5, 
    'eta': 0.9,  
    'silent': 1, 
    'num_class': 2,
    'objective': 'multi:softprob'}

# list of numbers from 0.0 to 1.0 with a 0.05 interval
alphas = np.arange(0.0, 1.0, 0.05)

for alpha in alphas:
    # Use XGBOOST
    bst = xgb.train(param, dtrain, 10)
    preds = bst.predict(dtest)

    #mse = mean_squared_error(preds, y_test)
    #run.log('alpha', alpha)
    #run.log('mse', mse)

    model_file_name = 'ridge_{0:.2f}.pkl'.format(alpha)
    # save model in the outputs folder so it automatically get uploaded
    with open(model_file_name, "wb") as file:
        joblib.dump(value=bst, filename=os.path.join('./outputs/',
                                                     model_file_name))

    #print('alpha is {0:.2f}, and mse is {1:0.2f}'.format(alpha, mse))