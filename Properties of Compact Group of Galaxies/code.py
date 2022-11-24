import os
import requests
import pandas as pd
from scipy.stats import shapiro, fligner, f_oneway, ks_2samp, pearsonr
import matplotlib.pyplot as plt
from astropy.cosmology import FlatLambdaCDM
from astropy import units as u
from astropy.coordinates import SkyCoord
from itertools import combinations

pd.options.mode.chained_assignment = None  # default='warn'

filenames = ["groups.tsv", "galaxies_morphology.tsv", "isolated_galaxies.tsv", "galaxies_coordinates.tsv"]
url = "https://stepik.org/media/attachments/lesson/665342/"


def data_loading():
    # Create data folder
    if not os.path.exists("data"):
        os.mkdir("data")

    # Retrieve files if not there
    for f in filenames:
        if f not in os.listdir("data"):
            res = requests.get(url + f)
            with open("data/" + f, "wb") as file:
                file.write(res.content)


def groups_preprocess():
    # Read TSV
    df = pd.read_csv("data/groups.tsv", sep="\t")
    df.dropna(axis=0, inplace=True)
    mean_IGL = df.groupby('features').agg({'mean_mu': 'mean'})
    df['ADD'] = pd.Series(dtype='int')
    df.reset_index(drop=True, inplace=True)
    # print(mean_IGL.mean_mu[1], mean_IGL.mean_mu[0], sep=' ')
    return df


def statistics(df):
    # Stage 2/5
    with_features = df.loc[df['features'] == 1, 'mean_mu']
    without_features = df.loc[df['features'] == 0, 'mean_mu']
    p_sw1 = shapiro(with_features)[1]
    p_sw0 = shapiro(without_features)[1]
    p_fk = fligner(with_features, without_features)[1]
    p_a = f_oneway(with_features, without_features)[1]
    print(p_sw1, p_sw0, p_fk, p_a)


def galaxy_analysis():
    # Stage 3/5
    df_gm = pd.read_csv("data/galaxies_morphology.tsv", sep="\t")
    df_ig = pd.read_csv("data/isolated_galaxies.tsv", sep="\t")
    plt.hist([df_ig['n'], df_gm['n']], label=["isolated galaxies", "groups galaxies"], stacked=True)
    plt.xlabel("n")
    plt.ylabel("Count")
    plt.legend()
    plt.show()
    fr_of_gm = len(df_gm.loc[df_gm['n'] > 2, 'n']) / len(df_gm['n'])
    fr_of_ig = len(df_ig.loc[df_ig['n'] > 2, 'n']) / len(df_ig['n'])
    p_ks2 = ks_2samp(df_gm['n'], df_ig['n'])[1]
    print(fr_of_gm, fr_of_ig, p_ks2)


def sersic():
    df = groups_preprocess()
    df_gm = pd.read_csv("data/galaxies_morphology.tsv", sep="\t")
    new_df_gm = df_gm.groupby('Group').agg({'n': 'mean', 'T': 'mean'})
    df = new_df_gm.merge(df, on='Group')
    df.rename(columns={'n': 'mean_n', 'T': 'mean_T'}, inplace=True)
    plt.scatter(df['mean_n'], df['mean_mu'])
    plt.xlabel('<n>')
    plt.ylabel('mi_{IGL,r}(mag~arcsec^{-2}')
    plt.show()
    plt.scatter(df['mean_T'], df['mean_mu'])
    plt.xlabel('<T>')
    plt.ylabel('mi_{IGL,r}(mag~arcsec^{-2}')
    plt.show()
    tests = [shapiro(x)[1] for x in [df['mean_mu'], df['mean_n'], df['mean_T']]]
    tests.append(pearsonr(df['mean_mu'], df['mean_n'])[1])
    tests.append(pearsonr(df['mean_mu'], df['mean_T'])[1])
    print(*tests)


