import pandas as pd
import os
import requests
import numpy as np
from datetime import datetime
from sklearn.preprocessing import StandardScaler, OneHotEncoder

# Check for ../Data directory presence
if not os.path.exists("../Data"):
    os.mkdir("../Data")

# Download data if it is unavailable.
if "nba2k-full.csv" not in os.listdir("../Data"):
    print("Train dataset loading.")
    url = "https://www.dropbox.com/s/wmgqf23ugn9sr3b/nba2k-full.csv?dl=1"
    r = requests.get(url, allow_redirects=True)
    open("../Data/nba2k-full.csv", "wb").write(r.content)
    print("Loaded.")

data_path = "../Data/nba2k-full.csv"


def clean_data(path: str):
    df = pd.read_csv(path, sep=",", )
    df.b_day = df.b_day.apply(lambda x: datetime.strptime(x, '%m/%d/%y'))
    df.draft_year = df.draft_year.apply(lambda x: datetime.strptime(str(x), '%Y'))
    df.team.fillna('No Team', inplace=True)
    df.height = df.height.apply(lambda x: x.split(' / ')[1]).astype('float')
    df.weight = df.weight.apply(lambda x: x.split(' / ')[1][:-4]).astype('float')
    df.salary = df.salary.apply(lambda x: x[1:]).astype('float')
    df.country = ['USA' if c == 'USA' else 'Not-USA' for c in df.country]
    df.draft_round = ['0' if d == 'Undrafted' else d for d in df.draft_round]
    return df


def feature_data(df):
    df.version = [pd.to_datetime(2020, format='%Y') if x == 'NBA2k20' else pd.to_datetime(2021, format='%Y') for x in
                  df.version]
    df['age'] = df['version'] - df['b_day']
    df['age'] = df.apply(lambda x: int(np.ceil(x.age / np.timedelta64(1, 'Y'))), axis=1)
    df['experience'] = df['version'] - df['draft_year']
    df['experience'] = df.apply(lambda x: int(round(x.experience / np.timedelta64(1, 'Y'))), axis=1)
    df = df.assign(bmi=lambda x: (x['weight'] / (x['height'] ** 2)))
    df.drop(['version', 'b_day', 'draft_year', 'weight', 'height'], inplace=True, axis=1)
    for el in ['full_name', 'rating', 'jersey', 'team', 'position', 'country', 'draft_round', 'draft_peak', 'college']:
        if df[el].nunique() >= 50:
            df = df.drop(columns=el)
    return df


def multicol_data(df, target='salary'):
    corr = df.select_dtypes('number').drop(columns=target).corr()
    correlated_features = []
    for i in range(corr.shape[0]):
        for j in range(i):
            if abs(corr.iloc[i, j]) > 0.5:
                correlated_features.append([corr.columns[i], corr.index[j]])

    for feature1, feature2 in correlated_features:
        if df[[feature1, target]].corr().iloc[1, 0] > df[[feature2, target]].corr().iloc[1, 0]:
            df.drop(columns=feature2, inplace=True)
        else:
            df.drop(columns=feature1, inplace=True)

    return df


def transform_data(df, target='salary'):
    num_feat_df = df.select_dtypes('number').drop(columns=target)
    cat_feat_df = df.select_dtypes('object')
    scaler = StandardScaler()
    encoder = OneHotEncoder().fit(cat_feat_df)
    col_names = encoder.categories_
    col_names_flat = [x for sublist in col_names for x in sublist]
    scaled_numerical = pd.DataFrame(scaler.fit_transform(num_feat_df), columns=num_feat_df.columns)
    encoded_nominal = encoder.transform(cat_feat_df)
    encoded_df = pd.DataFrame.sparse.from_spmatrix(encoded_nominal, columns=col_names_flat)
    X = pd.concat([scaled_numerical, encoded_df], axis=1)
    return X, df[target]


data_frame = clean_data(data_path)
data_frame = feature_data(data_frame)
data_frame = multicol_data(data_frame)
X, y = transform_data(data_frame)
answer = {
    'shape': [X.shape, y.shape],
    'features': list(X.columns),
    }
print(answer)
