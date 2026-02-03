#!/usr/bin/env python
# coding: utf-8

# In[3]:


import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(
    page_title="Nutrition & Sustainability Dashboard",
    page_icon="🥗",
    layout="wide"
)

# ===============================
# LOAD DATA
# ===============================
@st.cache_data
def load_data():
    df = pd.read_csv("openfoodfacts_nutrition_final_2025-12-10.csv")

    # Cleaning
    df['nutriscore_grade'] = df['nutriscore_grade'].astype(str).str.lower()
    df['ecoscore_grade'] = df['ecoscore_grade'].astype(str).str.lower()
    df['nova_group'] = pd.to_numeric(df['nova_group'], errors='coerce')

    for col in ['energy-kcal_100g', 'fat_100g', 'sugars_100g', 'proteins_100g']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df['main_country'] = df['countries'].str.split(',').str[0].str.strip()
    df['main_category'] = df['categories'].str.split(',').str[0].str.strip()
    df['is_organic'] = df['labels'].astype(str).str.contains('organic', case=False)

    nutri_map = {'a':5, 'b':4, 'c':3, 'd':2, 'e':1}
    eco_map = {'a':5, 'b':4, 'c':3, 'd':2, 'e':1}

    df['nutri_score'] = df['nutriscore_grade'].map(nutri_map)
    df['eco_score'] = df['ecoscore_grade'].map(eco_map)

    return df

df = load_data()

# ===============================
# HEADER
# ===============================
st.title("🥗 Global Food Sustainability & Nutrition Dashboard")
st.markdown("**Interactive analysis of nutrition quality, sustainability & processing levels**")
st.markdown("---")

# ===============================
# SIDEBAR FILTERS
# ===============================
st.sidebar.title("🔍 Filters")

show_france = st.sidebar.checkbox("France", True)
show_usa = st.sidebar.checkbox("USA", True)
show_organic = st.sidebar.checkbox("Organic Only")

countries = []
if show_france:
    countries.append("France")
if show_usa:
    countries.append("United States of America")

top_categories = df['main_category'].value_counts().head(10).index.tolist()
selected_category = st.sidebar.selectbox(
    "Product Category",
    ["All"] + top_categories
)

selected_nutri = st.sidebar.multiselect(
    "Nutri-Score",
    ['a','b','c','d','e'],
    default=['a','b','c','d','e']
)

selected_nova = st.sidebar.multiselect(
    "NOVA Group",
    [1,2,3,4],
    default=[1,2,3,4]
)

sugar_range = st.sidebar.slider(
    "Sugar (g / 100g)",
    0, 100, (0, 100)
)

# ===============================
# APPLY FILTERS
# ===============================
filtered_df = df[df['main_country'].isin(countries)]

if show_organic:
    filtered_df = filtered_df[filtered_df['is_organic']]

if selected_category != "All":
    filtered_df = filtered_df[filtered_df['main_category'] == selected_category]

filtered_df = filtered_df[filtered_df['nutriscore_grade'].isin(selected_nutri)]
filtered_df = filtered_df[filtered_df['nova_group'].isin(selected_nova)]
filtered_df = filtered_df[
    (filtered_df['sugars_100g'] >= sugar_range[0]) &
    (filtered_df['sugars_100g'] <= sugar_range[1])
]

# ===============================
# METRICS
# ===============================
c1, c2, c3 = st.columns(3)
c1.metric("Products", len(filtered_df))
c2.metric("Avg Nutri-Score", f"{filtered_df['nutri_score'].mean():.2f}")
c3.metric("Organic %", f"{filtered_df['is_organic'].mean()*100:.1f}%")

st.markdown("---")

# ===============================
# 1. NUTRI-SCORE DISTRIBUTION
# ===============================
st.subheader("1. Nutri-Score Distribution")
fig, ax = plt.subplots(figsize=(8,5))
filtered_df['nutriscore_grade'].value_counts() \
    .reindex(['a','b','c','d','e']) \
    .plot(kind='bar', color=['green','lightgreen','gold','orange','red'], ax=ax)
