import marimo

__generated_with = "0.21.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    dropdown = mo.ui.dropdown(options=["Lines!", "Bars!"], label="What would you like to see?")
    dropdown
    return (dropdown,)


@app.cell
async def _(dropdown):
    import micropip
    await micropip.install("plotly[express]") # <== new package install, not included in marimo env OOB.

    import plotly.express as px
    import pandas as pd

    df = pd.read_csv('public/dummy_data.csv')
    if dropdown.value == "Lines!":
        fig = px.line(x = df.x, y = df.y)
    else:
        fig = px.bar(x=df.x, y=df.y)
    fig
    return


if __name__ == "__main__":
    app.run()
