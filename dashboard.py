import pandas as pd
import streamlit as st
import plotly.express as px
import textwrap

st.set_page_config(page_title="Produção Individual", layout="wide")
st.title("Produção individual")

url = "https://docs.google.com/spreadsheets/d/1bYAQiCoNwgCgJBP8XpZuoafGN6uaEI5AfYIC-g68hYA/gviz/tq?tqx=out:csv"
df = pd.read_csv(url, on_bad_lines='skip')

colunas_periodos_ranking = [col for col in df.columns if col.count("_") == 2]

ordem_periodos = [
    "JAN_FEV", "FEV_MAR", "MAR_ABR", "ABR_MAI", "MAI_JUN", "JUN_JUL",
    "JUL_AGO", "AGO_SET", "SET_OUT", "OUT_NOV", "NOV_DEZ", "DEZ_JAN"
]

periodo_3meses = [
    "AGO_SET", "SET_OUT","OUT_NOV"
]

df_3meses = df_3meses = df[df["NOME 3 MESES"].notna() & (df["NOME 3 MESES"] != "")]


df_melt_3meses = df_3meses.melt(id_vars=["TÉCNICO", "SUPERVISOR"], value_vars=colunas_periodos_ranking, var_name="PERIODO_TIPO", value_name="VALOR")
df_melt_3meses[["PERIODO", "TIPO"]] = df_melt_3meses["PERIODO_TIPO"].str.rsplit("_", n=1, expand=True)
df_melt_3meses.drop(columns="PERIODO_TIPO", inplace=True)

nome_3meses = df_melt_3meses["TÉCNICO"].unique()

st.markdown("""
    <style>
    div[data-testid="stMarkdownContainer"] p {
        font-size: 20px;  
    }
    </style>
""", unsafe_allow_html=True)

ck_3meses = st.checkbox("Visualizar Técnicos que não bateram meta")


if ck_3meses:

    st.markdown(
                        f"<h2 style='font-size:30px;text-align:center; margin-top:30px; color: #a0aec0;' >Técnicos que não bateram meta nos últimos 3 períodos</h2>",
                        unsafe_allow_html=True
                )


    nome_escolhido_3meses = st.selectbox("Selecione um técnico", nome_3meses)

    df_filtrado = df_melt_3meses[df_melt_3meses["TÉCNICO"] == nome_escolhido_3meses]

    cols = st.columns(3)

    for i, periodo in enumerate(periodo_3meses):
        with cols[i]:
            # Filtra os dados do período atual
            df_periodo = df_filtrado[df_filtrado["PERIODO"] == periodo]
            

            # Obtém os valores de cada tipo
            meta = df_periodo.loc[df_periodo["TIPO"] == "MT", "VALOR"].iloc[0]
            faturado = df_periodo.loc[df_periodo["TIPO"] == "FAT", "VALOR"].iloc[0]
            atingimento = df_periodo.loc[df_periodo["TIPO"] == "ATG", "VALOR"].iloc[0]
            supervisor = df_periodo["SUPERVISOR"].iloc[0]
            

            # Exibe o card
            st.markdown(f"""
            <div style='background-color: rgba(255, 255, 255, 0.05); padding:20px; border-radius:15px; text-align:center; box-shadow: 0 4px 12px rgba(100,100,100,0.2); border: solid 1px rgba(255,255,255,0.2); margin: 40px 20px; '>
                <label style='font-size:22px; color:#a0aec0; margin-bottom:25px;'>{periodo}</label>
                <p style='font-size: 20px; color:#38a169;'><b>Meta:</b> {meta}</p>
                <p style='font-size: 20px; color: #e53e3e;'><b>Faturado:</b> {faturado}</p>
                <p style='font-size: 20px; color:#3182ce;'><b>Atingimento:</b> {atingimento}</p>
                 <p style='font-size:18px; color:#a0aec0;'><b>Supervisor: {supervisor}</b></p>
            </div>
            """, unsafe_allow_html=True)




df_melt_ranking = df.melt(id_vars=["TÉCNICO"], value_vars=colunas_periodos_ranking, var_name="PERIODO_TIPO", value_name="VALOR")
df_melt_ranking[["PERIODO", "TIPO"]] = df_melt_ranking["PERIODO_TIPO"].str.rsplit("_", n=1, expand=True)
df_melt_ranking.drop(columns="PERIODO_TIPO", inplace=True)

periodos_ranking = df_melt_ranking["PERIODO"].unique()[::-1]
periodos_unicos_ranking = [p for p in ordem_periodos if p in df_melt_ranking["PERIODO"].unique()]
periodos_unicos_ranking.reverse()

ranking_ck = st.checkbox("Visualizar Ranking")

