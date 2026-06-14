import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import os
from datetime import datetime

st.set_page_config(page_title="Airbnb Analytics", layout="wide", initial_sidebar_state="expanded")

# Font Awesome via CDN
st.markdown("""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
""", unsafe_allow_html=True)

@st.cache_resource
def get_connection():
    try:
        db_path = "c:/laragon/www/Airbnb-Analytics-Platform/Airbnb-Analytics-Platform/airbnb_analytics/dev.duckdb"
        conn = duckdb.connect(db_path, read_only=True)
        conn.execute("SELECT 1")
        return conn
    except Exception as e:
        st.error(f"Erreur de connexion à DuckDB: {str(e)}")
        st.info("Assurez-vous que `dbt seed && dbt run` ont été exécutés avec succès.")
        st.stop()

def load_data(query):
    try:
        conn = get_connection()
        return conn.execute(query).df()
    except Exception as e:
        st.error(f"Erreur lors du chargement: {str(e)}")
        return pd.DataFrame()

st.sidebar.markdown("### <i class='fas fa-home'></i> Airbnb Analytics", unsafe_allow_html=True)
page = st.sidebar.radio("Navigation", [
    "Accueil",
    "Analyse Hôtes",
    "Analyse Listings",
    "Analyse Avis",
    "Impact Pleine Lune"
])

if page == "Accueil":
    st.markdown("# <i class='fas fa-chart-bar'></i> Dashboard Airbnb Analytics", unsafe_allow_html=True)
    st.markdown("Bienvenue! Sélectionnez une analyse dans le menu latéral.")

    col1, col2, col3, col4 = st.columns(4)

    hosts = load_data("SELECT COUNT(DISTINCT host_id) as count FROM main_gold.fct_gold_dim_hosts")
    listings = load_data("SELECT COUNT(DISTINCT listing_id) as count FROM main_gold.fct_gold_dim_listings")
    reviews = load_data("SELECT COUNT(*) as count FROM main_gold.fct_gold_fact_reviews")
    superhosts = load_data("SELECT COUNT(DISTINCT host_id) as count FROM main_gold.fct_gold_dim_hosts WHERE is_superhost = TRUE")

    with col1:
        if len(hosts) > 0:
            st.metric("Total Hôtes", int(hosts['count'].values[0]))
    with col2:
        if len(listings) > 0:
            st.metric("Total Listings", int(listings['count'].values[0]))
    with col3:
        if len(reviews) > 0:
            st.metric("Total Avis", int(reviews['count'].values[0]))
    with col4:
        if len(superhosts) > 0:
            st.metric("Superhosts", int(superhosts['count'].values[0]))

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### <i class='fas fa-pie-chart'></i> Distribution par Type de Chambre", unsafe_allow_html=True)
        room_dist = load_data("""
            SELECT room_type, COUNT(*) as count
            FROM main_gold.fct_gold_dim_listings
            GROUP BY room_type
            ORDER BY count DESC
        """)
        if len(room_dist) > 0:
            fig = px.pie(room_dist, values='count', names='room_type',
                         title="Répartition des Listings par Type")
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### <i class='fas fa-tags'></i> Top Catégories de Prix", unsafe_allow_html=True)
        price_dist = load_data("""
            SELECT price_category, COUNT(*) as count
            FROM main_gold.fct_gold_dim_listings
            GROUP BY price_category
            ORDER BY count DESC
        """)
        if len(price_dist) > 0:
            fig = px.bar(price_dist, x='price_category', y='count',
                         title="Listings par Catégorie de Prix")
            st.plotly_chart(fig, use_container_width=True)

