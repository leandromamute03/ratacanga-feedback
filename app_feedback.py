import streamlit as st
import pandas as pd
import os
import plotly.express as px
from gerador_arte_feedback import criar_arte_resumo_feedback

st.set_page_config(page_title="Feedback Pós-Jogo", layout="wide", page_icon="🏉")
st.title("🏉 Central de Inteligência Pós-Jogo")

@st.cache_data
def carregar_jogadores():
    arquivo_excel = 'elenco_ndu.xlsx'
    if os.path.exists(arquivo_excel):
        df = pd.read_excel(arquivo_excel)
        # Limpa e padroniza a planilha
        df['Apelido'] = df['Apelido'].astype(str).str.strip()
        if 'Telefone' not in df.columns:
            df['Telefone'] = "" # Cria a coluna vazia se não existir para não quebrar o código
        return df.sort_values('Apelido')
    else:
        return pd.DataFrame({'Apelido': ["Jogador 1", "Jogador 2"], 'Telefone': ["", ""]})

df_elenco = carregar_jogadores()
lista_jogadores = df_elenco['Apelido'].tolist()
arquivo_dados = "feedbacks_salvos.csv"
arquivo_convocados = "convocados_salvos.csv"

# NOVA ORDEM DAS ABAS
tab_jogador, tab_antimigue, tab_arte = st.tabs(["1️⃣ Formulário do Atleta", "2️⃣ Controle (Anti-Migué)", "3️⃣ Painel e Arte Final 📸"])

# ==========================================
# ABA 1: FORMULÁRIO DO JOGADOR
# ==========================================
with tab_jogador:
    st.markdown("### Resenha Pós-Jogo")
    with st.form("form_feedback"):
        col1, col2, col3 = st.columns(3)
        with col1: jogador = st.selectbox("Quem é você?", ["Selecione seu nome..."] + lista_jogadores)
        with col2: setor = st.radio("Seu Setor:", ["Forward", "Back"], horizontal=True)
        with col3: status_jogo = st.radio("Seu status hoje:", ["Titular", "Impacto (Reserva)"], horizontal=True)
            
        st.divider()
        opcoes = ["1 - Insuficiente", "2 - Ruim", "3 - Bom", "4 - Excelente"]
        
        st.markdown("#### 1. O 'Eu'")
        pse = st.slider("Esforço Físico (PSE - 0 a 10):", 0, 10, 5)
        nota_pessoal = st.slider("Nota de Desempenho Pessoal (1 a 10):", 1, 10, 6)
        foco = st.radio("Foco: Assumi a responsabilidade pela minha ativação?", opcoes, horizontal=True)
        fortaleza = st.radio("Fortaleza Mental: Mantive a concentração após erros?", opcoes, horizontal=True)
        
        st.markdown("#### 2. O Caos Planejado")
        apoio = st.radio("Apoio: Nossas linhas ofereceram opções?", opcoes, horizontal=True)
        reload = st.radio("RELOAD: Velocidade para ficar de pé após o contato?", opcoes, horizontal=True)
        espaco = st.radio("Batalha pelo Espaço: Eficiência na caçada/cobertura?", opcoes, horizontal=True)
        
        st.markdown("#### 3. A Parede de Ruído")
        disciplina = st.radio("DISCIPLINA: Integridade, alinhamento e enquadramento?", opcoes, horizontal=True)
        anarquia = st.radio("ANARQUIA: Parede sonora e agressividade no turnover?", opcoes, horizontal=True)
        
        st.markdown("#### 4. O Coletivo")
        reinicio = st.radio("Reinício: Formações fixas nos deram plataformas limpas?", opcoes, horizontal=True)
        adaptacao = st.radio("Adaptação: Lemos o árbitro e o adversário a tempo?", opcoes, horizontal=True)
        
        impacto_banco = "N/A"
        if status_jogo == "Impacto (Reserva)":
            impacto_banco = st.radio("Missão de Impacto: Ditei o ritmo físico ao entrar?", opcoes, horizontal=True)
            
        pergunta_aberta = st.text_area("O Desafio Tático:", placeholder="Qual foi a principal falha coletiva hoje?")
        enviado = st.form_submit_button("🚀 Enviar Relatório", type="primary")
        
        if enviado:
            if jogador == "Selecione seu nome...":
                st.error("Selecione seu nome!")
            else:
                def e_nota(t): return int(t.split(" ")[0]) if t != "N/A" else None
                novo_feedback = {
                    "Data": pd.Timestamp.now().strftime("%d/%m/%Y"), "Jogador": jogador, "Setor": setor, "Status": status_jogo,
                    "PSE": pse, "Nota Pessoal": nota_pessoal, "Foco": e_nota(foco), "Fortaleza": e_nota(fortaleza),
                    "Apoio": e_nota(apoio), "RELOAD": e_nota(reload), "Espaço": e_nota(espaco),
                    "Disciplina": e_nota(disciplina), "Anarquia": e_nota(anarquia), "Reinicio": e_nota(reinicio),
                    "Adaptacao": e_nota(adaptacao), "Impacto Banco": e_nota(impacto_banco) if impacto_banco != "N/A" else None,
                    "Comentário Aberto": pergunta_aberta
                }
                df_novo = pd.DataFrame([novo_feedback])
                if os.path.exists(arquivo_dados):
                    df_final = pd.concat([pd.read_csv(arquivo_dados), df_novo], ignore_index=True)
                else: df_final = df_novo
                df_final.to_csv(arquivo_dados, index=False)
                st.success("✅ Salvo com sucesso!")

