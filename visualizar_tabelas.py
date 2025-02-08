import numpy as np
import pandas as pd
import yfinance as yf
import streamlit as st
import plotly.express as px
from click import style

st.set_page_config(layout='wide')
tabela_fundos = pd.read_excel('./fundos.xlsx')

valor_fundo = list()
valorP_fundo = list()
valor_DY = list()

def formatar(styler):
    styler.set_caption("Visualização de ativos")
    if 'Diferenca' in colunas_selecionadas:
        styler.background_gradient(vmin=-1, vmax=1, cmap="RdYlGn", subset=['Diferenca'], gmap=tabela_fundos['DifNormalize'])
    if 'P/VP' in colunas_selecionadas:
        inverso_p = tabela_fundos['P/VP'] * -1
        styler.background_gradient(vmin=-2, vmax=-0.01, cmap="RdYlGn", subset=['P/VP'], gmap=inverso_p)
    styler.format({'DY': '{:.2f}%'}, na_rep='Valor não encontrado', precision=2)
    return styler

for cod in tabela_fundos['Codigo']:
    try:
        valor_fundo.append(yf.Ticker(cod + ".SA").info.get('currentPrice'))
        valorP_fundo.append(yf.Ticker(cod + ".SA").info.get('priceToBook'))
        valor_DY.append(yf.Ticker(cod + ".SA").info.get('dividendRate'))
    except Exception as e:
        if e.args[0] == "priceToBook":
            valorP_fundo.append('Valor não encontrado')
        else:
            valor_fundo.append('Valor não encontrado')
            valorP_fundo.append('Valor não encontrado')

tabela_fundos['Valor total'] = valor_fundo * tabela_fundos['Quantidade']
tabela_fundos['Valor atual'] = valor_fundo
tabela_fundos['DY'] = valor_DY
tabela_fundos['P/VP'] = valorP_fundo

tabela_fundos.index = tabela_fundos['Codigo'].values
tabela_fundos.drop(columns=['Codigo'], inplace=True)

tabela_fundos['Diferenca'] = tabela_fundos['Valor atual'].values * tabela_fundos['Quantidade'].values - tabela_fundos['Preço medio'].values * tabela_fundos['Quantidade'].values

v = list(tabela_fundos['Diferenca'].fillna(0))
tabela_fundos['DifNormalize'] = v/np.linalg.norm(v)

colunas = list(tabela_fundos.columns)
colunas.remove('DifNormalize')

tab_vis_padrao, tab_grafico, tab_plano = st.tabs(["Visualização dos ativos","Visualização gráfica","Plano de carteira"])
col1 = st.sidebar

#Filtrando colunas
colunas_selecionadas = col1.multiselect('Informações a serem exibidas:', colunas, colunas)

#Filtrando ativos

valor_filtro = col1.selectbox('Selecione o valor', ['Tudo', 'Fundos', 'Renda Fixa', 'Ações'])

status_filtrar = col1.button('Filtrar')

codigosConversao = {'Fundos': '11', 'Renda Fixa': ' ', 'Ações': '3'}


