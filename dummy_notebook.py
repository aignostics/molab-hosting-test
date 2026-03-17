import marimo

__generated_with = "0.21.0"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import marimo as mo

    dropdown = mo.ui.dropdown(options=["Show me a cat!", "Show me a dog!"], label="What would you like to see?")
    dropdown
    return (dropdown,)


@app.cell(hide_code=True)
async def _(dropdown):
    import micropip
    await micropip.install("plotly[express]") # <== new package install, not included in marimo env OOB.
    import plotly.express as px

    from PIL import Image
    from PIL import ImageFile

    ImageFile.LOAD_TRUNCATED_IMAGES=True

    img = 'cat.png' if dropdown.value == "Show me a cat!" else 'dog.png'

    img = Image.open('public/cat.png')
    fig = px.imshow(img)
    fig
    return


if __name__ == "__main__":
    app.run()
