import streamlit as st
import requests 
import time
import pandas as pd
import json

CARRIER_MAP = {
    "American Airlines": "AA",
    "Delta Air Lines": "DL",
    "United Airlines": "UA",
    "Southwest Airlines": "WN",
    "JetBlue Airways": "B6",
    "Alaska Airlines": "AS",
    "Spirit Airlines": "NK",
    "Frontier Airlines": "F9",
    "Allegiant Air": "G4",
    "Hawaiian Airlines": "HA"
}

# Carregar dados de aeroportos do OpenFlights
@st.cache_data
def load_airports():
    url = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat"
    
    # Colunas do arquivo airports.dat
    columns = [
        'airport_id', 'name', 'city', 'country', 'iata', 'icao',
        'latitude', 'longitude', 'altitude', 'timezone', 'dst',
        'tz_database', 'type', 'source'
    ]
    
    try:
        df = pd.read_csv(url, header=None, names=columns, na_values='\\N')
        # Filtrar apenas aeroportos com código IATA válido
        df = df[df['iata'].notna() & (df['iata'] != '')]
        # Criar descrição formatada: "Nome - Cidade, País (IATA)"
        df['display_name'] = df['name'] + ' - ' + df['city'] + ', ' + df['country'] + ' (' + df['iata'] + ')'
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados de aeroportos: {e}")
        return pd.DataFrame()

def get_iata_from_selection(selection):
    """Extrai o código IATA da seleção do usuário"""
    if selection and '(' in selection and ')' in selection:
        # Extrai o código IATA entre parênteses
        return selection.split('(')[-1].split(')')[0]
    return None

def saveData(cia, ori, dest, date, dist):
    payload = {
    "companhia": cia,          
    "origem_aeroporto": ori,   
    "destino_aeroporto": dest,    
    "data_partida": date, 
    "distancia_km": dist    
    }
    return payload

# Carregar dados de aeroportos
airports_df = load_airports()

st.header("🛫 Nova Previsão de Atraso de Voo")
st.space(size="small")
tab1, tab2 = st.tabs(["Previsão Individual", "Previsão em Lote (CSV)"])

with tab1:
    with st.form("flight_delay_form"):
        col1, col2 = st.columns(2)
        with col1:
            # Usuário seleciona o nome completo da companhia
            cia_nome = st.selectbox("Selecione a Companhia Aérea", list(CARRIER_MAP.keys()))
            
            # Campo digitável para aeroporto de origem
            if not airports_df.empty:
                ori_selection = st.selectbox(
                    "Selecione o Aeroporto de Origem",
                    options=airports_df['display_name'].tolist(),
                )
            else:
                ori_selection = st.text_input("Código IATA do Aeroporto de Origem")
            
            # Campo digitável para aeroporto de destino
            if not airports_df.empty:
                dest_selection = st.selectbox(
                    "Selecione o Aeroporto de Destino",
                    options=airports_df['display_name'].tolist()              )
            else:
                dest_selection = st.text_input("Código IATA do Aeroporto de Destino")
                
        with col2:
            date = st.date_input("Selecione a Data do Voo")
            hour = st.time_input("Insira a Hora do Voo")
            dist = st.number_input("Insira a Distância do Voo (km)")
            
        submit_button = st.form_submit_button("Prever Atraso")
        
    if submit_button:
        cia_codigo = CARRIER_MAP[cia_nome]
        
        if not airports_df.empty:
            ori_codigo = get_iata_from_selection(ori_selection)
            dest_codigo = get_iata_from_selection(dest_selection)
        else:
            ori_codigo = ori_selection
            dest_codigo = dest_selection
        
        if not ori_codigo or not dest_codigo:
            st.error("Por favor, selecione aeroportos válidos.")
        else:
            payload = saveData(cia_codigo, ori_codigo, dest_codigo, f"{date}T{hour}", dist)

            try:
                url = "http://localhost:8000/api/v1/predict"
                response = requests.post(url, json=payload)
                with st.container():
                    if response.status_code == 200:
                        result = response.json()
                        
                        with st.spinner("Calculando Previsão de Atraso...", show_time=True):
                            time.sleep(2)
                            
                            st.badge("Success", icon=":material/check:", color="green")
                            st.write(f"**Companhia:** {cia_nome} ({cia_codigo})")
                            st.write(f"**Rota:** {ori_codigo} → {dest_codigo}")
                            st.write(f"**Probabilidade de Atraso:** {result['probability']*100:.2f}%")
                            st.write(f"**Mensagem:** {result['message']}")
                            st.write(f"**Risco Histórico do Aeroporto de Origem:** {result['internal_metrics']['historical_origin_risk']*100:.2f}%")
                            st.write(f"**Risco Histórico da Companhia:** {result['internal_metrics']['historical_carrier_risk']*100:.2f}%")
                            st.write(f"**Fonte do Dado:** {result['internal_metrics']['source']}")

                    elif response.status_code == 400:
                        st.error("Ocorreu um erro interno ao conectar com o back end.")
                    else:
                        st.error(f"Erro na resposta da API: Status {response.status_code}")

            except Exception as e:
                st.error("Erro na requisição para a API de Previsão.")
                with st.expander("Ver detalhes técnicos do erro"):
                    st.write(e)
            