#Adicionar novos ativos
with col1.form('Adicionar ativos'):
    nome_ativo_adicionar = st.text_input('Codigo do ativo')

    quantidade_ativos = st.number_input('Quantide de cotas')

    preco_compra = st.number_input('Valor do ativo')

    adicionado = st.form_submit_button("Adicionar")

    if adicionado:
        ativo_adicionar = {'Codigo': [nome_ativo_adicionar],'Preço medio': [preco_compra], 'Quantidade': [quantidade_ativos]}
        ativo_adicionar_tabela = pd.DataFrame(ativo_adicionar)
        if nome_ativo_adicionar not in tabela_fundos.index:
            try:
                valor_fundo = (yf.Ticker(ativo_adicionar_tabela['Codigo'][0] + ".SA").info.get('currentPrice'))
                valorP_fundo = (yf.Ticker(ativo_adicionar_tabela['Codigo'][0] + ".SA").info.get('priceToBook'))
                valor_DY = (yf.Ticker(ativo_adicionar_tabela['Codigo'][0] + ".SA").info.get('dividendRate'))
            except Exception as e:
                if e.args[0] == "priceToBook":
                    valorP_fundo = 'Valor não encontrado'
                else:
                    valor_fundo = 'Valor não encontrado'
                    valorP_fundo = 'Valor não encontrado'

            ativo_adicionar_tabela['Valor total'] = valor_fundo * ativo_adicionar_tabela['Quantidade']
            ativo_adicionar_tabela['Valor atual'] = valor_fundo
            ativo_adicionar_tabela['DY'] = valor_DY
            ativo_adicionar_tabela['P/VP'] = valorP_fundo
            ativo_adicionar_tabela.index = ativo_adicionar_tabela['Codigo'].values
            ativo_adicionar_tabela.drop(columns=['Codigo'], inplace=True)
            ativo_adicionar_tabela['Diferenca'] = ativo_adicionar_tabela['Valor atual'].values * ativo_adicionar_tabela['Quantidade'].values - ativo_adicionar_tabela['Preço medio'].values * ativo_adicionar_tabela['Quantidade'].values
            v = list(tabela_fundos['Diferenca']) + list(ativo_adicionar_tabela['Diferenca'])
            ativo_adicionar_tabela['DifNormalize'] = ativo_adicionar_tabela['Diferenca'][0] / np.linalg.norm(v)
            tabela_fundos.loc[nome_ativo_adicionar] = ativo_adicionar_tabela.values.tolist()[0]
        else:
            try:
                valor_fundo = (yf.Ticker(nome_ativo_adicionar + ".SA").info.get('currentPrice'))
            except Exception as e:
                print(e.args[0])

            quantidade_nova = tabela_fundos.loc[nome_ativo_adicionar]['Quantidade'] + quantidade_ativos
            preco_medio = (tabela_fundos.loc[nome_ativo_adicionar]['Preço medio'] * tabela_fundos.loc[nome_ativo_adicionar]['Quantidade'] + preco_compra * quantidade_ativos)/quantidade_nova
            tabela_fundos.loc[nome_ativo_adicionar, 'Preço medio'] = preco_medio
            tabela_fundos.loc[nome_ativo_adicionar, 'Quantidade'] = quantidade_nova
            tabela_fundos.loc[nome_ativo_adicionar, 'Diferenca'] = valor_fundo * quantidade_nova - preco_medio * quantidade_nova
            tabela_fundos.loc[nome_ativo_adicionar, 'Valor total'] = valor_fundo * quantidade_nova
            v = list(tabela_fundos['Diferenca'].fillna(0))
            tabela_fundos['DifNormalize'] = v / np.linalg.norm(v)
        #tabela_fundos.to_excel('./fundos.xlsx')
        st.write('Adicionado!')
#Aba 1
with tab_vis_padrao:
    st.header('Visualização dos ativos')
    st.divider()
    col1, col2 = st.columns([0.2,0.8])
    if status_filtrar and valor_filtro != 'Tudo':
        tabela_ativos_filtro = tabela_fundos.loc[tabela_fundos.index.str.contains(codigosConversao[valor_filtro])]
        col2.dataframe(tabela_ativos_filtro[colunas_selecionadas].style.pipe(formatar))
    else:
        col2.dataframe(tabela_fundos[colunas_selecionadas].style.pipe(formatar))

#Aba 2
with tab_grafico:
    graph_holding_distribution = px.pie(tabela_fundos, values='Valor total', names=tabela_fundos.index, title='Distribuição dos ativos')
    col1, col2, col3 = st.columns([0.5, 0.25, 0.25])
    col1.markdown('# Valores Gerais')
    col2.metric('Valor total aplicado', tabela_fundos['Valor total'].sum())
    col3.metric('Quantidade de dividendos acumulado', tabela_fundos['Quantidade'].sum())
    st.divider()
    col1, col2 = st.columns([0.8,0.2])
    graph_exb = col2.radio('Tipo gráfico', ['Distribuição dos ativos', 'Evolução dos ativos'])
    if graph_exb == 'Distribuição dos ativos':
        fig = px.pie(tabela_fundos, values='Valor total', names=tabela_fundos.index, title='Distribuição dos ativos')
        col1.plotly_chart(fig, use_container_width=True)
    elif graph_exb == 'Evolução dos ativos':
        col1.write('Construindo...')