if ranking_ck:

    st.markdown(
                    f"<h2 style='font-size:30px;text-align:center; margin-top:30px; color: #a0aec0;' >Ranking por Período</h2>",
                    unsafe_allow_html=True
            )

    periodo_escolhido_ranking = st.selectbox("Selecione um período", periodos_unicos_ranking)

    

    df_melt_ranking = df_melt_ranking[df_melt_ranking["PERIODO"] == periodo_escolhido_ranking]

    df_atg_ranking = df_melt_ranking[df_melt_ranking["TIPO"] == "ATG"].copy()

    df_atg_ranking["VALOR"] = (
        df_atg_ranking["VALOR"]
        .astype(str)
        .str.replace("%", "", regex=False)
        .str.replace(",", ".", regex=False)
        .str.strip()
    )

    df_atg_ranking["VALOR"] = pd.to_numeric(df_atg_ranking["VALOR"], errors="coerce")
    df_atg_ranking = df_atg_ranking.dropna(subset=["VALOR"])
    df_atg_ranking = df_atg_ranking[df_atg_ranking["VALOR"] != 0]


    # Calcula média de atingimento por técnico
    ranking = df_atg_ranking.groupby("TÉCNICO", as_index=False)["VALOR"].mean().dropna()



    # Top 10 e bottom 10
    melhores = ranking.sort_values("VALOR", ascending=False).head(10)
    piores = ranking.sort_values("VALOR", ascending=True).head(10)




    st.markdown("""
    <style>
    .rank-container {
        display: flex;
        justify-content: space-around;
        gap: 40px;
        margin-bottom: 40px;
        
    }
    .rank-card {
        width: 45%;
        background-color: #0e1117;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 10px rgba(255,255,255,0.1);
    }
    .rank-card h3 {
        text-align: center;
        color: #4fd1c5;
        margin-bottom: 15px;
    }
    .rank-list {
        list-style: none;
        padding-left: 0;
        color: white;
        font-size: 16px;
    }
    .rank-list li {
        display: flex;
        justify-content: space-between;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        padding: 6px 0;
    }
    .rank-list li span:first-child {
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

    # HTML dos rankings
    melhores_html = "".join([
        f"<li><span>{row['TÉCNICO']}</span><span>{row['VALOR']:.1f}%</span></li>"
        for _, row in melhores.iterrows()
    ])
    piores_html = "".join([
        f"<li><span>{row['TÉCNICO']}</span><span>{row['VALOR']:.1f}%</span></li>"
        for _, row in piores.iterrows()
    ])

    html = textwrap.dedent(f"""
    <div class="rank-container">
        <div class="rank-card">
            <h3>🏆 Top 10 Técnicos</h3>
            <ul class="rank-list">{melhores_html}</ul>
        </div>
        <div class="rank-card">
            <h3>⚠️ 10 Piores Técnicos</h3>
            <ul class="rank-list">{piores_html}</ul>
        </div>
    </div>
    """)

    st.markdown(html, unsafe_allow_html=True)


tecnicos = df["TÉCNICO"]

ck_valores = st.checkbox("Visualizar Valores Individuais")

if ck_valores:

   

    st.markdown(
                        f"<h2 style='font-size:30px;text-align:center;margin-top:30px; color: #a0aec0;' >Valores Individuais de todos os técnicos</h2>",
                        unsafe_allow_html=True
                )

    
    tecnico_escolhido = st.selectbox("Selecione o técnico", tecnicos)
    

    df = df[df["TÉCNICO"] == tecnico_escolhido].copy()

    colunas_periodos = [col for col in df.columns if col.count("_") == 2]


    df_melt = df.melt(id_vars=["TÉCNICO"], value_vars=colunas_periodos, var_name="PERIODO_TIPO", value_name="VALOR")


    df_melt[["PERIODO", "TIPO"]] = df_melt["PERIODO_TIPO"].str.rsplit("_", n=1, expand=True)
    df_melt.drop(columns="PERIODO_TIPO", inplace=True)

    periodos = df_melt["PERIODO"].unique()[::-1]
    periodos_unicos = sorted(df_melt["PERIODO"].dropna().unique(), reverse=True)
    periodos_unicos.insert(0, "Todos")

    periodo_escolhido = st.selectbox("Selecione um período", periodos_unicos)
    
    st.markdown(
                    f"<h2 style='font-size:35px;text-align:center;' >{tecnico_escolhido}</h2>",
                    unsafe_allow_html=True
            )


    df_atg = df_melt[df_melt["TIPO"] == "ATG"].copy()


    df_atg["VALOR"] = (
        df_atg["VALOR"]
        .astype(str)
        .str.replace("%", "", regex=False)
        .str.replace(",", ".", regex=False)
        .str.strip()
    )

    # Converter para número, ignorando textos
    df_atg["VALOR"] = pd.to_numeric(df_atg["VALOR"], errors="coerce")

    # Remover valores NaN (que eram textos)
    df_atg = df_atg.dropna(subset=["VALOR"])



    st.markdown("""
    <style>
        .performance-cards {
            display: flex;
            justify-content: center;
            gap: 50px;
            margin: 40px auto;
            flex-wrap: wrap;
        }
        .performance-card {
            background-color: rgba(255, 255, 255, 0.05);
            box-shadow: 0 4px 12px rgba(100,100,100,0.2);
            border-radius: 15px;
            width: 250px;
            padding: 30px 20px;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.2);
            transition: 0.3s;
        }
        .performance-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 4px 12px rgba(255,255,255,0.3);
        }
        .performance-card label {
            color: #a0aec0;
            margin-bottom: 10px;
            font-weight: 600;
            font-size: 20px;
        }
        .performance-card .valor {
            font-size: 34px;
            font-weight: bold;
            color: #48bb78;
        }
        .performance-card.pior .valor {
            color: #e53e3e;
        }
        .performance-card .periodo {
            color: #63b3ed;
            font-size: 18px;
            margin-top: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Exibe os cards se houver dados
    if not df_atg.empty:
        melhor = df_atg.loc[df_atg["VALOR"].idxmax()]
        pior = df_atg.loc[df_atg["VALOR"].idxmin()]

        melhor_html = textwrap.dedent(f"""
        <div class="performance-card">
            <label>Melhor Mês</label>
            <div class="valor">{melhor['VALOR']:.1f}%</div>
            <div class="periodo">{melhor['PERIODO']}</div>
        </div>
        """).strip()

        pior_html = textwrap.dedent(f"""
        <div class="performance-card pior">
            <label>Pior Mês</label>
            <div class="valor">{pior['VALOR']:.1f}%</div>
            <div class="periodo">{pior['PERIODO']}</div>
        </div>
        """).strip()

        wrapper = f"<div class='performance-cards'>{melhor_html}{pior_html}</div>"

    
        st.markdown(f"<div class='performance-cards'>{melhor_html}{pior_html}</div>", unsafe_allow_html=True)
    else:
        st.warning("Nenhum dado de ATG encontrado.")


    st.markdown("""
    <style>
    .card-container {
        
        display: flex;
        gap: 50px;
        flex-wrap: wrap;
        justify-content: center;
        margin-bottom: 40px;
        margin:auto;
            
    }
    .card {
        background-color: transparent;
        box-shadow: 0 4px 12px rgba(100,100,100,0.1);
        border-radius: 15px;
        text-align:center;
        width: 220px;
        padding: 50px 20px;
        transition: 0.3s;
        border: solid 1px rgb(30, 30, 30);
        justify-content: center;
        align-itens: center;
        align-self:center;
        gap: 40px
        
    }
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 12px rgba(255,255,255,0.1);
    }
    .card h4 {
        text-align: center;
        color: white;
        font-weight: 600;
        margin-bottom: 15px;
    }
    .card .metric {
        text-align: center;
        font-size: 28px;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .card .label {
        text-align: center;
        font-size: 24px;
        color: white;
        letter-spacing: 1px;
    }
    .period-title {
        font-size: 22px;
        font-weight: 700;
        margin-top: 30px;
        margin-bottom: 15px;
        color: #2b6cb0;
        text-align:center;
    }
    .atg { color: #3182ce; }
    .meta { color: #38a169; }
    .fat { color: #d69e2e; }
    </style>
    """, unsafe_allow_html=True)

    # Título principal

    if periodo_escolhido != "Todos":
        dados_periodo = df_melt[df_melt["PERIODO"] == periodo_escolhido].set_index("TIPO")["VALOR"]

        st.markdown(f"<div class='period-title'>📅 {periodo_escolhido}</div>", unsafe_allow_html=True)

        card_html = f"""
        <div class="card-container">
            <div class="card">
                <div class="metric atg">{dados_periodo.get('ATG', '-')}</div>
                <div class="label">Atingido</div>
            </div>
            <div class="card">
                <div class="metric meta">{dados_periodo.get('MT', '-')}</div>
                <div class="label">Meta</div>
            </div>
            <div class="card">
                <div class="metric fat">{dados_periodo.get('FAT', '-')}</div>
                <div class="label">Faturado</div>
            </div>
        </div>
        """

        st.markdown(card_html, unsafe_allow_html=True)

    else:

        # Cria os cards por período
        for periodo in periodos:
            dados_periodo = df_melt[df_melt["PERIODO"] == periodo].set_index("TIPO")["VALOR"]
            
            st.markdown(f"<div class='period-title'>📅 {periodo}</div>", unsafe_allow_html=True)

            card_html = f"""
            <div class="card-container">
                <div class="card">
                    <div class="metric atg">{dados_periodo.get('ATG', '-')}</div>
                    <div class="label">Atingido</div>
                </div>
                <div class="card">
                <div class="metric meta">{dados_periodo.get('MT', '-')}</div>
                    <div class="label">Meta</div>
                </div>
                <div class="card">
                    <div class="metric fat">{dados_periodo.get('FAT', '-')}</div>
                    <div class="label">Faturado</div>
                </div>
            </div>
            """
            
            st.markdown(card_html, unsafe_allow_html=True)