with tab2:
    st.subheader("📊 Upload de Arquivo CSV")
    st.info("O arquivo CSV deve conter as colunas: companhia, origem_aeroporto, destino_aeroporto, data_partida, distancia_km")
    
    with st.expander("Ver exemplo de formato CSV"):
        exemplo_df = pd.DataFrame({
            'companhia': ['AA', 'DL'],
            'origem_aeroporto': ['JFK', 'LAX'],
            'destino_aeroporto': ['MIA', 'SFO'],
            'data_partida': ['2024-03-15T10:30', '2024-03-16T14:20'],
            'distancia_km': [1759, 543]
        })
        st.dataframe(exemplo_df)
    
    uploaded_file = st.file_uploader("Escolha um arquivo CSV", type=['csv'])
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.success(f"✅ Arquivo carregado com sucesso! {len(df)} registros encontrados.")
            st.dataframe(df.head())
            
            if st.button("Processar Previsões em Lote"):
                url = "http://localhost:8000/api/v1/predict"
                results = []
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for idx, row in df.iterrows():
                    status_text.text(f"Processando voo {idx + 1} de {len(df)}...")
                    
                    payload = {
                        "companhia": row['companhia'],
                        "origem_aeroporto": row['origem_aeroporto'],
                        "destino_aeroporto": row['destino_aeroporto'],
                        "data_partida": row['data_partida'],
                        "distancia_km": float(row['distancia_km'])
                    }
                    
                    try:
                        response = requests.post(url, json=payload)
                        if response.status_code == 200:
                            result = response.json()
                            results.append({
                                'Voo': idx + 1,
                                'Companhia': row['companhia'],
                                'Origem': row['origem_aeroporto'],
                                'Destino': row['destino_aeroporto'],
                                'Probabilidade (%)': f"{result['probability']*100:.2f}",
                                'Status': 'Sucesso',
                                'Resposta Completa': json.dumps(result)
                            })
                        else:
                            results.append({
                                'Voo': idx + 1,
                                'Companhia': row['companhia'],
                                'Origem': row['origem_aeroporto'],
                                'Destino': row['destino_aeroporto'],
                                'Probabilidade (%)': 'N/A',
                                'Status': f'Erro {response.status_code}',
                                'Resposta Completa': response.text
                            })
                    except Exception as e:
                        results.append({
                            'Voo': idx + 1,
                            'Companhia': row['companhia'],
                            'Origem': row['origem_aeroporto'],
                            'Destino': row['destino_aeroporto'],
                            'Probabilidade (%)': 'N/A',
                            'Status': 'Erro de conexão',
                            'Resposta Completa': str(e)
                        })
                    
                    progress_bar.progress((idx + 1) / len(df))
                
                status_text.text("✅ Processamento concluído!")
                
                results_df = pd.DataFrame(results)
                st.subheader("📈 Resultados das Previsões")
                st.dataframe(results_df[['Voo', 'Companhia', 'Origem', 'Destino', 'Probabilidade (%)', 'Status']])
                
                csv_results = results_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Resultados (CSV)",
                    data=csv_results,
                    file_name="previsoes_voos.csv",
                    mime="text/csv"
                )
                
                with st.expander("🔍 Ver Retornos Completos da API"):
                    for result in results:
                        st.write(f"**Voo {result['Voo']}:**")
                        try:
                            st.json(json.loads(result['Resposta Completa']))
                        except:
                            st.code(result['Resposta Completa'])
                        st.divider()
                        
        except Exception as e:
            st.error(f"Erro ao processar arquivo CSV: {str(e)}")
            with st.expander("Ver detalhes técnicos do erro"):
                st.write(e)
    
     
