import streamlit as st

# Hero Section
st.markdown(
    """
    <div style='text-align: center; padding: 2rem 0;'>
        <h1 style='font-size: 2.5em; margin-bottom: 0;'>📖 Projeto de Análise de Dados de Voos</h1>
        <p style='font-size: 1.2em; color: #888; margin-top: 0.5rem;'>
            Um projeto educacional sobre análise de dados, machine learning e visualização
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

# Seção: Origem dos dados
st.header("🌐 Fonte de Dados")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown(
        """
        ### Dados Públicos Governamentais
        
        Este projeto utiliza **dados públicos oficiais** do **Bureau of Transportation Statistics (BTS)**,
        uma agência do Departamento de Transportes dos EUA que mantém bases de dados sobre aviação civil.
        
        #### 🔬 Processo de Tratamento:
        """
    )

    tab1, tab2, tab3 = st.tabs(["🔍 Validação", "🧹 Limpeza", "⚖️ Normalização"])

    with tab1:
        st.markdown("""
        **Verificação de consistência**
        - Checagem de tipos de dados
        - Identificação de valores ausentes
        - Validação de datas
        - Detecção de duplicatas
        """)

    with tab2:
        st.markdown("""
        **Tratamento de problemas**
        - Remoção de duplicados
        - Preenchimento de nulos
        - Correção de inconsistências
        - Filtragem de outliers
        """)

    with tab3:
        st.markdown("""
        **Padronização**
        - Formatos de data uniformes
        - Códigos de aeroporto padronizados
        - Conversão de fusos horários
        - Escalas normalizadas
        """)

with col2:
    st.info(
        "🔒 **Dados Públicos**\n\n✓ Sem informações pessoais\n✓ Fonte governamental\n✓ Uso educacional"
    )

    with st.expander("📊 Ver Fonte"):
        st.markdown("""
        **Bureau of Transportation Statistics**
        
        [Acessar base de dados →](https://www.transtats.bts.gov/DL_SelectFields.aspx?gnoyr_VQ=FGK&QO_fu146_anzr=b0-gvzr)
        """)

st.divider()

# Seção: Jornada do dado
st.header("🔄 Pipeline de Processamento")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("1️⃣\n\n**COLETA**\n\nExtração de Dados", key="btn_coleta", use_container_width=True, help="Clique para ver detalhes"):
        if st.session_state.get('show_coleta', False):
            st.session_state.show_coleta = False
        else:
            st.session_state.show_coleta = True
            st.session_state.show_processamento = False
    
with col2:
    if st.button("2️⃣\n\n**PROCESSAMENTO**\n\nTransformação", key="btn_processamento", use_container_width=True, help="Clique para ver detalhes"):
        if st.session_state.get('show_processamento', False):
            st.session_state.show_processamento = False
        else:
            st.session_state.show_processamento = True
            st.session_state.show_coleta = False

with col3:
    if st.button("3️⃣\n\n**VISUALIZAÇÃO**\n\nDashboard", key="btn_visualizacao", use_container_width=True, help="Clique para ir ao Dashboard"):
        st.switch_page("pages/Dashboard.py")

# Mostrar detalhes se botões foram clicados
if st.session_state.get('show_coleta', False):
    st.markdown("#### 📂 Detalhes da Coleta de Dados")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("""
        **Fonte de Dados:**
        - Bureau of Transportation Statistics
        - Dados públicos oficiais
        - Formato: SQL estruturado
        """)
    with col2:
        st.markdown("""
        **Processo de Coleta:**
        - Importação via arquivo SQL
        - Carregamento em SQLite (memória)
        - Volume: 1000+ registros de voos
        - Campos: data, origem, destino, companhia, atraso
        """)

if st.session_state.get('show_processamento', False):
    st.markdown("#### ⚙️ Detalhes do Processamento")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **Limpeza de Dados:**
        - Remoção de duplicados
        - Tratamento de valores nulos
        - Validação de datas
        - Filtro de outliers
        """)
    with col2:
        st.markdown("""
        **Feature Engineering:**
        - Extração de dia da semana
        - Criação de rotas (origem → destino)
        - Separação de data e hora
        - Normalização de códigos
        """)

st.divider()

# Seção: Ética e boas práticas
st.header("🛡️ Boas Práticas e Ética")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### ✅ Práticas Aplicadas")

    with st.expander("✅ Uso Responsável", expanded=True):
        st.markdown("""
        - Dados públicos e abertos apenas
        - Respeito às diretrizes da fonte
        - Documentação transparente
        - Código versionado
        """)

    with st.expander("✅ Dados Seguros"):
        st.markdown("""
        - Dados já anonimizados
        - Sem informações pessoais
        - Agregações estatísticas
        - Fonte confiável
        """)

    with st.expander("✅ Transparência"):
        st.markdown("""
        - Código-fonte disponível
        - Metodologia documentada
        - Processo explicável
        - Fonte citada
        """)

with col2:
    st.markdown("### ❌ O Que Evitamos")

    with st.expander("❌ Uso Comercial", expanded=True):
        st.markdown("""
        - Projeto educacional apenas
        - Dados não comercializados
        - Uso para aprendizado
        """)

    with st.expander("❌ Coleta Desnecessária"):
        st.markdown("""
        - Sem dados pessoais
        - Sem rastreamento
        - Dados públicos apenas
        """)

    with st.expander("❌ Análises Enviesadas"):
        st.markdown("""
        - Atenção a vieses
        - Limitações documentadas
        - Análise crítica
        """)

st.divider()

# Seção: O que o projeto faz
st.header("💻 Funcionalidades do Projeto")

st.markdown("""
Este projeto demonstra habilidades práticas em análise de dados aplicadas a um dataset real:
""")

tab1, tab2, tab3 = st.tabs(
    ["📊 Análise Exploratória", "🔮 Modelo Preditivo", "📈 Dashboard"]
)

with tab1:
    st.markdown("""
    ### Exploração de Dados
    
    **O que fazemos:**
    - Carregamento e limpeza de dados
    - Estatísticas descritivas
    - Identificação de padrões temporais
    - Análise de rotas e companhias
    
    **Tecnologias:**
    - ✅ Pandas para manipulação
    - ✅ SQLite para consultas
    - ✅ Análise exploratória (EDA)
    """)

with tab2:
    st.markdown("""
    ### Previsão de Atrasos
    
    **O que fazemos:**
    - Feature engineering
    - Treinamento de modelo
    - Avaliação de métricas
    - Previsões de atrasos
    
    **Tecnologias:**
    - ✅ Scikit-learn
    - ✅ Machine Learning
    - ✅ Métricas de avaliação
    """)

with tab3:
    st.markdown("""
    ### Visualização Interativa
    
    **O que fazemos:**
    - Gráficos com Plotly
    - Dashboard com Streamlit
    - Filtros interativos
    - Visualizações responsivas
    
    **Tecnologias:**
    - ✅ Plotly Express
    - ✅ Streamlit
    - ✅ Design responsivo
    """)

st.divider()

# Aprendizados
st.header("🎓 Aprendizados do Bootcamp")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="💼 Habilidades", value="Data Science", help="Análise, visualização e ML"
    )

