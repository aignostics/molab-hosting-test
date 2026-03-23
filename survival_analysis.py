import marimo

__generated_with = "0.21.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    await micropip.install("huggingface_hub") # <== new package install, not included in marimo env OOB.
    await micropip.install("lifelines") # <== new package install, not included in marimo env OOB.
    await micropip.install("scipy") # <== new package install, not included in marimo env OOB.
    await micropip.install("plotly") # <== new package install, not included in marimo env OOB.
    return 

@app.cell(hide_code=True)
def _():
    import pandas as pd
    from huggingface_hub import hf_hub_download

    # # download the OpenTME bladder dataset
    # REPO_ID = "Aignostics/OpenTME"
    # FILENAME = "data/bladder/tme_features.csv"

    REPO_ID = "MaaikeG/test_dataset"
    FILENAME = "readouts.csv"

    path = hf_hub_download(repo_id=REPO_ID, filename=FILENAME, repo_type="dataset")
    df_tme = pd.read_csv(path, skiprows=1)

    # load survival data
    origin = mo.notebook_location() / "public"
    df_survival = pd.read_csv(origin / "metadata.csv")

    # store relevant columns (dropping IMAGE_RESOLUTION etc)
    tme_feat = df_tme.columns[6:]
    return df_survival, df_tme, mo, pd, tme_feat


@app.cell(hide_code=True)
def _(df_survival, mo):
    mo.vstack([
        mo.md(f"""# Survival analysis 

    This notebook shows how one can find features in OpenTME that correlate with survival, and how to plot Kaplan-Meyer curves stratified by such a feature.


    For the purpose of this example we need survival data. This is not included in OpenTME, but may be extracted from TCGA directly.
    We extracted survival data for a small subset of TCGA slides and add this to the dataframe. 

    The survival data can be found in columns `{list(df_survival.columns[3:])}`
    """),
        df_survival.head(),
    ])
    return


@app.cell
def _(df_survival, df_tme, mo):
    df = df_tme.merge(df_survival, left_on="FILE_NAME_TCGA", right_on="Slide name", how="inner")

    assert len(df) == len(df_tme)

    # encode survival status as binary column
    df["event"] = df["Overall Survival Status"]
    df["time"] = df["Overall Survival (Months)"]

    mo.vstack([
        mo.md(
            "We join the survival data with our OpenTME features, and group by 'event' to see how many slides we have for the survival categories."
        ),
        mo.md(df.groupby("event").SLIDE_UUID.count().to_markdown()),
    ])
    return (df,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Get most correlated feature

    We use the column `Overall Survival Status` and find the feature that correlates most strongly with it.
    """)
    return


@app.cell
def _(df, mo, pd, tme_feat):
    import numpy as np
    from scipy.stats import pointbiserialr

    correlations = np.zeros((len(tme_feat),))

    for i, col in enumerate(tme_feat):
        _feat = df[col]
        filter = ~_feat.isna()

        # skip features that N/A for many cases, and non-numeric features
        if filter.sum() < 100 or not pd.api.types.is_numeric_dtype(_feat):
            continue

        # compute correlation and store
        correlation, _ = pointbiserialr(x=df.event[filter].astype(bool), y=_feat[filter].astype(float))
        correlations[i] = correlation

    # get most correlated features
    feat = tme_feat[np.abs(correlations).argmax()]
    mo.md(f"""Most correlated feature with survival: `{feat}`""")
    return feat, np


@app.cell
def _(df, feat, mo):
    import plotly.express as px

    fig = px.box(df, x="Overall Survival Status", y=feat)

    mo.vstack([mo.md("""## Distribution of most correlated feature vs. survival status"""), mo.ui.plotly(fig)])
    return


@app.cell(hide_code=True)
def _(df, feat, mo):
    _text = mo.md(f"""## Kaplan-Meyer
    Now that we've found the feature that correlates most strongly with survival, let's try to see how it affects Kaplan-Meyer analysis. 

    We split the patients into two groups, having a value for `{feat}` either above of below the value of the slider. We then plot the Kaplan-Meyer curves for both groups.
    """)
    slider = mo.ui.slider(
        start=df[feat].min(),
        stop=df[feat].max(),
        label=f"Select value of `{feat}` to split patients by.",
        include_input=True,
        step=1e-5,
        full_width=True,
        value=df[feat].median(),
    )
    mo.vstack([_text, slider])
    return (slider,)


@app.cell
def _(df, feat, np, slider):
    from lifelines import KaplanMeierFitter

    # from aignostics_opentmeexplorer.elements.plotting import kaplan_meyer

    def fit_kaplan_meyer(df):
        kmf = KaplanMeierFitter()
        kmf.fit(durations=df.time, event_observed=df.event, label=df.name)
        return kmf

    def fit_kaplan_meyer_groupwise(df):
        kmfs = df.groupby("group").apply(fit_kaplan_meyer)
        # kmp = kaplan_meyer.KaplanMeyerPlotter(show_censors=True)
        # return kmp.render(kmfs)
        return kmfs

    def split_by_value(df, col: str, value: float):
        return np.where(df[col] > value, f"{col} > {value:.2e}", f"{col} < {value:.2e}")

    # split patients into two groups, having feature above or below the value given by the slider
    df["group"] = split_by_value(df, feat, slider.value)

    # fit Kaplan-Meyer estimator and plot for each group.
    kmfs = fit_kaplan_meyer_groupwise(df.dropna(subset=["group", "time", "event"]))
    [kmf.plot() for kmf in kmfs]


    # # Display results
    # _title = f"Overall survival for patients split by `{feat}` larger or smaller than {slider.value:.2e}. \n"
    # mo.vstack([mo.md(_title), mo.ui.plotly(_fig)])
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
