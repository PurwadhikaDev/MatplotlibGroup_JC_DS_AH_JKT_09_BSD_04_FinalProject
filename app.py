# from pycaret.regression import load_model, predict_model, interpret_model
from pycaret.regression import *
from PIL import Image
import streamlit as st
import pandas as pd
import numpy as np
import time

HOUSE_EMOJI_URL = "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/240/apple/285/house_1f3e0.png"

st.set_page_config(
    page_title="Residential Price Prediction", page_icon=HOUSE_EMOJI_URL,
)

def predict(model, df):
    predictions_data = predict_model(estimator=model, data=df)
    predicted_price = predictions_data["Label"][0]
    interval = 351834.78 # using 95% prediction intervals
    lower, upper = predicted_price - interval, predicted_price + interval
    return lower, predicted_price, upper

# app title and description
def main():
    st.markdown("<br>", unsafe_allow_html=True)
    st.title("Washington D.C. Residential Properties Price Prediction 🏠")
    st.write(
        """
    [![GitHub](https://img.shields.io/github/watchers/elvanselvano/purwadhika-final-project?style=social)](https://github.com/elvanselvano/purwadhika-final-project)
    [![Status](https://img.shields.io/badge/status-active-success.svg)](https://github.com/elvanselvano/purwadhika-final-project) 
    [![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/elvanselvano/purwadhika-final-project/blob/main/LICENSE)
    """
    )

    image = Image.open("./assets/wallpaper.jpg")
    st.image(image)

    st.markdown(
        "<h6 style='text-align: center; color: white;'><em>Image from wallpaperaccess.com</em></h6>",
        unsafe_allow_html=True,
    )
    st.markdown("")

    st.markdown(
        """
    This web app uses actual transaction data from 2010 to 2018 and machine learning models to predict the prices of housing in Washington, D.C., which is the capital of the United States. The transaction data contain attributes and transaction prices of residential property that respectively serve as independent variables and dependent variables for the machine learning models.
    """
    )

    st.info(
        "All data is available at [Open Data D.C.](https://opendata.dc.gov/). The residential and address point data is managed by the [Office of the Chief Technology Officer](https://octo.dc.gov/)."
    )

    # interior details
    st.sidebar.subheader("Interior Details")
    st.sidebar.write("")
    ROOMS = st.sidebar.slider(label="Room", min_value=1, max_value=6, value=3, step=1)
    BEDRM = st.sidebar.slider(label="Bedroom", min_value=1, max_value=6, value=3, step=1)
    BATHRM = st.sidebar.slider(
        label="Full Bathroom", min_value=0, max_value=6, value=2, step=1
    )
    HF_BATHRM = st.sidebar.slider(
        label="Half Bathroom", min_value=0, max_value=2, value=1, step=1
    )
    KITCHENS = st.sidebar.slider(
        label="Kitchens", min_value=0, max_value=4, value=1, step=1
    )
    HEAT = st.sidebar.radio(
        "Heating", ("Forced Air", "Hot Water Rad", "Warm Cool", "Ht Pump")
    )

    # additional features
    st.sidebar.write("---")
    st.sidebar.subheader("Additional Features")
    st.sidebar.write("")
    ac_check = st.sidebar.checkbox("AC", value=False)
    AC = 1 if ac_check else 0

    fireplaces_check = st.sidebar.checkbox("Fireplace", value=False)
    FIREPLACES = 1 if fireplaces_check else 0

    remodeled_check = st.sidebar.checkbox("Remodeled", value=False)
    RMDL = 1 if remodeled_check else 0

    # construction details
    st.sidebar.write("---")
    st.sidebar.subheader("Construction Details")
    st.sidebar.write("")
    STYLE = st.sidebar.selectbox(
        "Style", ("1 Story", "1.5 Story Fin", "2 Story", "2.5 Story Fin", "3 Story")
    )
    INTWALL = st.sidebar.selectbox(
        "Interior Wall", ("Hardwood", "Hardwood/Carp", "Wood Floor", "Carpet")
    )
    EXTWALL = st.sidebar.selectbox(
        "Exterior Wall",
        (
            "Common Brick",
            "Brick/Siding",
            "Vinyl Siding",
            "Wood Siding",
            "Stucco",
            "Face Brick",
        ),
    )
    ROOF = st.sidebar.selectbox(
        "Roof", ("Built Up", "Metal- Sms", "Comp Shingle", "Slate", "Neopren", "Shake")
    )
    STRUCT = st.sidebar.selectbox(
        "Structure", ("Row Inside", "Single", "Semi-Detached", "Row End", "Multi")
    )
    st.sidebar.write("---")
    st.sidebar.subheader("Property Details")
    st.sidebar.write("")
    AYB = st.sidebar.number_input(
        label="AYB", min_value=1914, max_value=2018, value=1935, step=1
    )
    EYB = st.sidebar.number_input(
        label="EYB", min_value=1964, max_value=2018, value=1972, step=1
    )
    GBA = st.sidebar.number_input(
        label="Gross Building Area", min_value=1204, max_value=1800, value=1577, step=1
    )
    LANDAREA = st.sidebar.number_input(
        label="Land Area", min_value=1425, max_value=3460, value=2736, step=1
    )
    CNDTN = st.sidebar.slider(label="Condition", min_value=1, max_value=6, value=4, step=1)
    SALENUM = st.sidebar.slider(
        label="Total sold since May 2014", min_value=1, max_value=5, value=1, step=1
    )
    SALEYEAR = st.sidebar.number_input(
        label="Sale Year", min_value=2010, max_value=2018, value=2017, step=1
    )
    GRADE = st.sidebar.selectbox(
        "Grade",
        (
            "Average",
            "Above Average",
            "Good Quality",
            "Very Good",
            "Superior",
            "Excellent",
            "Exceptional-A",
        ),
    )

    WARD = st.sidebar.selectbox(
        "Ward",
        ("Ward 1", "Ward 2", "Ward 3", "Ward 4", "Ward 5", "Ward 6", "Ward 7", "Ward 8"),
    )

    st.subheader("Property Information")
    st.markdown(
        "👈  In the sidebar, there are 23 features that you can adjust. The features are shown\
        in the table below. After you have adjusted the \
        features, click on the **Predict** button to see the prediction of the machine\
            learning model."
    )

    # mapping features with user's input
    features = {
        "ROOM": ROOMS,
        "BEDRM": BEDRM,
        "BATHRM": BATHRM,
        "HF_BATHRM": HF_BATHRM,
        "KITCHENS": KITCHENS,
        "HEAT": HEAT,
        "AC": AC,  
        "FIREPLACES": FIREPLACES,
        "RMDL": RMDL,
        "STYLE": STYLE,
        "INTWALL": INTWALL,
        "EXTWALL": EXTWALL,
        "ROOF": ROOF,
        "STRUCT": STRUCT,
        "AYB": AYB,
        "EYB": EYB,
        "GBA": GBA, 
        "LANDAREA": LANDAREA, 
        "CNDTN": CNDTN,
        "SALE_NUM": SALENUM,
        "SALEYEAR": SALEYEAR,   
        "GRADE": GRADE,
        "WARD": WARD,  
    }

    # Convert Features into DataFrame
    features_df = pd.DataFrame([features])
    st.dataframe(features_df)

    if SALEYEAR < EYB:
        EYB_SALEYEAR_DIFF = 0
    else:
        EYB_SALEYEAR_DIFF = SALEYEAR-EYB

    SQFT_ROOMS = GBA/ROOMS

    # Feature Engineering
    features = {
        "BATHRM": BATHRM,
        "HF_BATHRM": HF_BATHRM,
        "HEAT": HEAT,
        "AC": AC,
        "BEDRM": BEDRM,
        "SALE_NUM": SALENUM,
        "AYB_SALEYEAR_DIFF": SALEYEAR-AYB,
        "EYB_SALEYEAR_DIFF": EYB_SALEYEAR_DIFF,
        "GBA": GBA,
        "STYLE": STYLE,
        "STRUCT": STRUCT,
        "GRADE": GRADE,
        "CNDTN": CNDTN,
        "EXTWALL": EXTWALL,
        "ROOF": ROOF,
        "INTWALL": INTWALL,
        "KITCHENS": KITCHENS,
        "FIREPLACES": FIREPLACES,
        "LANDAREA": LANDAREA,
        "WARD": WARD,
        "SALEYEAR": SALEYEAR,
        "RMDL": RMDL,
        "SQFT_ROOMS": SQFT_ROOMS
    }

    features_df = pd.DataFrame([features])

    # predict button
    if st.button("Predict"):
        my_bar = st.progress(0)

        for percent_complete in range(100):
            time.sleep(0.025)
            my_bar.progress(percent_complete + 1)

        model = load_model("catboost_final")
        lower, predicted_price, upper = predict(model, features_df)

        if lower >= 100000:
            st.success(
                "✅ Based on the features, the price of the property is $"
                + str(int(predicted_price))
                + ". This type of house typically sold from $"
                + str(int(lower))
                + " up to $"
                + str(int(upper))
                + "."
            )
        else:
            st.success(
                "✅ Based on the features, the price of the property is $"
                + str(int(predicted_price))
                + ". This type of house typically sold up to $"
                + str(int(upper))
                + "."
            )

    st.write("---")
    # Data Section
    expander_bar = st.beta_expander("Data Description")
    expander_bar.markdown(
        """
    |            Feature            |                         Description                          | 
    | :-----------------------------: | -------------- |
    | ROOMS | Number of Rooms |
    | BATHRM | Number of Bathroom     |
    | HF_BATHRM | Number of half bathroom (no bathtub or shower) |
    | HEAT | Heating Type |
    | AC | Has AC? (Y/N) |
    | BEDRM | Number of bedroom |
    | AYB | 	The earliest time the main portion of the building was built |
    | EYB | The year an improvement was built more recent than actual year built |
    | GBA | Gross building area in square feet |
    | STYLE | Type of story |
    | STRUCT | 	Building structure |
    | GRADE | Property Grade |
    | CNDTN | Property Condition |
    | EXTWALL | Exterior wall type |
    | ROOF | Roof type |
    | INTWALL | Interior wall type |
    | KITCHENS | Number of kitchens |
    | FIREPLACES | Number of fireplaces |
    | LANDAREA | Land area of property in square feet |
    | WARD | Ward (district is divided into eight wards, each with approximately 75,000 residents) |
    | SALEYEAR | Year of most recent sale |
    | RMDL | Has remodeled? (Y/N)

    """
    )
    expander_bar.write('')

if __name__ == "__main__":
    main()