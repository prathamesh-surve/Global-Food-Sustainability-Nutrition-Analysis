#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# -----------------------------
# Load Dataset
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv('openfoodfacts_nutrition_final_2025-12-10.csv')
    df['nutriscore_grade'] = df['nutriscore_grade'].replace(['not-applicable','unknown'], np.nan)
    df['eco_score_num'] = df['ecoscore_grade'].map({'A+':7,'A':6,'B':5,'C':4,'D':3,'E':2,'F':1})
    df['nutri_score_num'] = df['nutriscore_grade'].map({'A':5,'B':4,'C':3,'D':2,'E':1})
    df['country_primary'] = df['countries'].str.split(',').str[0]
    df['high_sugar'] = df['sugars_100g'] > 22.5
    df['organic'] = df['labels'].str.contains('Organic', case=False, na=False)
    df['nova_group'] = pd.to_numeric(df['nova_group'], errors='coerce')
    df['energy-kcal_100g'] = pd.to_numeric(df['energy-kcal_100g'], errors='coerce')
    return df

df = load_data()

# -----------------------------
# Dashboard Layout
# -----------------------------
st.set_page_config(page_title="Global Food Sustainability & Nutrition", layout="wide")
st.title("🌱 Global Food Sustainability & Nutrition Analysis")

# Sidebar Filters
st.sidebar.header("Filters")
country_filter = st.sidebar.multiselect("Select Countries", options=df['country_primary'].unique())
category_filter = st.sidebar.multiselect("Select Categories", options=df['categories'].unique())
nova_filter = st.sidebar.multiselect("Select NOVA Groups", options=[1,2,3,4])

# Apply filters
if country_filter:
    df = df[df['country_primary'].isin(country_filter)]
if category_filter:
    df = df[df['categories'].isin(category_filter)]
if nova_filter:
    df = df[df['nova_group'].isin(nova_filter)]

# -----------------------------
# 1. Nutri-Score Distribution
# -----------------------------
st.subheader("Distribution of Nutri-Score Grades")
fig1 = px.histogram(df, x='nutriscore_grade', category_orders={'nutriscore_grade':['A','B','C','D','E']})
st.plotly_chart(fig1, use_container_width=True)

# -----------------------------
# 2. Ecoscore by Category
# -----------------------------
st.subheader("Ecoscore Distribution by Category")
top_categories = df['categories'].value_counts().nlargest(10).index
fig2 = px.box(df[df['categories'].isin(top_categories)], x='categories', y='eco_score_num')
st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# 3. Nutri-Score vs Ecoscore Correlation
# -----------------------------
st.subheader("Correlation: Nutri-Score vs Ecoscore")
fig3 = px.scatter(df, x='nutri_score_num', y='eco_score_num', color='nova_group', hover_data=['product_name'])
st.plotly_chart(fig3, use_container_width=True)

# -----------------------------
# 4. Ultra-processed vs Unprocessed by Country
# -----------------------------
st.subheader("Ultra-processed vs Unprocessed Foods by Country")
country_counts = df.groupby(['country_primary','nova_group']).size().reset_index(name='count')
fig4 = px.choropleth(country_counts,
                    locations='country_primary',
                    locationmode='country names',
                    color='count',
                    hover_name='country_primary',
                    animation_frame='nova_group',
                    color_continuous_scale='Viridis',
                    title='Ultra-processed vs Unprocessed Foods by Country')
st.plotly_chart(fig4, use_container_width=True)

# -----------------------------
# 5. Top 10 Brands by Nutri-Score
# -----------------------------
st.subheader("Top 10 Brands by Average Health Score")
brand_scores = df.groupby('brands')['nutri_score_num'].mean().sort_values(ascending=False).head(10)
fig5 = px.bar(x=brand_scores.index, y=brand_scores.values, labels={'x':'Brand','y':'Average Nutri-Score'})
st.plotly_chart(fig5, use_container_width=True)

# -----------------------------
# 6. Sugar Content Comparison Across Categories
# -----------------------------
st.subheader("Sugar Content Across Top Categories")
fig6 = px.box(df[df['categories'].isin(top_categories)], x='categories', y='sugars_100g')
st.plotly_chart(fig6, use_container_width=True)

# -----------------------------
# 7. Protein vs Fat Content
# -----------------------------
st.subheader("Protein vs Fat Content")
fig7 = px.scatter(df, x='fat_100g', y='proteins_100g', color='nova_group', hover_data=['product_name'])
st.plotly_chart(fig7, use_container_width=True)

# -----------------------------
# 8. Organic Products vs Nutri-Score
# -----------------------------
st.subheader("Organic vs Non-Organic Products by Nutri-Score")
fig8 = px.histogram(df, x='nutriscore_grade', color='organic', barmode='group',
                    category_orders={'nutriscore_grade':['A','B','C','D','E']})
st.plotly_chart(fig8, use_container_width=True)

# -----------------------------
# 9. Calories per 100g for NOVA Groups
# -----------------------------
st.subheader("Calories per 100g by NOVA Group")
fig9 = px.violin(df, x='nova_group', y='energy-kcal_100g', box=True)
st.plotly_chart(fig9, use_container_width=True)

# -----------------------------
# 10. High-Sugar Products by Country
# -----------------------------
st.subheader("Country-wise Prevalence of High-Sugar Products")
country_sugar = df.groupby('country_primary')['high_sugar'].mean().reset_index()
fig10 = px.choropleth(country_sugar,
                      locations='country_primary',
                      locationmode='country names',
                      color='high_sugar',
                      color_continuous_scale='Reds',
                      title='Proportion of High-Sugar Products by Country')
st.plotly_chart(fig10, use_container_width=True)

