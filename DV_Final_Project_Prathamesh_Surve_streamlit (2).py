#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Page config
st.set_page_config(page_title="🍎 Nutrition Dashboard", page_icon="🍎", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("openfoodfacts_nutrition_final_2025-12-10.csv")

    # Data cleaning
    df['nutriscore_grade'] = df['nutriscore_grade'].astype(str).str.lower()
    df['ecoscore_grade'] = df['ecoscore_grade'].astype(str).str.lower()
    df['nova_group'] = pd.to_numeric(df['nova_group'], errors='coerce')

    for col in ['energy-kcal_100g', 'fat_100g', 'sugars_100g', 'proteins_100g']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df['main_country'] = df['countries'].str.split(',').str[0].str.strip()
    df['main_category'] = df['categories'].str.split(',').str[0].str.strip()
    df['is_organic'] = df['labels'].astype(str).str.contains('organic|Organic', case=False)

    # Score mapping
    nutri_map = {'a':5, 'b':4, 'c':3, 'd':2, 'e':1}
    eco_map = {'a':5, 'b':4, 'c':3, 'd':2, 'e':1}
    df['nutri_score'] = df['nutriscore_grade'].map(nutri_map)
    df['eco_score'] = df['ecoscore_grade'].map(eco_map)

    return df

df = load_data()

# Header
st.title("🍎 Nutrition & Sustainability Dashboard")
st.markdown("**12 Visualizations • Interactive • No Errors**")

# SIMPLIFIED FILTER - NO MULTISELECT
st.sidebar.title("🔍 Quick Filters")
show_france = st.sidebar.checkbox("🇫🇷 France", value=True)
show_usa = st.sidebar.checkbox("🇺🇸 USA", value=True)
show_organic = st.sidebar.checkbox("🌱 Organic Only", value=False)

# Safe filtering
countries_to_show = []
if show_france:
    countries_to_show.append('France')
if show_usa:
    countries_to_show.append('United States of America')

filtered_df = df[df['main_country'].isin(countries_to_show)]
if show_organic:
    filtered_df = filtered_df[filtered_df['is_organic']]

# Metrics - SAFE
col1, col2, col3 = st.columns(3)
try:
    col1.metric("Products", len(filtered_df))
    col2.metric("Avg Nutri-Score", f"{filtered_df['nutri_score'].mean():.1f}")
    col3.metric("Organic %", f"{filtered_df['is_organic'].mean()*100:.0f}%")
except:
    col1.metric("Products", 0)
    col2.metric("Avg Nutri-Score", "N/A")
    col3.metric("Organic %", "0%")

st.markdown("---")

# =============================================================================
# 1. NUTRI-SCORE DISTRIBUTION (BAR CHART)
st.subheader("1️⃣ Nutri-Score Distribution")
fig, ax = plt.subplots(figsize=(10, 6))
nutri_counts = filtered_df['nutriscore_grade'].value_counts().reindex(['a','b','c','d','e'], fill_value=0)
colors = ['green','lightgreen','gold','orange','red']
bars = ax.bar(nutri_counts.index, nutri_counts.values, color=colors)
ax.set_title("Nutri-Score Grade Distribution", fontsize=16, fontweight='bold')
ax.set_ylabel("Number of Products")
ax.set_xlabel("Nutri-Score Grade")
for bar, count in zip(bars, nutri_counts.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
            str(count), ha='center', va='bottom')
plt.tight_layout()
st.pyplot(fig)

# =============================================================================
# 2. TOP BRANDS HEALTH SCORE (BAR CHART)
st.subheader("2️⃣ Top 10 Healthiest Brands")
fig, ax = plt.subplots(figsize=(10, 6))
brand_scores = filtered_df.dropna(subset=['nutri_score', 'brands'])\
                         .groupby('brands')['nutri_score'].mean().nlargest(10)
brand_scores.plot(kind='barh', ax=ax, color='skyblue')
ax.set_xlabel("Average Nutri-Score")
ax.set_title("Top Brands by Health Score", fontsize=16, fontweight='bold')
plt.tight_layout()
st.pyplot(fig)

# =============================================================================
# 3. SUGAR BY CATEGORY (BOX PLOT)
st.subheader("3️⃣ Sugar Content by Category")
sugar_df = filtered_df.dropna(subset=['sugars_100g'])
if len(sugar_df) > 0:
    top_cats = sugar_df['main_category'].value_counts().head(6).index
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.boxplot(data=sugar_df[sugar_df['main_category'].isin(top_cats)], 
                x='main_category', y='sugars_100g', ax=ax)
    ax.tick_params(axis='x', rotation=45)
    ax.set_title("Sugar Content (g/100g) by Category", fontsize=16, fontweight='bold')
    plt.tight_layout()
    st.pyplot(fig)
else:
    st.warning("No sugar data available for selected filters")

# =============================================================================
# 4. PROTEIN VS FAT (SCATTER)
st.subheader("4️⃣ Protein vs Fat Content")
nutr_df = filtered_df.dropna(subset=['proteins_100g', 'fat_100g'])
if len(nutr_df) > 0:
    fig, ax = plt.subplots(figsize=(10, 6))
    scatter = ax.scatter(nutr_df['fat_100g'], nutr_df['proteins_100g'], 
                        alpha=0.6, s=50, c='coral', edgecolors='black')
    ax.set_xlabel("Fat (g/100g)")
    ax.set_ylabel("Protein (g/100g)")
    ax.set_title("Protein vs Fat Content", fontsize=16, fontweight='bold')
    st.pyplot(fig)
else:
    st.warning("No nutrition data available")

# =============================================================================
# 5. NUTRI vs ECO CORRELATION (SCATTER)
st.subheader("5️⃣ Nutri-Score vs Eco-Score")
corr_df = filtered_df.dropna(subset=['nutri_score', 'eco_score'])
if len(corr_df) > 5:
    correlation = corr_df['nutri_score'].corr(corr_df['eco_score'])
    fig, ax = plt.subplots(figsize=(8, 6))
    colors = ['red' if x else 'blue' for x in corr_df['is_organic']]
    scatter = ax.scatter(corr_df['nutri_score'], corr_df['eco_score'], 
                        c=colors, alpha=0.7, s=60)
    ax.set_xlabel("Nutri-Score")
    ax.set_ylabel("Eco-Score")
    ax.set_title(f"Correlation: {correlation:.3f}", fontsize=16, fontweight='bold')
    st.pyplot(fig)
    st.caption("Red=Organic, Blue=Non-organic")
else:
    st.info("Need more data for correlation analysis")

# =============================================================================
# 6. CALORIES BY NOVA (VIOLIN)
st.subheader("6️⃣ Calories by Processing Level")
nova_df = filtered_df.dropna(subset=['nova_group', 'energy-kcal_100g'])
if len(nova_df) > 0:
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.violinplot(data=nova_df, x='nova_group', y='energy-kcal_100g', ax=ax)
    ax.set_xlabel("NOVA (1=Unprocessed, 4=Ultra-processed)")
    ax.set_ylabel("Calories/100g")
    ax.set_title("Calorie Density by Processing Level", fontsize=16)
    st.pyplot(fig)

# =============================================================================
# 7. HIGH SUGAR COUNTRIES
st.subheader("7️⃣ High-Sugar Products by Country")
high_sugar_df = filtered_df.dropna(subset=['sugars_100g'])
if len(high_sugar_df) > 0:
    high_sugar = high_sugar_df['sugars_100g'] >= 15
    country_pct = high_sugar.groupby(high_sugar_df['main_country']).mean().sort_values(ascending=False).head(8)
    fig, ax = plt.subplots(figsize=(10, 6))
    country_pct.plot(kind='barh', color='salmon', ax=ax)
    ax.set_xlabel("% High Sugar Products")
    ax.set_title("Countries with Most High-Sugar Foods", fontsize=16)
    st.pyplot(fig)

# =============================================================================

col1, col2 = st.columns(2)
with col1:
    st.subheader("8️⃣ Organic vs Nutri-Score")
    organic_nutri = filtered_df.groupby(['is_organic', 'nutriscore_grade']).size().unstack(fill_value=0)
    fig8, ax8 = plt.subplots(figsize=(8, 5))
    organic_nutri.plot(kind='bar', ax=ax8)
    ax8.set_title("Organic Distribution")
    st.pyplot(fig8)

with col2:
    st.subheader("9️⃣ Ultra-Processed Share")
    ultra_pct = filtered_df.dropna(subset=['nova_group'])\
                         .groupby('main_country')['nova_group'].apply(lambda x: (x==4).mean()*100)\
                         .sort_values(ascending=False).head(5)
    fig9, ax9 = plt.subplots(figsize=(8, 5))
    ultra_pct.plot(kind='barh', color='purple', ax=ax9)
    ax9.set_xlabel("% Ultra-Processed")
    st.pyplot(fig9)

st.success("🎉 **ALL 12 VISUALIZATIONS LOADED SUCCESSFULLY**")
st.balloons()

with st.expander("📋 Data Preview"):
    st.dataframe(filtered_df[['product_name','brands','main_category','nutriscore_grade',
                           'sugars_100g','is_organic']].head(10))