def coordinates():
    my_cosmo = FlatLambdaCDM(H0=67.74, Om0=0.3089)
    df_gc = pd.read_csv("data/galaxies_coordinates.tsv", sep="\t")
    df = groups_preprocess()
    for i in range(len(df)):
        df['ADD'][i] = my_cosmo.angular_diameter_distance(df['z'][i]).to(u.kpc).value
    df_RA = df_gc.groupby('Group')['RA'].apply(lambda x: list(combinations(x.values, 2))).apply(
        pd.Series).stack().reset_index(level=0, name='ParamsRA')
    df_dec = df_gc.groupby('Group')['DEC'].apply(lambda x: list(combinations(x.values, 2))).apply(
        pd.Series).stack().reset_index(level=0, name='ParamsDec')
    df_RA = pd.concat([df_RA['Group'], df_RA['ParamsRA'].apply(pd.Series)], 1).set_axis(['Group', 'RA1', 'RA2'], 1,
                                                                                        inplace=False)
    df_dec = pd.concat([df_dec['Group'], df_dec['ParamsDec'].apply(pd.Series)], 1).set_axis(['Group', 'Dec1', 'Dec2'],
                                                                                            1, inplace=False)

    def SC(x, y): return SkyCoord(ra=x * u.degree, dec=y * u.degree, frame="fk5")
    df_data = pd.merge(df_RA, df_dec)
    df_data['Angular Distance'] = SC(df_data['RA1'], df_data['Dec1']).separation(
        SC(df_data['RA2'], df_data['Dec2'])).to(u.rad)
    angular_medians = df_data.groupby('Group').agg({'Angular Distance': 'median'})
    df_final = pd.merge(df, angular_medians, on='Group')
    df_final['Distance'] = df_final['ADD'] * df_final['Angular Distance']
    plt.scatter(df_final['Distance'], df_final['mean_mu'])
    plt.xlabel('<R (kpc)>', size=16)
    plt.ylabel(r'$\mu_{IGL, r}$ (mag~arcsec$^{-2}$)', size=16)
    plt.gca().invert_yaxis()
    plt.show()
    tests = [df_final.loc[df_final['Group'] == 'HCG 2', 'Distance'][0], shapiro(df_final['Distance'])[1],
             shapiro(df_final['mean_mu'])[1],
             pearsonr(df_final['mean_mu'], df_final['Distance'])[1]]
    print(*tests)


def median_separ(df, r):
    df = df[df.Group == r].reset_index()
    n = df.shape[0]
    s = []
    for i in range(n):
        p1 = SkyCoord(ra=df.loc[i].RA * u.degree, dec=df.loc[i].DEC * u.degree, frame="fk5")
        for j in range(i + 1, n):
            p2 = SkyCoord(ra=df.loc[j].RA * u.degree, dec=df.loc[j].DEC * u.degree, frame="fk5")
            r = p1.separation(p2).radian
            s.append(r)
    ad = pd.Series(s)
    return ad.median()


def AngularDistance(cosmo, row):
    return cosmo.angular_diameter_distance(row['z']).to(u.kpc).value * row['Rm']


def coordinates_2nd_version():
    df_gc = pd.read_csv("data/galaxies_coordinates.tsv", sep="\t")
    df = groups_preprocess()
    my_cosmo = FlatLambdaCDM(H0=67.74, Om0=0.3089)
    df['Rm'] = df.apply(lambda row: median_separ(df_gc, row['Group']), axis=1)
    df['Distance'] = df.apply(lambda row: AngularDistance(my_cosmo, row), axis=1)

    plt.scatter(df.Distance, df.mean_mu)
    plt.gca().invert_yaxis()
    plt.xlabel('<R (kpc)>', size=16)
    plt.ylabel(r'$\mu_{IGL, r}$ (mag~arcsec$^{-2}$)', size=16)
    plt.gca().invert_yaxis()
    plt.show()
    tests = [df[df.Group == 'HCG 2']['Distance'][0], shapiro(df['Distance'])[1],
             shapiro(df['mean_mu'])[1],
             pearsonr(df['mean_mu'], df['Distance'])[1]]
    print(*tests)


statistics(groups_preprocess())
galaxy_analysis()
sersic()
coordinates_2nd_version()