elif page == "Analyse Hôtes":
    st.markdown("# <i class='fas fa-hotel'></i> Analyse des Hôtes", unsafe_allow_html=True)

    st.sidebar.markdown("### <i class='fas fa-filter'></i> Filtres - Hôtes", unsafe_allow_html=True)

    min_reviews = st.sidebar.slider(
        "Nombre minimum d'avis",
        min_value=0,
        max_value=500,
        value=0,
        step=10
    )

    superhosts_only = st.sidebar.checkbox(
        "Seulement les Superhosts",
        value=False
    )

    min_rating = st.sidebar.slider(
        "Taux minimum d'avis positifs (%)",
        min_value=0.0,
        max_value=100.0,
        value=0.0,
        step=5.0
    )

    where_conditions = []
    if min_reviews > 0:
        where_conditions.append(f"total_reviews >= {min_reviews}")
    if superhosts_only:
        where_conditions.append("is_superhost = TRUE")
    if min_rating > 0:
        where_conditions.append(f"positive_review_rate >= {min_rating / 100}")

    where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"

    hosts_data = load_data(f"""
        SELECT
            host_id, host_name, is_superhost,
            total_listings, listings_with_reviews,
            avg_listing_price, total_reviews,
            positive_review_rate
        FROM main_gold.fct_gold_dim_hosts
        WHERE {where_clause}
        ORDER BY total_reviews DESC
        LIMIT 100
    """)

    st.info(f"Résultats: {len(hosts_data)} hôtes correspondent aux filtres")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### <i class='fas fa-chart-column'></i> Top 10 Hôtes par Avis", unsafe_allow_html=True)
        top_hosts = hosts_data.head(10)
        if len(top_hosts) > 0:
            fig = px.bar(top_hosts, x='host_name', y='total_reviews',
                         color='is_superhost',
                         title="Top 10 Hôtes (par nombre d'avis)")
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### <i class='fas fa-dollar-sign'></i> Prix Moyen (Top 10)", unsafe_allow_html=True)
        top_hosts_price = hosts_data.head(10)
        if len(top_hosts_price) > 0:
            fig = px.bar(top_hosts_price, x='host_name', y='avg_listing_price',
                         title="Prix Moyen des Listings (Top 10 Hôtes)")
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### <i class='fas fa-chart-scatter'></i> Listings vs Avis", unsafe_allow_html=True)
        if len(hosts_data) > 0:
            fig = px.scatter(hosts_data, x='total_listings', y='total_reviews',
                            color='positive_review_rate', size='avg_listing_price',
                            hover_name='host_name',
                            title="Listings vs Avis (taille = prix moyen)")
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### <i class='fas fa-histogram'></i> Distribution Taux Positif", unsafe_allow_html=True)
        if len(hosts_data) > 0:
            fig = px.histogram(hosts_data, x='positive_review_rate', nbins=20,
                              title="Distribution du Taux d'Avis Positifs")
            st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.markdown("### <i class='fas fa-table'></i> Tableau Détaillé des Hôtes", unsafe_allow_html=True)
    st.dataframe(hosts_data, use_container_width=True, hide_index=True)

elif page == "Analyse Listings":
    st.markdown("# <i class='fas fa-home'></i> Analyse des Listings", unsafe_allow_html=True)

    st.sidebar.markdown("### <i class='fas fa-filter'></i> Filtres - Listings", unsafe_allow_html=True)

    room_types = st.sidebar.multiselect(
        "Type de chambre",
        options=['Entire home/apt', 'Private room', 'Shared room', 'Hotel room'],
        default=['Entire home/apt', 'Private room']
    )

    price_categories = st.sidebar.multiselect(
        "Catégorie de prix",
        options=['Budget', 'Economique', 'Standard', 'Premium', 'Luxe'],
        default=['Budget', 'Economique', 'Standard']
    )

    min_price = st.sidebar.number_input(
        "Prix minimum par nuit ($)",
        min_value=0,
        value=0,
        step=10
    )

    max_price = st.sidebar.number_input(
        "Prix maximum par nuit ($)",
        min_value=0,
        value=1000,
        step=50
    )

    room_filter = ",".join(f"'{rt}'" for rt in room_types) if room_types else "'Entire home/apt'"
    price_filter = ",".join(f"'{pc}'" for pc in price_categories) if price_categories else "'Standard'"

    listings_data = load_data(f"""
        SELECT
            listing_id, listing_name, room_type, host_name,
            nightly_price, price_category, minimum_nights,
            total_reviews, reviews_per_day, positive_review_pct,
            days_listed
        FROM main_gold.fct_gold_dim_listings
        WHERE room_type IN ({room_filter})
            AND price_category IN ({price_filter})
            AND nightly_price BETWEEN {min_price} AND {max_price}
        ORDER BY total_reviews DESC
        LIMIT 200
    """)

    st.info(f"Résultats: {len(listings_data)} listings correspondent aux filtres")

    col1, col2, col3 = st.columns(3)

    with col1:
        avg_price = listings_data['nightly_price'].mean() if len(listings_data) > 0 else 0
        st.metric("Prix Moyen", f"${avg_price:.2f}")

    with col2:
        avg_reviews = listings_data['total_reviews'].mean() if len(listings_data) > 0 else 0
        st.metric("Avis Moyen/Listing", f"{avg_reviews:.0f}")

    with col3:
        avg_positive = listings_data['positive_review_pct'].mean() if len(listings_data) > 0 else 0
        st.metric("Taux Positif Moyen", f"{avg_positive:.1%}")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### <i class='fas fa-chart-box'></i> Distribution des Prix par Type", unsafe_allow_html=True)
        if len(listings_data) > 0:
            fig = px.box(listings_data, x='room_type', y='nightly_price',
                        title="Prix par Type de Chambre")
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### <i class='fas fa-chart-scatter'></i> Avis vs Prix", unsafe_allow_html=True)
        if len(listings_data) > 0:
            fig = px.scatter(listings_data, x='nightly_price', y='total_reviews',
                            color='room_type', size='positive_review_pct',
                            hover_name='listing_name',
                            title="Relation Prix vs Avis")
            st.plotly_chart(fig, use_container_width=True)

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### <i class='fas fa-ranking-star'></i> Top 15 Listings par Avis", unsafe_allow_html=True)
        top_listings = listings_data.head(15)
        if len(top_listings) > 0:
            fig = px.bar(top_listings, x='listing_name', y='total_reviews',
                        color='price_category',
                        title="Top 15 Listings (par avis)")
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### <i class='fas fa-tachometer-alt'></i> Vitesse de Reviews", unsafe_allow_html=True)
        if len(listings_data) > 0:
            fig = px.histogram(listings_data, x='reviews_per_day', nbins=30,
                              title="Distribution Reviews par Jour")
            st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.markdown("### <i class='fas fa-table'></i> Tableau des Listings", unsafe_allow_html=True)
    st.dataframe(listings_data.head(100), use_container_width=True, hide_index=True)