# ==========================================
# ABA 2: O ANTI-MIGUÉ (Com Memória e WhatsApp)
# ==========================================
with tab_antimigue:
    st.markdown("### 🚨 Painel de Cobrança")
    
    # Sistema de Memória dos Convocados
    if os.path.exists(arquivo_convocados):
        convocados_salvos = pd.read_csv(arquivo_convocados)['Jogador'].tolist()
    else:
        convocados_salvos = []

    jogadores_escalados = st.multiselect("Defina os 23 escalados do jogo:", lista_jogadores, default=convocados_salvos)
    
    if st.button("💾 Salvar Lista de Escalados para este Fim de Semana"):
        pd.DataFrame({'Jogador': jogadores_escalados}).to_csv(arquivo_convocados, index=False)
        st.success("Lista travada! Agora o sistema lembrará de quem cobrar.")

    st.divider()

    if os.path.exists(arquivo_dados):
        df = pd.read_csv(arquivo_dados)
        responderam = df['Jogador'].unique().tolist()
        faltam = [j for j in jogadores_escalados if j not in responderam]
        
        col_falta, col_ok = st.columns(2)
        with col_falta:
            st.error(f"❌ Faltam Responder ({len(faltam)})")
            for f in faltam:
                # Busca o telefone na planilha
                telefone = str(df_elenco.loc[df_elenco['Apelido'] == f, 'Telefone'].values[0]).strip()
                if telefone and telefone != "nan":
                    # Botão verde mágico do WhatsApp
                    st.markdown(f"- {f} 📲 [Cobrar no WhatsApp](https://wa.me/55{telefone}?text=Fala%20irmao!%20Preenche%20o%20feedback%20do%20jogo%20rapidao%3A%20https://respondaessamrd.streamlit.app/)")
                else:
                    st.write(f"- {f} (Sem telefone na planilha)")
                
        with col_ok:
            st.success(f"✅ Já Responderam ({len([j for j in jogadores_escalados if j in responderam])})")
            for j in [j for j in jogadores_escalados if j in responderam]:
                st.write(f"- {j}")
    else:
        st.info("Aguardando a primeira resposta para iniciar o rastreamento.")

# ==========================================
# ABA 3: PAINEL E ARTE FINAL
# ==========================================
with tab_arte:
    st.markdown("### 📸 Estúdio de Exportação")
    if os.path.exists(arquivo_dados):
        df = pd.read_csv(arquivo_dados)
        
        col_export1, col_export2 = st.columns([1, 2])
        
        with col_export1:
            st.metric("Total de Respostas Coletadas", len(df))
            adversario_nome = st.text_input("Adversário:", "Poli")
            
            if st.button("📸 Desenhar Arte do Feedback", type="primary", use_container_width=True):
                with st.spinner("Construindo Teia de Aranha..."):
                    arte = criar_arte_resumo_feedback(df, adversario_nome)
                    st.session_state['arte_feedback'] = arte
        
        with col_export2:
            if 'arte_feedback' in st.session_state:
                st.image(st.session_state['arte_feedback'], caption="Imagem em alta resolução desenhada com sucesso.")
                st.success("Tire um print ou clique com o botão direito para salvar e postar no Instagram!")
                
    else:
        st.warning("Nenhum dado coletado ainda.")
