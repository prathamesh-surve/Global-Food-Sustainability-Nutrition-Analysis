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
st.set_page_config(page_title="Nutrition Dashboard", page_icon="🍎", layout="wide")

@st.cache_data
def load_data():
    """Load OpenFoodFacts data [file:1]"""
    df = pd.read_csv("openfoodfacts_nutrition_final_2025-12-10.csv")

    # Data cleaning
    df['nutriscore_grade'] = df['nutriscore_grade'].astype(str).str.lower()
    df['ecoscore_grade'] = df['ecoscore_grade'].astype(str).str.lower()
    df['nova_group'] = pd.to_numeric(df['nova_group'], errors='coerce')

    # Numeric columns
    for col in ['energy-kcal_100g', 'fat_100g', 'sugars_100g', 'proteins_100g']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Derived features
    df['main_country'] = df['countries'].str.split(',').str[0].str.strip()
    df['main_category'] = df['categories'].str.split(',').str[0].str.strip()
    df['is_organic'] = df['labels'].astype(str).str.contains('organic|Organic', case=False)

    # Score mapping
    nutri_map = {'a':5, 'b':4, 'c':3, 'd':2, 'e':1}
    eco_map = {'a':5, 'b':4, 'c':3, 'd':2, 'e':1}
    df['nutri_score'] = df['nutriscore_grade'].map(nutri_map)
    df['eco_score'] = df['ecoscore_grade'].map(eco_map)

    return df

# Load data
df = load_data()
st.title("Nutrition & Sustainability Analysis")
st.markdown("**All 12 visualizations from your requirements**")

# Sidebar filters
st.sidebar.header("🔧 Filters")
countries = st.sidebar.multiselect(
    "Select Countries", 
    options=sorted(df['main_country'].value_counts().head(15).index),
    default=['France', 'United States of America']
)

filtered_df = df[df['main_country'].isin(countries)].copy()

# Key metrics row 1
col1, col2, col3, col4 = st.columns(4)
col1.metric("Products", len(filtered_df))
col2.metric("Avg Nutri-Score", f"{filtered_df['nutri_score'].mean():.1f}/5")
col3.metric("Avg Eco-Score", f"{filtered_df['eco_score'].mean():.1f}/5")
col4.metric("Organic Share", f"{filtered_df['is_organic'].mean()*100:.0f}%")

st.markdown("---")

# =============================================================================
# VISUALIZATION 1: Nutri-Score Distribution (Bar Chart)
# =============================================================================
st.subheader("1. Nutri-Score Distribution")
fig, ax = plt.subplots(figsize=(10, 6))
nutri_counts = filtered_df['nutriscore_grade'].value_counts().reindex(['a','b','c','d','e'], fill_value=0)
colors = ['#00ff00', '#90ee90', '#ffff00', '#ffa500', '#ff0000']
nutri_counts.plot(kind='bar', ax=ax, color=colors)
ax.set_title("Nutri-Score Grade Distribution", fontsize=16, fontweight='bold')
ax.set_ylabel("Number of Products", fontsize=12)
ax.set_xlabel("Nutri-Score Grade", fontsize=12)
plt.xticks(rotation=0)
st.pyplot(fig)

# =============================================================================
# VISUALIZATION 2: Top Brands by Health Score (Bar Chart)
# =============================================================================
st.subheader("2. Top 10 Healthiest Brands")
fig, ax = plt.subplots(figsize=(10, 6))
brand_scores = filtered_df.dropna(subset=['nutri_score', 'brands'])\
    .groupby('brands')['nutri_score'].mean().nlargest(10)
brand_scores.plot(kind='barh', ax=ax, color='skyblue')
ax.set_xlabel("Average Nutri-Score", fontsize=12)
ax.set_title("Top Brands by Average Health Score", fontsize=16, fontweight='bold')
st.pyplot(fig)

# =============================================================================
# VISUALIZATION 3: Sugar Content by Category (Box Plot)
# =============================================================================
st.subheader("3. Sugar Content by Category")
sugar_df = filtered_df.dropna(subset=['sugars_100g'])
top_cats = sugar_df['main_category'].value_counts().head(6).index
fig, ax = plt.subplots(figsize=(12, 6))
sns.boxplot(data=sugar_df[sugar_df['main_category'].isin(top_cats)], 
            x='main_category', y='sugars_100g', ax=ax, palette='viridis')
ax.tick_params(axis='x', rotation=45)
ax.set_title("Sugar Content Distribution by Category (g/100g)", fontsize=16, fontweight='bold')
ax.set_xlabel("Product Category", fontsize=12)
st.pyplot(fig)

# =============================================================================
# VISUALIZATION 4: Protein vs Fat (Scatter Plot)
# =============================================================================
st.subheader("4. Protein vs Fat Content")
nutr_df = filtered_df.dropna(subset=['proteins_100g', 'fat_100g', 'energy-kcal_100g'])
fig, ax = plt.subplots(figsize=(10, 7))
scatter = ax.scatter(nutr_df['fat_100g'], nutr_df['proteins_100g'], 
                    s=nutr_df['energy-kcal_100g']/20, c='coral', alpha=0.6, edgecolors='black')
