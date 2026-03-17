import marimo

__generated_with = "0.21.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    dropdown = mo.ui.dropdown(options=["Show me a cat!", "Show me a dog!"], label="What would you like to see?")
    dropdown
    return dropdown, mo


@app.cell
async def _(dropdown, mo):
    import micropip
    await micropip.install("plotly") # <== new package install, not included in marimo env OOB.

    import plotly.express as px
    from skimage import io

    loc = mo.notebook_location()

    img = 'cat.png' if dropdown.value == "Show me a cat!" else 'dog.png'
    img = io.imread('public/' + img)
    fig = px.imshow(img)
    fig
    return


if __name__ == "__main__":
    app.run()
