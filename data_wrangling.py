import pandas as pd
import numpy as np


if __name__ == '__main__':
    df = pd.read_csv("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/dataset_part_1.csv")
    print(df.head(10))

    print('Percent null:')
    print(df.isnull().sum() / len(df) * 100)

    print('\nDatatypes')
    print(df.dtypes)

    # Task 1: Calculate the number of launches at each site
    print('\n\nTask 1:')
    print(df['LaunchSite'].value_counts())

    # Task 2: Calculate the number and occurence of each type of orbit
    print('\n\nTask 2:')
    print(df['Orbit'].value_counts())

    # Task 3: Calculate the number and occurence of mission outcome of the orbits
    print('\n\nTask 3:')
    landing_outcomes = df['Outcome'].value_counts()
    print(landing_outcomes)

    bad_outcomes = set(landing_outcomes.keys()[[1,3,5,6,7]])
    print('\n Bad Outcomes')
    print(bad_outcomes)

    # Task 4: Create a landing outcome label from Outcome column
    print('\n\nTask 4:')
    landing_class = [0 if outcome in bad_outcomes else 1 for outcome in df['Outcome']]

    df['Class'] = landing_class
    print(df[['Class']].head(8))

    print(df.head(5))

    print('Success Rate:', df["Class"].mean())