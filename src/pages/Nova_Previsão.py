import streamlit as st
import requests 
import time
import pandas as pd
import json

CARRIER_MAP = {
    # Backend valida pelo NOME (deve conter: AMERICAN, DELTA, UNITED, SOUTHWEST, LATAM, GOL, AZUL)
    "American Airlines": "American Airlines",
    "Delta Air Lines": "Delta Air Lines",
    "United Airlines": "United Airlines",
    "Southwest Airlines": "Southwest Airlines",
    "LATAM Airlines": "LATAM Airlines",
    "GOL Linhas Aéreas": "GOL Linhas Aéreas",
    "Azul Linhas Aéreas": "Azul Linhas Aéreas"
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
st.write("")  # Adiciona um pequeno espaço vertical
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
            # Garante formato ISO-8601 completo (incluindo segundos)
            # st.time_input retorna datetime.time
            datetime_str = f"{date}T{hour.strftime('%H:%M:%S')}"
            
            payload = saveData(cia_codigo, ori_codigo, dest_codigo, datetime_str, dist)

            try:
                # URL CORRIGIDA e VERIFICADA (Endpoint correto do Controller)
                url = "http://localhost:8080/api/v1/predict"
                
                response = requests.post(url, json=payload)
                
                with st.container():
                    if response.status_code == 200:
                        result = response.json()
                        
                        with st.spinner("Calculando Previsão de Atraso...", show_time=True):
                            time.sleep(1) # Visual effect
                            
                            # DEBUG: Mostra o JSON bruto para garantir que estamos vendo tudo
                            # st.json(result) 

                            st.badge("Success", icon=":material/check:", color="green")
                            st.write(f"**Companhia:** {cia_nome} ({cia_codigo})")
                            st.write(f"**Rota:** {ori_codigo} → {dest_codigo}")
                            st.write(f"**Probabilidade de Atraso:** {result['probabilidade']*100:.2f}%")
                            st.write(f"**Mensagem:** {result['mensagem']}")
                            
                            # Verificação de segurança para métricas internas
                            metrics = result.get('metricas_internas', {})
                            if metrics:
                                st.write(f"**Risco Histórico do Aeroporto de Origem:** {metrics.get('risco_historico_origem', 0)*100:.2f}%")
                                st.write(f"**Risco Histórico da Companhia:** {metrics.get('risco_historico_companhia', 0)*100:.2f}%")
                                st.write(f"**Fonte do Dado:** {metrics.get('fonte', 'N/A')}")

                    elif response.status_code == 400:
                        st.error("Erro de Validação dos Dados (400 Bad Request)")
                        with st.expander("Detalhes do Erro da API"):
                            # Tenta mostrar JSON se possível, senão texto puro
                            try:
                                st.json(response.json())
                            except:
                                st.text(response.text)
                    else:
                        st.error(f"Erro na resposta da API: Status {response.status_code}")
                        st.text(response.text)

            except Exception as e:
                st.error(f"Erro na requisição para a API de Previsão: {url}")
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
            'data_partida': ['2024-03-15T10:30:00', '2024-03-16T14:20:00'],
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
                # URL CORRIGIDA PARA O ENDPOINT DE BATCH
                url = "http://localhost:8080/api/v1/predict/batch"
                
                batch_payload = []
                rows_mapping = [] # Para mapear a resposta de volta para a linha original
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                status_text.text("Preparando dados...")
                
                # Prepara o payload em lote
                for idx, row in df.iterrows():
                    # Garante formato ISO: Se faltar segundos, adiciona.
                    d_str = str(row['data_partida'])
                    if len(d_str) == 16: # Ex: 2024-03-15T10:30
                         d_str += ":00"
                    
                    payload = {
                        "companhia": row['companhia'],
                        "origem_aeroporto": row['origem_aeroporto'],
                        "destino_aeroporto": row['destino_aeroporto'],
                        "data_partida": d_str,
                        "distancia_km": float(row['distancia_km'])
                    }
                    batch_payload.append(payload)
                    rows_mapping.append(row)
                
                status_text.text(f"Enviando {len(batch_payload)} voos para análise...")
                progress_bar.progress(50)
                
                results = []
                
                try:
                    # Envia tudo de uma vez
                    response = requests.post(url, json=batch_payload)
                    
                    progress_bar.progress(90)
                    
                    if response.status_code == 200:
                        responses_data = response.json()
                        
                        # Processa as respostas
                        for idx, res_item in enumerate(responses_data):
                            row = rows_mapping[idx]
                            results.append({
                                'Voo': idx + 1,
                                'Companhia': row['companhia'],
                                'Origem': row['origem_aeroporto'],
                                'Destino': row['destino_aeroporto'],
                                'Probabilidade (%)': f"{res_item['probabilidade']*100:.2f}",
                                'Status': 'Sucesso',
                                'Resposta Completa': json.dumps(res_item)
                            })
                            
                        status_text.text("✅ Processamento concluído!")
                        progress_bar.progress(100)
                        
                    elif response.status_code == 400:
                         st.error("Erro de Validação no Lote (400). Verifique o formato dos dados.")
                         try:
                             st.json(response.json())
                         except:
                             st.text(response.text)
                         status_text.text("Falha no processamento.")
                    else:
                        st.error(f"Erro no processamento em lote: {response.status_code}")
                        st.text(response.text)
                        
                except Exception as e:
                    st.error(f"Erro de conexão: {str(e)}")
                
                if results:
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
