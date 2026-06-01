import streamlit as st
import pandas as pd
import os
import plotly.express as px
from gerador_arte_feedback import criar_arte_resumo_feedback

st.set_page_config(page_title="Feedback Pós-Jogo", layout="wide", page_icon="🏉")
st.title("🏉 Painel de Inteligência e Feedback")

@st.cache_data
def carregar_jogadores():
    arquivo_excel = 'elenco_ndu.xlsx'
    if os.path.exists(arquivo_excel):
        df = pd.read_excel(arquivo_excel)
        return sorted(df['Apelido'].dropna().astype(str).str.strip().tolist())
    else:
        return ["Jogador A", "Jogador B", "Jogador C"] 

lista_jogadores = carregar_jogadores()
arquivo_dados = "feedbacks_salvos.csv"

tab_jogador, tab_treinador, tab_antimigue = st.tabs(["📱 Preencher (Jogadores)", "📊 Painel e Arte (Treinador)", "🚨 Controle (Anti-Migué)"])

# ==========================================
# ABA 1: VISÃO DO JOGADOR
# ==========================================
with tab_jogador:
    st.markdown("### Resenha Pós-Jogo")
    with st.form("form_feedback"):
        col1, col2, col3 = st.columns(3)
        with col1: jogador = st.selectbox("Quem é você?", ["Selecione seu nome..."] + lista_jogadores)
        with col2: setor = st.radio("Seu Setor:", ["Forward", "Back"], horizontal=True)
        with col3: status_jogo = st.radio("Seu status hoje:", ["Titular", "Impacto (Reserva)"], horizontal=True)
            
        st.divider()
        opcoes_escala = ["1 - Insuficiente", "2 - Ruim", "3 - Bom", "4 - Excelente"]
        
        st.markdown("#### 1. O 'Eu'")
        pse = st.slider("Esforço Físico (PSE - 0 a 10):", 0, 10, 5)
        nota_pessoal = st.slider("Nota de Desempenho Pessoal (1 a 10):", 1, 10, 6)
        foco = st.radio("Foco Pré-Jogo: Assumi a responsabilidade pela minha ativação?", opcoes_escala, horizontal=True)
        fortaleza = st.radio("Fortaleza Mental: Mantive a concentração após erros?", opcoes_escala, horizontal=True)
        
        st.markdown("#### 2. O Caos Planejado")
        apoio = st.radio("Apoio (Bola/Espaço): Nossas linhas ofereceram opções?", opcoes_escala, horizontal=True)
        reload = st.radio("RELOAD (Urgência): Velocidade para ficar de pé após o contato?", opcoes_escala, horizontal=True)
        espaco = st.radio("Batalha pelo Espaço: Fomos eficientes na caçada/cobertura?", opcoes_escala, horizontal=True)
        
        st.markdown("#### 3. A Parede de Ruído")
        disciplina = st.radio("DISCIPLINA: A linha manteve integridade e alinhamento?", opcoes_escala, horizontal=True)
        anarquia = st.radio("ANARQUIA: Subimos fazendo barulho e agressivos no turnover?", opcoes_escala, horizontal=True)
        
        st.markdown("#### 4. O Coletivo")
        reinicio = st.radio("Reinício: Formações fixas nos deram plataformas limpas?", opcoes_escala, horizontal=True)
        adaptacao = st.radio("Adaptação: Lemos o árbitro e o adversário a tempo?", opcoes_escala, horizontal=True)
        
        impacto_banco = "N/A"
        if status_jogo == "Impacto (Reserva)":
            impacto_banco = st.radio("Missão de Impacto: Ditei o ritmo físico ao entrar?", opcoes_escala, horizontal=True)
            
        pergunta_aberta = st.text_area("O Desafio Tático:", placeholder="Qual foi a principal falha coletiva hoje?")
        enviado = st.form_submit_button("🚀 Enviar Relatório", type="primary")
        
        if enviado:
            if jogador == "Selecione seu nome...":
                st.error("Selecione seu nome!")
            else:
                def extrair_nota(texto): return int(texto.split(" ")[0]) if texto != "N/A" else None
                novo_feedback = {
                    "Data": pd.Timestamp.now().strftime("%d/%m/%Y"), "Jogador": jogador, "Setor": setor, "Status": status_jogo,
                    "PSE": pse, "Nota Pessoal": nota_pessoal, "Foco": extrair_nota(foco), "Fortaleza": extrair_nota(fortaleza),
                    "Apoio": extrair_nota(apoio), "RELOAD": extrair_nota(reload), "Espaço": extrair_nota(espaco),
                    "Disciplina": extrair_nota(disciplina), "Anarquia": extrair_nota(anarquia), "Reinicio": extrair_nota(reinicio),
                    "Adaptacao": extrair_nota(adaptacao), "Impacto Banco": extrair_nota(impacto_banco) if impacto_banco != "N/A" else None,
                    "Comentário Aberto": pergunta_aberta
                }
                df_novo = pd.DataFrame([novo_feedback])
                if os.path.exists(arquivo_dados):
                    df_final = pd.concat([pd.read_csv(arquivo_dados), df_novo], ignore_index=True)
                else: df_final = df_novo
                df_final.to_csv(arquivo_dados, index=False)
                st.success("✅ Salvo com sucesso!")

