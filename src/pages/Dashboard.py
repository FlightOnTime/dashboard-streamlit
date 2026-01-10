import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

@st.cache_data
def loadData():
    connection = sqlite3.connect(":memory:")

    pages = os.path.dirname(os.path.abspath(__file__))
    
    archivePath = os.path.join(pages, 'MOCK_DATA.sql')
    
    with open(archivePath, 'r') as f:
        sqlScript = f.read()

    connection.executescript(sqlScript)

    query = "SELECT * FROM MOCK_DATA"
    df = pd.read_sql_query(query, connection)
    connection.close()

    df['data_partida'] = pd.to_datetime(df['data_partida'])
    df['data_apenas'] = df['data_partida'].dt.date
    df['linhas_aereas'] = df['origem_aeroporto'] + " -> " + df['destino_aeroporto']
    df['hora_partida'] = df['data_partida'].dt.hour
    
    return df
def loadDataToday():
    connection = sqlite3.connect(":memory:")

    pages = os.path.dirname(os.path.abspath(__file__))
    
    archivePath = os.path.join(pages, 'MOCK_DATA.sql')
    
    with open(archivePath, 'r') as f:
        sqlScript = f.read()

    connection.executescript(sqlScript)

    query = "SELECT * FROM MOCK_DATA WHERE DATE(data_partida) = DATE('now')"
    df = pd.read_sql_query(query, connection)
    connection.close()

    df['data_partida'] = pd.to_datetime(df['data_partida'])
    df['data_apenas'] = df['data_partida'].dt.date
    df['linhas_aereas'] = df['origem_aeroporto'] + " -> " + df['destino_aeroporto']
    df['hora_partida'] = df['data_partida'].dt.hour
    
    return df
try:
    dfToday = loadDataToday()
    col1, col2 = st.columns([0.85, 0.15])
    
    with col1:
        st.header("📊 Dashboard de Análise de Voos de Hoje")
    with col2:
        st.button("🔄 Atualizar Dados") #Its not working

    #Add random coordinates for demonstration
    n_points = 500
    df_fake = pd.DataFrame({
    'lat': np.random.uniform(-60, 80, n_points), 
    'lon': np.random.uniform(-180, 180, n_points),
    'valor': np.random.uniform(10, 100, n_points) 
    })

    fig1 = go.Figure()

