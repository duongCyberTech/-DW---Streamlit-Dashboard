from api_call.api import Api
import streamlit as st

api = Api()

@st.cache_data
def get_all_transactions():
    return api.get_all_transactions()

@st.cache_data
def stats_counting():
    return api.stats_counting()

@st.cache_data
def revenue_in_year_by_month(selected_value, selected_period):
    return api.revenue_in_year_by_month(selected_value, selected_period)

@st.cache_data
def rfm_analysis(rfm_mall, selected_limit):
    return api.rfm_analysis(rfm_mall, selected_limit)

@st.cache_data
def rfm_segmentation(rfm_mall):
    return api.rfm_segmentation(rfm_mall)

def rfm_bill(payload):
    return api.rfm_bill(payload)

@st.cache_data
def model_metadata():
    return api.model_metadata()

@st.cache_data
def model_prediction(fdata):
    return api.model_prediction(fdata)