ax.set_ylabel("Number of Products")
st.pyplot(fig)

# ===============================
# 2. TOP BRANDS
# ===============================
st.subheader("2. Top 10 Healthiest Brands")
top_brands = filtered_df.dropna(subset=['brands','nutri_score']) \
    .groupby('brands')['nutri_score'].mean().nlargest(10)
fig, ax = plt.subplots(figsize=(8,5))
top_brands.plot(kind='barh', ax=ax)
ax.set_xlabel("Average Nutri-Score")
st.pyplot(fig)

# ===============================
# 3. SUGAR BY CATEGORY
# ===============================
st.subheader("3. Sugar Content by Category")
top_cat = filtered_df['main_category'].value_counts().head(6).index
fig, ax = plt.subplots(figsize=(10,5))
sns.boxplot(
    data=filtered_df[filtered_df['main_category'].isin(top_cat)],
    x='main_category', y='sugars_100g', ax=ax
)
ax.tick_params(axis='x', rotation=45)
st.pyplot(fig)

# ===============================
# 4. PROTEIN VS FAT
# ===============================
st.subheader("4. Protein vs Fat Content")
fig, ax = plt.subplots(figsize=(8,5))
ax.scatter(filtered_df['fat_100g'], filtered_df['proteins_100g'], alpha=0.6)
ax.set_xlabel("Fat (g/100g)")
ax.set_ylabel("Protein (g/100g)")
st.pyplot(fig)

# ===============================
# 5. NUTRI vs ECO
# ===============================
st.subheader("5. Nutri-Score vs Eco-Score")
corr_df = filtered_df.dropna(subset=['nutri_score','eco_score'])
fig, ax = plt.subplots(figsize=(6,5))
ax.scatter(corr_df['nutri_score'], corr_df['eco_score'], alpha=0.7)
ax.set_title(f"Correlation: {corr_df['nutri_score'].corr(corr_df['eco_score']):.3f}")
ax.set_xlabel("Nutri-Score")
ax.set_ylabel("Eco-Score")
st.pyplot(fig)

# ===============================
# 6. CALORIES BY NOVA
# ===============================
st.subheader("6. Calories by Processing Level (NOVA)")
fig, ax = plt.subplots(figsize=(8,5))
sns.violinplot(
    data=filtered_df.dropna(subset=['nova_group','energy-kcal_100g']),
    x='nova_group', y='energy-kcal_100g', ax=ax
)
ax.set_xlabel("NOVA Group")
ax.set_ylabel("Calories / 100g")
st.pyplot(fig)

# ===============================
# 7. HIGH SUGAR COUNTRIES
# ===============================
st.subheader("7. High-Sugar Products by Country")
hs = filtered_df['sugars_100g'] >= 15
country_hs = hs.groupby(filtered_df['main_country']).mean()*100
fig, ax = plt.subplots(figsize=(8,5))
country_hs.sort_values().plot(kind='barh', ax=ax)
ax.set_xlabel("% High Sugar Products")
st.pyplot(fig)

# ===============================
# 8. ORGANIC VS NUTRI
# ===============================
st.subheader("8. Organic vs Nutri-Score")
fig, ax = plt.subplots(figsize=(8,5))
filtered_df.groupby(['is_organic','nutriscore_grade']).size().unstack().plot(
    kind='bar', ax=ax
)
st.pyplot(fig)

# ===============================
# 9. ULTRA-PROCESSED SHARE
# ===============================
st.subheader("9. Ultra-Processed Food Share")
ultra = filtered_df.groupby('main_country')['nova_group'] \
    .apply(lambda x: (x==4).mean()*100)
fig, ax = plt.subplots(figsize=(8,5))
ultra.sort_values().plot(kind='barh', ax=ax)
ax.set_xlabel("% Ultra-Processed")
st.pyplot(fig)