with col2:
    st.metric(label="🐍 Linguagem", value="Python", help="Pandas, Plotly, Streamlit")

with col3:
    st.metric(
        label="📚 Conceitos", value="Completos", help="Do dado bruto ao dashboard"
    )

st.markdown("""
### Principais aprendizados aplicados:

- **Análise de Dados:** Limpeza, transformação e exploração de dados reais
- **Visualização:** Criação de dashboards interativos e gráficos informativos
- **Machine Learning:** Implementação de modelos preditivos básicos
- **Web Development:** Deploy de aplicação com Streamlit
- **Boas Práticas:** Código limpo, documentação e versionamento
""")

st.divider()

# Call to action
st.header("🚀 Quer explorar o código?")

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown(
        """
    <div style='text-align: center; padding: 1rem; background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%); border-radius: 10px;'>
        <p style='font-size: 1.1em;'>
        Este é um projeto educacional desenvolvido em um bootcamp de Data Science.
        Todo o código está disponível para estudo e aprendizado.
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    with col_a:
        if st.button("💻 Ver Código", use_container_width=True, type="primary"):
            st.info("📂 Repositório: github.com/seu-usuario/dashboard-streamlit")

    with col_b:
        if st.button("📖 Documentação", use_container_width=True):
            st.info("📚 Veja o README.md do projeto")

st.markdown("---")

# Footer
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**🎓 Tecnologias**")
    st.caption("• Python & Pandas\n• Plotly & Streamlit\n• SQLite & SQL")

with col2:
    st.markdown("**📊 Dados**")
    st.caption("• Fonte: BTS (Gov. EUA)\n• Dados públicos\n• Uso educacional")

with col3:
    st.markdown("**💡 Conceitos**")
    st.caption("• Análise de dados\n• Machine Learning\n• Data Visualization")

st.caption(
    "📚 Projeto educacional desenvolvido para fins de aprendizado. Dados públicos do Bureau of Transportation Statistics."
)
