import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import confusion_matrix

def plot_confusion_matrix(y, y_predict):
    """
    This function plots the confusion matrix.
    """

    cm = confusion_matrix(y, y_predict)
    ax = plt.subplot()
    sns.heatmap(cm, annot = True, ax = ax) #annot = True to annotate cells
    ax.set_xlabel('Predicted labels')
    ax.set_ylabel('True labels')
    ax.set_title('Confusion Matrix')
    ax.xaxis.set_ticklabels(['did not land', 'land'])
    ax.yaxis.set_ticklabels(['did not land', 'landed'])
    plt.show()

if __name__ == '__main__':
    data = pd.read_csv('https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/dataset_part_2.csv')
    X = pd.read_csv('https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/dataset_part_3.csv')
    Y = data['Class'].to_numpy()

    transform = preprocessing.StandardScaler()
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size = 0.2, random_state = 2)

    # L1 Lasso L2 Ridge
    log_parameters = {
        "C" : [0.01, 0.1, 1],
        'penalty' : ['l2'],
        'solver' : ['lbfgs']
    }

    logreg = LogisticRegression()
    logreg_cv = GridSearchCV(estimator = logreg, param_grid = log_parameters, cv = 10)
    logreg_cv.fit(X_train, Y_train)

    print("Logreg Best Parameters:", logreg_cv.best_params_)
    print("Logreg Score:", logreg_cv.best_score_)

    yhat = logreg_cv.predict(X_test)
    plot_confusion_matrix(Y_test, yhat)

    # KNN
    knn_parameters = {
        'n_neighbors': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'algorithm': ['auto', 'ball_tree', 'kd_tree', 'brute'],
        'p': [1,2]
    }

    knn_classifier = KNeighborsClassifier()
    knn_cv = GridSearchCV(estimator = knn_classifier, param_grid = knn_parameters, cv = 10)
    knn_cv.fit(X_train, Y_train)

    print("KNN Best Parameters:", knn_cv.best_params_)
    print("KNN Accuracy:", knn_cv.best_score_)

    yhat = knn_cv.predict(X_test)
    plot_confusion_matrix(Y_test, yhat)