elif page == "Analyse Avis":
    st.markdown("# <i class='fas fa-star'></i> Analyse des Avis", unsafe_allow_html=True)

    st.sidebar.markdown("### <i class='fas fa-filter'></i> Filtres - Avis", unsafe_allow_html=True)

    sentiments = st.sidebar.multiselect(
        "Sentiments",
        options=['positive', 'negative', 'neutral'],
        default=['positive', 'negative', 'neutral']
    )

    min_review_date = st.sidebar.date_input(
        "Date minimum des avis",
        value=datetime(2009, 6, 20).date()
    )

    positive_only = st.sidebar.checkbox(
        "Seulement avis positifs",
        value=False
    )

    sentiment_filter = ",".join(f"'{s}'" for s in sentiments) if sentiments else "'positive'"
    where_conditions = [f"sentiment IN ({sentiment_filter})", f"review_date >= '{min_review_date}'"]

    if positive_only:
        where_conditions.append("is_positive_review = TRUE")

    where_clause = " AND ".join(where_conditions)

    reviews_data = load_data(f"""
        SELECT *
        FROM main_gold.fct_gold_fact_reviews
        WHERE {where_clause}
        ORDER BY review_date DESC
    """)

    st.info(f"Résultats: {len(reviews_data)} avis correspondent aux filtres")

    col1, col2, col3 = st.columns(3)

    with col1:
        total_reviews = len(reviews_data)
        st.metric("Total Avis", total_reviews)

    with col2:
        if len(reviews_data) > 0:
            positive_pct = (reviews_data['is_positive_review'].sum() / len(reviews_data)) * 100
            st.metric("Avis Positifs", f"{positive_pct:.1f}%")
        else:
            st.metric("Avis Positifs", "0%")

    with col3:
        if len(reviews_data) > 0:
            avg_text_length = reviews_data['review_text_length'].mean()
            st.metric("Longueur Moyenne", f"{avg_text_length:.0f} caractères")
        else:
            st.metric("Longueur Moyenne", "0")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### <i class='fas fa-pie-chart'></i> Distribution Sentiments", unsafe_allow_html=True)
        if len(reviews_data) > 0:
            sentiment_dist = reviews_data['sentiment'].value_counts().reset_index()
            sentiment_dist.columns = ['sentiment', 'count']
            fig = px.pie(sentiment_dist, values='count', names='sentiment',
                        title="Distribution des Sentiments")
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### <i class='fas fa-chart-line'></i> Avis par Mois", unsafe_allow_html=True)
        if len(reviews_data) > 0:
            reviews_monthly = reviews_data.copy()
            reviews_monthly['month'] = pd.to_datetime(reviews_monthly['review_date']).dt.to_period('M')
            monthly_count = reviews_monthly.groupby('month').size().reset_index(name='count')
            monthly_count['month'] = monthly_count['month'].astype(str)
            fig = px.line(monthly_count, x='month', y='count',
                         title="Tendance des Avis par Mois", markers=True)
            st.plotly_chart(fig, use_container_width=True)

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### <i class='fas fa-calendar'></i> Avis par Jour de la Semaine", unsafe_allow_html=True)
        if len(reviews_data) > 0:
            day_names = {1: 'Lun', 2: 'Mar', 3: 'Mer', 4: 'Jeu', 5: 'Ven', 6: 'Sam', 7: 'Dim'}
            reviews_data_copy = reviews_data.copy()
            reviews_data_copy['day_name'] = reviews_data_copy['review_day_of_week'].map(day_names)
            day_dist = reviews_data_copy['day_name'].value_counts().reindex(['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'])
            fig = px.bar(x=day_dist.index, y=day_dist.values,
                        title="Avis par Jour de la Semaine",
                        labels={'x': 'Jour', 'y': 'Nombre d\'avis'})
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### <i class='fas fa-histogram'></i> Distribution Longueur Avis", unsafe_allow_html=True)
        if len(reviews_data) > 0:
            fig = px.histogram(reviews_data, x='review_text_length', nbins=50,
                              title="Longueur des Avis")
            st.plotly_chart(fig, use_container_width=True)