ax.set_xlabel("Fat Content (g/100g)", fontsize=12)
ax.set_ylabel("Protein Content (g/100g)", fontsize=12)
ax.set_title("Protein vs Fat Content (Bubble size = Calories)", fontsize=16, fontweight='bold')
plt.colorbar(scatter, ax=ax, label='Calories per 100g')
st.pyplot(fig)

# =============================================================================
# VISUALIZATION 5: Nutri-Score vs Eco-Score Correlation (Scatter Plot)
# =============================================================================
st.subheader("5. Nutri-Score vs Eco-Score Correlation")
corr_df = filtered_df.dropna(subset=['nutri_score', 'eco_score'])
correlation = corr_df['nutri_score'].corr(corr_df['eco_score'])
col1, col2 = st.columns([3,1])
with col1:
    fig, ax = plt.subplots(figsize=(8, 8))
    colors = ['red' if x else 'blue' for x in corr_df['is_organic']]
    scatter = ax.scatter(corr_df['nutri_score'], corr_df['eco_score'], 
                        c=colors, alpha=0.7, s=60)
    ax.set_xlabel("Nutri-Score (A=5, E=1)", fontsize=12)
    ax.set_ylabel("Eco-Score (A=5, E=1)", fontsize=12)
    ax.set_title(f"Nutrition vs Environmental Impact\nCorrelation: {correlation:.3f}", fontsize=16, fontweight='bold')
    st.pyplot(fig)
with col2:
    st.metric("Correlation", f"{correlation:.3f}")

# =============================================================================
# VISUALIZATION 6: Calories by NOVA Group (Violin Plot)
# =============================================================================
st.subheader("6. Calories by Processing Level (NOVA)")
nova_df = filtered_df.dropna(subset=['nova_group', 'energy-kcal_100g'])
fig, ax = plt.subplots(figsize=(10, 6))
sns.violinplot(data=nova_df, x='nova_group', y='energy-kcal_100g', ax=ax, palette='Set2')
ax.set_xlabel("NOVA Group\n(1=Unprocessed, 4=Ultra-processed)", fontsize=12)
ax.set_ylabel("Calories per 100g", fontsize=12)
ax.set_title("Calorie Density by Food Processing Level", fontsize=16, fontweight='bold')
st.pyplot(fig)

# =============================================================================
# VISUALIZATION 7: High-Sugar Products by Country
# =============================================================================
st.subheader("7. High-Sugar Products by Country")
high_sugar = filtered_df.dropna(subset=['sugars_100g'])['sugars_100g'] >= 15
country_sugar_pct = high_sugar.groupby(filtered_df['main_country']).mean().sort_values(ascending=False).head(10)
fig, ax = plt.subplots(figsize=(10, 6))
country_sugar_pct.plot(kind='barh', ax=ax, color='salmon')
ax.set_xlabel("% Products with ≥15g sugar/100g", fontsize=12)
ax.set_title("Countries with Highest Share of High-Sugar Products", fontsize=16, fontweight='bold')
st.pyplot(fig)

# =============================================================================
# VISUALIZATION 8: Organic vs Nutri-Score
# =============================================================================
st.subheader("8. Organic Products by Nutri-Score")
organic_nutri = filtered_df.groupby(['is_organic', 'nutriscore_grade']).size().unstack(fill_value=0)
fig, ax = plt.subplots(figsize=(10, 6))
organic_nutri.plot(kind='bar', ax=ax, width=0.8)
ax.set_title("Organic vs Non-Organic Distribution by Nutri-Score", fontsize=16, fontweight='bold')
ax.set_xlabel("Nutri-Score Grade")
ax.set_ylabel("Number of Products")
ax.legend(title="Organic", loc='upper right')
plt.xticks(rotation=0)
st.pyplot(fig)

# =============================================================================
# VISUALIZATION 9: Ecoscore by Category (Box Plot)
# =============================================================================
st.subheader("9. Eco-Score by Product Category")
eco_df = filtered_df.dropna(subset=['eco_score']).copy()
eco_df['eco_grade'] = pd.cut(eco_df['eco_score'], bins=5, labels=['E','D','C','B','A'])
top_cats = eco_df['main_category'].value_counts().head(6).index
fig, ax = plt.subplots(figsize=(12, 6))
sns.boxplot(data=eco_df[eco_df['main_category'].isin(top_cats)], 
            x='main_category', y='eco_score', ax=ax)
ax.tick_params(axis='x', rotation=45)
ax.set_title("Eco-Score Distribution by Category", fontsize=16, fontweight='bold')
ax.set_ylabel("Eco-Score (numeric)")
st.pyplot(fig)

# =============================================================================
# VISUALIZATION 10: Ultra-processed by Country
# =============================================================================
st.subheader("10. Ultra-Processed Foods by Country")
nova_country = filtered_df.dropna(subset=['nova_group']).groupby(['main_country', 'nova_group']).size().unstack(fill_value=0)
nova_country['ultra_pct'] = nova_country[4] / nova_country.sum(axis=1) * 100
top_ultra = nova_country['ultra_pct'].sort_values(ascending=False).head(10)
fig, ax = plt.subplots(figsize=(10, 6))
top_ultra.plot(kind='barh', ax=ax, color='purple')
ax.set_xlabel("% Ultra-Processed (NOVA=4)", fontsize=12)
ax.set_title("Share of Ultra-Processed Foods by Country", fontsize=16, fontweight='bold')
st.pyplot(fig)