# Adiciona a camada de "Heatmap" (Scattergeo com cores)
    fig1.add_trace(go.Scattergeo(
    lon = df_fake['lon'],
    lat = df_fake['lat'],
    mode = 'markers',
    marker = dict(
        size = 8,
        color = df_fake['valor'],        # A cor depende do valor (Heatmap)
        colorscale = 'Inferno',          # Escala de cores (Viridis, Plasma, Inferno, Magma)
        cmin = 0,
        cmax = 100,
        opacity = 0.8,
        colorbar = dict(title="Intensidade"),
        line = dict(width=0)             # Remove borda dos pontos para suavizar
    ),
    text = df_fake['valor'], # O que aparece ao passar o mouse
    name = 'Dados'
    ))

    fig1.update_geos(
        projection_type="orthographic", #ISSO TRANSFORMA EM GLOBO
        showcountries=True, 
        countrycolor="white",
        showocean=True, 
        oceancolor="#2156BB",
        showland=True, 
        landcolor="#18CB54",
        showlakes=False,
        projection_rotation=dict(lon=0, lat=0, roll=1) 
    )

    fig1.update_layout(
        height=600,
        margin={"r":0,"t":0,"l":0,"b":0},
        paper_bgcolor="rgba(0,0,0,0)", 
        plot_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(fig1, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Status dos Voos de Hoje")
        dfDelayed = dfToday['atraso_previsto'].value_counts().reset_index()
        dfDelayed.columns = ['Status_Code', 'Total']
        dfDelayed['Status_Nome'] = dfDelayed['Status_Code'].map({0: 'No Horário', 1: 'Atrasado'})
        fig2 = px.pie(
            dfDelayed,
            values='Total',
            names='Status_Nome',
            color='Status_Nome',
            color_discrete_map={'No Horário': '#2ECC71', 'Atrasado': '#EF553B'},
            hole=0.4 
        )

    st.plotly_chart(fig2, use_container_width=True)
    with col2:
        st.subheader("Aeroportos mais problematicos hoje")
        
        
except Exception as e:
    st.error(f"Erro no dashboad de dados de hoje: {str(e)}")

try:
    df = loadData()
    st.header("🔍 Filtros")
    
    availableDates = sorted(df['data_apenas'].unique())
    minDate = min(availableDates)
    maxDate = max(availableDates)
    
    st.subheader("📅 Período")      
    col1, col2 = st.columns(2)
    
    with col1:
        data_inicio = st.date_input(
            "Data Início",
            value= minDate,
            min_value= minDate,
            max_value= maxDate
        )
    
    with col2:
        data_fim = st.date_input(
            "Data Fim",
            value= maxDate,
            min_value= minDate,
            max_value= maxDate
        )
    with col1:
        st.subheader("Companhias mais usadas")
        topCompany = df['companhia_aerea'].value_counts().head(5)
        fig = px.bar(
            topCompany,
            x=topCompany.index,
            y=topCompany.values,
            labels={'x': 'Companhia Aérea', 'y': 'Número de Voos'},
            title='Top 5 Companhias Aéreas'
        )
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.subheader("Atrasos por Dia da Semana")
        delaysByDay = df.groupby('dia_da_semana')['atraso_previsto'].mean().reindex([0,1,2,3,4,5,6])
        fig2 = go.Figure(data=go.Bar(
            x=['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado'],
            y=delaysByDay.values,
            marker_color='indianred'
        ))
        fig2.update_layout(
            title='Média de Atrasos por Dia da Semana',
            xaxis_title='Dia da Semana',
            yaxis_title='Média de Atrasos'
        )
        st.plotly_chart(fig2, use_container_width=True)

    with col1:
        st.subheader("Linhas Aéreas e Atrasos")
        topDelayLines = df.groupby('linhas_aereas')['atraso_previsto'].mean().sort_values(ascending=False).head(5)
        fig3 = px.bar(
            topDelayLines,
            x=topDelayLines.index,
            y=topDelayLines.values,
            labels={'x': 'Linha Aérea', 'y': 'Média de Atrasos'},
            title='Top 5 Linhas Aéreas com Maior Média de Atrasos'
        )
        st.plotly_chart(fig3, use_container_width=True)
    with col2:
        st.subheader("Atrasos por Hora do Dia")
        delaysByHour = df.groupby('hora_partida')['atraso_previsto'].mean()
        fig4 = go.Figure(data=go.Scatter(
            x=delaysByHour.index,
            y=delaysByHour.values,
            mode='lines+markers',
            line=dict(color='royalblue')
        ))
        fig4.update_layout(
            title='Média de Atrasos por Hora do Dia',
            xaxis_title='Hora do Dia',
            yaxis_title='Média de Atrasos'
        )
        st.plotly_chart(fig4, use_container_width=True)
    
    company = ['Todas'] + sorted(df['companhia_aerea'].unique().tolist())

    st.subheader("🏢 Companhia Aérea")

    companySelected = st.selectbox(
        "🛫 Selecione a Companhia Aerea",
        company
    )
    if companySelected != 'Todas':
        dfCleaned= df[df['companhia_aerea'] == companySelected]
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Linhas mais Usadas")
        topLines = dfCleaned['linhas_aereas'].value_counts().head(5)
        fig5 = px.bar(
            topLines,
            x=topLines.index,
            y=topLines.values,
            labels={'x': 'Linha Aérea', 'y': 'Número de Voos'},
            title='Top 5 Linhas Aéreas'
        )
        st.plotly_chart(fig5, use_container_width=True)
    with col2:
        st.subheader("Atrasos por Linha Aérea")
        delaysByLine = dfCleaned.groupby('linhas_aereas')['atraso_previsto'].mean().sort_values(ascending=False).head(5)
        fig6 = px.bar(
            delaysByLine,
            x=delaysByLine.index,
            y=delaysByLine.values,
            labels={'x': 'Linha Aérea', 'y': 'Média de Atrasos'},
            title='Top 5 Linhas Aéreas com Maior Média de Atrasos'
        )
        st.plotly_chart(fig6, use_container_width=True)

    st.subheader("🛫 Filtro de Aeroporto")
    airportOptions = ['Todos'] + sorted(df['origem_aeroporto'].unique().tolist())
    airportFilter = st.selectbox(
        "🛫 Aeroporto de Origem",
        airportOptions
    )
    if airportFilter != 'Todos':
        dfCleanedArp = df[df['origem_aeroporto'] == airportFilter]
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top Destinos")
        topDestinations = df['destino_aeroporto'].value_counts().head
        fig7 = px.bar(
            topDestinations,
            x=topDestinations.index,
            y=topDestinations.values,
            labels={'x': 'Aeroporto de Destino', 'y': 'Número de Voos'},
            title='Top 5 Aeroportos de Destino'
        )
        st.plotly_chart(fig7, use_container_width=True)

    with col2:
        st.subheader("Top companhias do aerporto")
        topCompaniesAtAirport = df['companhia_aerea'].value_counts().head(5)
        fig8 = px.bar(
            topCompaniesAtAirport,
            x=topCompaniesAtAirport.index,
            y=topCompaniesAtAirport.values,
            labels={'x': 'Companhia Aérea', 'y': 'Número de Voos'},
            title='Top 5 Companhias Aéreas no Aeroporto'
        )
        st.plotly_chart(fig8, use_container_width=True)

    st.subheader("⏰ Filtro de Atrasos")
    
    delayOptions = ['Todos', 'Com Atraso', 'Sem Atraso']
    delayFilter = st.selectbox(
        "⏰ Atraso Previsto",
        delayOptions
    )
    
    dfCleaned = df[
        (df['data_apenas'] >= data_inicio) & 
        (df['data_apenas'] <= data_fim)
    ]
    
    if delayFilter == 'Com Atraso':
        dfCleaned = dfCleaned[dfCleaned['atraso_previsto'] == 1]
    elif delayFilter == 'Sem Atraso':
        dfCleaned = dfCleaned[dfCleaned['atraso_previsto'] == 0]
    col1, col2 = st.columns(2)

except Exception as e:
    st.error(f"Erro no dashboad de dados filtrados: {str(e)}")