elif page == "Impact Pleine Lune":
    st.markdown("# <i class='fas fa-moon'></i> Analyse: Impact de la Pleine Lune", unsafe_allow_html=True)

    st.sidebar.markdown("### <i class='fas fa-filter'></i> Filtres - Pleine Lune", unsafe_allow_html=True)

    fm_sentiments = st.sidebar.multiselect(
        "Sentiments (Pleine Lune)",
        options=['positive', 'negative', 'neutral'],
        default=['positive', 'negative', 'neutral']
    )

    fm_positive_only = st.sidebar.checkbox(
        "Seulement positifs (Pleine Lune)",
        value=False
    )

    fm_sentiment_filter = ",".join(f"'{s}'" for s in fm_sentiments) if fm_sentiments else "'positive'"
    fm_where_conditions = [f"sentiment IN ({fm_sentiment_filter})"]

    if fm_positive_only:
        fm_where_conditions.append("is_positive = TRUE")

    fm_where_clause = " AND ".join(fm_where_conditions)

    fm_data = load_data(f"""
        SELECT *
        FROM main_gold.fct_gold_fact_full_moon_reviews
        WHERE {fm_where_clause}
        ORDER BY review_date DESC
    """)

    st.info(f"Résultats: {len(fm_data)} avis en pleine lune correspondent aux filtres")

    if len(fm_data) > 0:
        col1, col2 = st.columns(2)

        with col1:
            total_fm_reviews = len(fm_data)
            st.metric("Avis en Pleine Lune", total_fm_reviews)

        with col2:
            positive_pct = (fm_data['is_positive'].sum() / len(fm_data)) * 100
            st.metric("Avis Positifs (PL)", f"{positive_pct:.1f}%")

        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### <i class='fas fa-pie-chart'></i> Sentiments Pleine Lune", unsafe_allow_html=True)
            sentiment_dist = fm_data['sentiment'].value_counts().reset_index()
            sentiment_dist.columns = ['sentiment', 'count']
            fig = px.pie(sentiment_dist, values='count', names='sentiment',
                        title="Sentiments lors de Pleine Lune")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### <i class='fas fa-ranking-star'></i> Top 10 Listings (PL)", unsafe_allow_html=True)
            top_listings_fm = fm_data['listing_name'].value_counts().head(10)
            fig = px.bar(x=top_listings_fm.values, y=top_listings_fm.index,
                        orientation='h',
                        title="Listings avec Plus d'Avis en Pleine Lune",
                        labels={'x': 'Nombre d\'avis', 'y': 'Listing'})
            st.plotly_chart(fig, use_container_width=True)

        st.divider()
        st.markdown("### <i class='fas fa-table'></i> Tableau Avis Pleine Lune", unsafe_allow_html=True)

        display_cols = ['listing_name', 'host_name', 'review_date', 'full_moon_date',
                       'sentiment', 'text_length']
        st.dataframe(fm_data[display_cols].head(100), use_container_width=True, hide_index=True)
    else:
        st.warning("Aucune donnée de pleine lune trouvée.")
