import streamlit as st
import pandas as pd
import os
import plotly.express as px
from gerador_arte_feedback import criar_carrossel_feedback

st.set_page_config(page_title="Feedback Pós-Jogo", layout="wide", page_icon="🏉")

@st.cache_data
def carregar_jogadores():
    arquivo_excel = 'elenco_ndu.xlsx'
    if os.path.exists(arquivo_excel):
        df = pd.read_excel(arquivo_excel)
        df['Apelido'] = df['Apelido'].astype(str).str.strip()
        if 'Telefone' not in df.columns:
            df['Telefone'] = "" 
        return df.sort_values('Apelido')
    else:
        return pd.DataFrame({'Apelido': ["Jogador 1", "Jogador 2"], 'Telefone': ["", ""]})

df_elenco = carregar_jogadores()
lista_jogadores = df_elenco['Apelido'].tolist()
arquivo_dados = "feedbacks_salvos.csv"
arquivo_convocados = "convocados_salvos.csv"

# ==========================================
# A PORTA SECRETA DO TREINADOR
# ==========================================
with st.sidebar:
    st.image("logo_ratacanga.png", use_column_width=True) if os.path.exists("logo_ratacanga.png") else None
    st.header("Área Restrita")
    senha_acesso = st.text_input("Senha do Treinador", type="password")

# ==========================================
# VISÃO PÚBLICA (O FORMULÁRIO DO JOGADOR)
# ==========================================
st.title("🏉 Central de Inteligência Pós-Jogo")
st.markdown("### Resenha da Partida")

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
            st.success("✅ Salvo com sucesso! Sua avaliação foi enviada para o treinador.")

# ==========================================
# VISÃO PRIVADA (SÓ APARECE COM A SENHA "MAMUTE")
# ==========================================
if senha_acesso.upper() == "MAMUTE":
    st.divider()
    st.title("🖥️ Painel de Comando do Treinador")
    
    tab_dados, tab_antimigue, tab_arte = st.tabs(["📊 Compilado de Dados", "🚨 Controle (Anti-Migué)", "📸 Gerar Carrossel (Instagram)"])

    # --- ABA DADOS ---
    with tab_dados:
        if os.path.exists(arquivo_dados):
            df = pd.read_csv(arquivo_dados)
            st.metric("Total de Respostas", len(df))
            st.dataframe(df) # Mostra a tabela crua para você conferir
        else:
            st.warning("Nenhum dado coletado.")

    # --- ABA ANTI-MIGUÉ ---
    with tab_antimigue:
        st.write("Defina os 23 escalados para o sistema cobrar quem não respondeu.")
        convocados_salvos = pd.read_csv(arquivo_convocados)['Jogador'].tolist() if os.path.exists(arquivo_convocados) else []
        jogadores_escalados = st.multiselect("Escalados do Jogo:", lista_jogadores, default=convocados_salvos)
        
        if st.button("💾 Salvar Lista de Escalados"):
            pd.DataFrame({'Jogador': jogadores_escalados}).to_csv(arquivo_convocados, index=False)
            st.success("Lista salva!")

        if os.path.exists(arquivo_dados):
            df = pd.read_csv(arquivo_dados)
            responderam = df['Jogador'].unique().tolist()
            faltam = [j for j in jogadores_escalados if j not in responderam]
            
            col_falta, col_ok = st.columns(2)
            with col_falta:
                st.error(f"❌ Faltam Responder ({len(faltam)})")
                for f in faltam:
                    telefone = str(df_elenco.loc[df_elenco['Apelido'] == f, 'Telefone'].values[0]).strip()
                    if telefone and telefone != "nan":
                        st.markdown(f"- {f} 📲 [Cobrar no WhatsApp](https://wa.me/55{telefone}?text=Preenche%20o%20feedback%20rapidao%3A%20https://respondaessamrd.streamlit.app/)")
                    else: st.write(f"- {f}")
            with col_ok:
                st.success(f"✅ Já Responderam ({len([j for j in jogadores_escalados if j in responderam])})")
                for j in [j for j in jogadores_escalados if j in responderam]: st.write(f"- {j}")

    # --- ABA ARTE FINAL (CARROSSEL) ---
    with tab_arte:
        st.markdown("### Preencha os dados para gerar o Carrossel do Instagram")
        
        col_j1, col_j2 = st.columns(2)
        with col_j1:
            data_str = st.text_input("Data do Jogo", "31/05/2026")
            local_str = st.text_input("Local", "CEPEUSP")
            adv_str = st.text_input("Adversário", "Poli")
        with col_j2:
            pontos_nos = st.text_input("Nossos Pontos", "50")
            pontos_eles = st.text_input("Pontos Deles", "14")
            
        st.markdown("#### Seus Comentários Técnicos")
        txt_geral = st.text_area("Comentário Geral:", "A equipe manteve a intensidade durante os 80 minutos. A transição e o apoio garantiram a continuidade da bola viva.")
        txt_fwd = st.text_area("Comentário Forwards:", "Scrum dominante. Excelente leitura de espaço e limpeza de ruck nos momentos de desordem.")
        txt_backs = st.text_area("Comentário Backs:", "Tomada de decisão agressiva e Parede Sonora impecável nas subidas defensivas.")
        
        if st.button("📸 Desenhar Carrossel Completo (4 Imagens)", type="primary"):
            if os.path.exists(arquivo_dados):
                df = pd.read_csv(arquivo_dados)
                detalhes = {"data": data_str, "local": local_str, "adversario": adv_str, "placar_nos": pontos_nos, "placar_eles": pontos_eles}
                comentarios = {"geral": txt_geral, "forwards": txt_fwd, "backs": txt_backs}
                
                with st.spinner("Desenhando Carrossel..."):
                    imagens = criar_carrossel_feedback(df, detalhes, comentarios)
                    st.success("Carrossel gerado com sucesso!")
                    
                    c1, c2, c3, c4 = st.columns(4)
                    with c1: st.image(imagens[0], caption="1. Capa")
                    with c2: st.image(imagens[1], caption="2. Análise")
                    with c3: st.image(imagens[2], caption="3. Votos")
                    with c4: st.image(imagens[3], caption="4. Radar")
            else:
                st.error("Nenhum dado coletado para desenhar as artes.")