# ==========================================
# ABA 2: PAINEL DO TREINADOR E GERADOR DE ARTE
# ==========================================
with tab_treinador:
    st.markdown("### 📈 Dashboard e Publicação")
    if os.path.exists(arquivo_dados):
        df = pd.read_csv(arquivo_dados)
        st.metric("Total de Respostas", len(df))
        
        # Botão para gerar a arte do Instagram
        adversario_nome = st.text_input("Nome do Adversário (Para a Arte):", "Poli")
        if st.button("📸 Gerar Arte do Feedback para Instagram", type="primary"):
            with st.spinner("Compilando médias e desenhando arte..."):
                arte = criar_arte_resumo_feedback(df, adversario_nome)
                st.image(arte, width=400, caption="Pronto para postar!")
                
        st.divider()
        categorias = ['Foco', 'Fortaleza', 'Apoio', 'RELOAD', 'Espaço', 'Disciplina', 'Anarquia', 'Reinicio', 'Adaptacao']
        medias = [df[cat].mean() for cat in categorias]
        df_radar = pd.DataFrame(dict(r = medias + [medias[0]], theta = categorias + [categorias[0]]))
        fig = px.line_polar(df_radar, r='r', theta='theta', line_close=True, range_r=[1,4], markers=True)
        fig.update_traces(fill='toself', line_color='#E74C3C')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Nenhum dado coletado ainda.")

# ==========================================
# ABA 3: CONTROLE (O ANTI-MIGUÉ)
# ==========================================
with tab_antimigue:
    st.markdown("### 🚨 Painel de Cobrança")
    st.write("Defina quem foram os 23 escalados para o sistema verificar automaticamente quem está devendo resposta.")
    
    jogadores_escalados = st.multiselect("Selecione os 23 jogadores que foram para o jogo:", lista_jogadores, default=lista_jogadores[:23] if len(lista_jogadores) >= 23 else lista_jogadores)
    
    if os.path.exists(arquivo_dados):
        df = pd.read_csv(arquivo_dados)
        responderam = df['Jogador'].unique().tolist()
        
        # Lógica do Anti-Migué: Escalados que não estão na lista de respostas
        faltam = [j for j in jogadores_escalados if j not in responderam]
        
        st.divider()
        col_ok, col_falta = st.columns(2)
        with col_ok:
            st.success(f"✅ Já Responderam ({len([j for j in jogadores_escalados if j in responderam])})")
            for j in [j for j in jogadores_escalados if j in responderam]:
                st.write(f"- {j}")
                
        with col_falta:
            if len(faltam) > 0:
                st.error(f"❌ Faltam Responder ({len(faltam)})")
                for f in faltam:
                    st.write(f"- {f}")
                
                # Gera uma lista fácil de copiar e colar no WhatsApp
                st.text_area("Copiar para cobrar no WhatsApp:", "Atenção! Faltam preencher o feedback: " + ", ".join(faltam))
            else:
                st.balloons()
                st.success("Todos os 23 jogadores já responderam! O relatório está completo.")
    else:
        st.info("Aguardando a primeira resposta para iniciar o rastreamento.")