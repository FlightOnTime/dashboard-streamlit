import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

@st.cache_data
def carregar_aeroportos_openflights():
    """Carrega dados de aeroportos do OpenFlights via GitHub"""
    url = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat"
    
    # Colunas do arquivo airports.dat
    colunas = [
        'airport_id', 'name', 'city', 'country', 'iata', 'icao',
        'latitude', 'longitude', 'altitude', 'timezone', 'dst',
        'tz_database', 'type', 'source'
    ]
    
    try:
        df_airports = pd.read_csv(url, header=None, names=colunas, na_values='\\N')
        
        # Filtrar apenas aeroportos com código IATA válido
        df_airports = df_airports[df_airports['iata'].notna()]
        
        # Criar dicionário para lookup rápido por código IATA
        airport_dict = {}
        for _, row in df_airports.iterrows():
            airport_dict[row['iata']] = {
                'lat': row['latitude'],
                'lon': row['longitude'],
                'nome': f"{row['name']} - {row['city']}, {row['country']}"
            }
        
        return airport_dict
    except Exception as e:
        st.error(f"Erro ao carregar dados do OpenFlights: {str(e)}")
        return {}
    
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
    
    # Carregar dados de aeroportos do OpenFlights
    aeroportos_coords = carregar_aeroportos_openflights()
    
    # Adicionar coordenadas de origem
    df['origem_latitude'] = df['origem_aeroporto'].map(lambda x: aeroportos_coords.get(x, {}).get('lat', None))
    df['origem_longitude'] = df['origem_aeroporto'].map(lambda x: aeroportos_coords.get(x, {}).get('lon', None))
    df['origem_nome_completo'] = df['origem_aeroporto'].map(lambda x: aeroportos_coords.get(x, {}).get('nome', x))
    
    # Adicionar coordenadas de destino
    df['destino_latitude'] = df['destino_aeroporto'].map(lambda x: aeroportos_coords.get(x, {}).get('lat', None))
    df['destino_longitude'] = df['destino_aeroporto'].map(lambda x: aeroportos_coords.get(x, {}).get('lon', None))
    df['destino_nome_completo'] = df['destino_aeroporto'].map(lambda x: aeroportos_coords.get(x, {}).get('nome', x))
    
    return df

try:
    dfToday = loadDataToday()
    col1, col2 = st.columns([0.85, 0.15])
    
    with col1:
        st.header("📊 Dashboard de Análise de Voos de Hoje")
    with col2:
        st.button("🔄 Atualizar Dados") 
    
    # Carregar dados completos para ter acesso a todas as coordenadas
    df_completo = loadData()
    if dfToday.empty:
        raise ValueError("Não há dados de voos para hoje")
    
    
    # Criar DataFrame com coordenadas únicas dos aeroportos
    aeroportos_origem = df_completo[['origem_aeroporto', 'origem_latitude', 'origem_longitude', 'origem_nome_completo']].copy()
    aeroportos_origem.columns = ['aeroporto', 'latitude', 'longitude', 'nome_completo']
    
    aeroportos_destino = df_completo[['destino_aeroporto', 'destino_latitude', 'destino_longitude', 'destino_nome_completo']].copy()
    aeroportos_destino.columns = ['aeroporto', 'latitude', 'longitude', 'nome_completo']
    
    # Combinar e remover duplicatas
    df_aeroportos = pd.concat([aeroportos_origem, aeroportos_destino]).drop_duplicates(subset=['aeroporto'])
    
    # Remover aeroportos sem coordenadas
    df_aeroportos = df_aeroportos.dropna(subset=['latitude', 'longitude'])
    
    # Contar número de voos por aeroporto (como intensidade)
    voos_origem = dfToday['origem_aeroporto'].value_counts()
    voos_destino = dfToday['destino_aeroporto'].value_counts()
    total_voos = voos_origem.add(voos_destino, fill_value=0)
    
    df_aeroportos['total_voos'] = df_aeroportos['aeroporto'].map(total_voos).fillna(0)
    
    # Criar o mapa
    fig1 = go.Figure()

    # Adiciona a camada de aeroportos
    fig1.add_trace(go.Scattergeo(
        lon = df_aeroportos['longitude'],
        lat = df_aeroportos['latitude'],
        mode = 'markers',
        marker = dict(
            size = 12 + df_aeroportos['total_voos'] * 2,
            color = df_aeroportos['total_voos'],
            colorscale = 'Inferno',
            cmin = 0,
            cmax = df_aeroportos['total_voos'].max() if len(df_aeroportos) > 0 else 1,
            opacity = 0.8,
            colorbar = dict(title="Nº de Voos"),
            line = dict(width=1, color='white')
        ),
        text = df_aeroportos['nome_completo'] + '<br>Código: ' + df_aeroportos['aeroporto'] + '<br>Voos: ' + df_aeroportos['total_voos'].astype(int).astype(str),
        hoverinfo = 'text',
        name = 'Aeroportos'
    ))

    fig1.update_geos(
        projection_type="orthographic",
        showcountries=True, 
        countrycolor="white",
        showocean=True, 
        oceancolor="#2156BB",
        showland=True, 
        landcolor="#18CB54",
        showlakes=False,
        projection_rotation=dict(lon=-47.9, lat=-15.8, roll=0),
        center=dict(lon=-47.9, lat=-15.8)
    )

    fig1.update_layout(
        height=600,
        margin={"r":0,"t":0,"l":0,"b":0},
        paper_bgcolor="rgba(0,0,0,0)", 
        plot_bgcolor="rgba(0,0,0,0)"
    )
    
    st.plotly_chart(fig1, use_container_width=True)
    
    # Mostrar informações sobre aeroportos sem coordenadas (se houver)
    aeroportos_sem_coords = df_completo[df_completo['origem_latitude'].isna()]['origem_aeroporto'].unique()
    if len(aeroportos_sem_coords) > 0:
        st.warning(f"⚠️ Aeroportos sem coordenadas no OpenFlights: {', '.join(aeroportos_sem_coords)}")
    
    # Mostrar estatísticas
    st.info(f"✅ Total de aeroportos identificados: {len(df_aeroportos)}")
    

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("✈️ Atrasados vs Pontuais")
        dfDelayed = dfToday['atraso_previsto'].value_counts().reset_index()
        dfDelayed.columns = ['Status_Code', 'Total']
        dfDelayed['Status_Nome'] = dfDelayed['Status_Code'].map({0: 'Pontual', 1: 'Atrasado'})
        fig2 = px.pie(
            dfDelayed,
            values='Total',
            names='Status_Nome',
            color='Status_Nome',
            color_discrete_map={'Pontual': '#2ECC71', 'Atrasado': '#EF553B'},
            hole=0.4 
        )
        fig2.update_layout(
            title='Distribuição de Status dos Voos'
        )
        st.plotly_chart(fig2, use_container_width=True)
        
    with col2:
        st.subheader("🚨 Aeroportos Mais Problemáticos")
        airport_delays = dfToday.groupby('origem_aeroporto').agg({
            'atraso_previsto': ['sum', 'count', 'mean']
        }).reset_index()
        airport_delays.columns = ['Aeroporto', 'Total_Atrasos', 'Total_Voos', 'Taxa_Atraso']
        airport_delays = airport_delays.sort_values('Taxa_Atraso', ascending=False).head(5)
        
        fig3 = px.bar(
            airport_delays,
            x='Aeroporto',
            y='Taxa_Atraso',
            color='Taxa_Atraso',
            color_continuous_scale='Reds',
            labels={'Taxa_Atraso': 'Taxa de Atraso (%)'},
            text='Taxa_Atraso'
        )
        fig3.update_traces(texttemplate='%{text:.1%}', textposition='outside')
        fig3.update_layout(
            title='Top 5 Aeroportos com Maior Taxa de Atraso',
            showlegend=False
        )
        st.plotly_chart(fig3, use_container_width=True)
    
    st.subheader("⏰ Evolução de Atrasos por Hora")
    hourly_data = dfToday.groupby('hora_partida').agg({
        'atraso_previsto': ['sum', 'count']
    }).reset_index()
    hourly_data.columns = ['Hora', 'Atrasados', 'Total_Voos']
    hourly_data['Pontuais'] = hourly_data['Total_Voos'] - hourly_data['Atrasados']
    hourly_data['Taxa_Atraso'] = (hourly_data['Atrasados'] / hourly_data['Total_Voos']) * 100
    
    fig4 = go.Figure()
    
    fig4.add_trace(go.Bar(
        x=hourly_data['Hora'],
        y=hourly_data['Pontuais'],
        name='Pontuais',
        marker_color='#2ECC71'
    ))
    
    fig4.add_trace(go.Bar(
        x=hourly_data['Hora'],
        y=hourly_data['Atrasados'],
        name='Atrasados',
        marker_color='#EF553B'
    ))
    
    fig4.add_trace(go.Scatter(
        x=hourly_data['Hora'],
        y=hourly_data['Taxa_Atraso'],
        name='Taxa de Atraso (%)',
        yaxis='y2',
        mode='lines+markers',
        marker=dict(size=8, color='#F39C12'),
        line=dict(width=3, color='#F39C12')
    ))
    
    fig4.update_layout(
        title='Evolução de Voos por Hora do Dia',
        xaxis_title='Hora do Dia',
        yaxis_title='Número de Voos',
        yaxis2=dict(
            title='Taxa de Atraso (%)',
            overlaying='y',
            side='right'
        ),
        barmode='stack',
        hovermode='x unified',
        height=500
    )
    
    st.plotly_chart(fig4, use_container_width=True)
      
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
    
    if df.empty:
        raise ValueError("Não há dados de voos para as datas selecionadas")
    
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
    df = df[
        (df['data_apenas'] >= data_inicio) & 
        (df['data_apenas'] <= data_fim)
    ]
    
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
        delaysByDay = df.groupby('dia_da_semana')['atraso_previsto'].sum().reindex([0,1,2,3,4,5,6])
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
        topDelayLines = df.groupby('linhas_aereas')['atraso_previsto'].sum().sort_values(ascending=False).head(5)
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
        delaysByHour = df.groupby('hora_partida')['atraso_previsto'].sum()
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
    
    company =  sorted(df['companhia_aerea'].unique().tolist())

    st.subheader("🏢 Companhia Aérea")

    companySelected = st.selectbox(
        "🛫 Selecione a Companhia Aerea",
        company
    )
    
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

    
    
    
    with col1:    
        csv_filtered_date = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Dados Filtrados por Data (CSV)",
            data=csv_filtered_date,
            file_name=f"voos_filtrados_{data_inicio}_a_{data_fim}.csv",
            mime="text/csv",
            key="download_filtered_date"
        )
    with col2:
        csv_today = dfToday.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Dados de Hoje (CSV)",
            data=csv_today,
            file_name=f"voos_hoje_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            key="download_today"
        )
except NameError:
    pass
except Exception as e:
    st.error(f"Erro no dashboad de dados filtrados: {str(e)}")
