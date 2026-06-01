from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import math
import textwrap

def desenhar_texto_quebrado(draw, texto, x, y, fonte, cor, largura_maxima):
    # Quebra o texto para caber na tela
    linhas = textwrap.wrap(texto, width=largura_maxima)
    y_atual = y
    for linha in linhas:
        draw.text((x, y_atual), linha, font=fonte, fill=cor)
        y_atual += fonte.size + 10
    return y_atual

def criar_carrossel_feedback(df, detalhes_jogo, comentarios):
    LARGURA, ALTURA = 1080, 1350
    arquivos_gerados = []

    try:
        font_tit_gigante = ImageFont.truetype("fonte_padrao.ttf", 110)
        font_titulo = ImageFont.truetype("fonte_padrao.ttf", 80)
        font_sub = ImageFont.truetype("fonte_padrao.ttf", 45)
        font_texto = ImageFont.truetype("fonte_padrao.ttf", 35)
        font_pequena = ImageFont.truetype("fonte_padrao.ttf", 25)
    except:
        font_tit_gigante = font_titulo = font_sub = font_texto = font_pequena = ImageFont.load_default()

    # --- DADOS MATEMÁTICOS GERAIS ---
    nota_geral = df['Nota Pessoal'].mean() if not df.empty else 0
    nota_forwards = df[df['Setor'] == 'Forward']['Nota Pessoal'].mean() if not df[df['Setor'] == 'Forward'].empty else 0
    nota_backs = df[df['Setor'] == 'Back']['Nota Pessoal'].mean() if not df[df['Setor'] == 'Back'].empty else 0

    categorias = ['Foco', 'Fortaleza', 'Apoio', 'RELOAD', 'Espaço', 'Disciplina', 'Anarquia', 'Reinicio', 'Adaptacao']
    medias = {cat: df[cat].mean() for cat in categorias if not df[cat].dropna().empty}
    
    ponto_forte = max(medias, key=medias.get) if medias else "N/A"
    ponto_fraco = min(medias, key=medias.get) if medias else "N/A"

    COR_FUNDO = (15, 20, 30)
    COR_DESTAQUE = (255, 215, 0) # Dourado/Amarelo
    COR_TEXTO = (220, 220, 220)

    # ==========================================
    # SLIDE 1: A CAPA (Placar e Notas)
    # ==========================================
    img1 = Image.new('RGB', (LARGURA, ALTURA), color=COR_FUNDO)
    d1 = ImageDraw.Draw(img1)
    
    d1.text((80, 100), "MATCH REPORT", font=font_tit_gigante, fill=COR_TEXTO)
    d1.text((80, 220), f"{detalhes_jogo['data']} | {detalhes_jogo['local']}", font=font_sub, fill=(150, 150, 150))
    d1.line([(80, 290), (1000, 290)], fill=COR_DESTAQUE, width=4)

    # Placar
    d1.text((LARGURA//2, 400), "RATACANGA", font=font_sub, fill=COR_DESTAQUE, anchor="mm")
    d1.text((LARGURA//2, 480), f"{detalhes_jogo['placar_nos']} x {detalhes_jogo['placar_eles']}", font=font_tit_gigante, fill=COR_TEXTO, anchor="mm")
    d1.text((LARGURA//2, 560), f"{detalhes_jogo['adversario'].upper()}", font=font_sub, fill=(150, 150, 150), anchor="mm")

    # Notas
    d1.rectangle([(80, 680), (1000, 920)], fill=(25, 30, 45), outline=COR_DESTAQUE, width=2)
    d1.text((150, 720), "FORWARDS", font=font_sub, fill=(150, 150, 150))
    d1.text((200, 780), f"{nota_forwards:.1f}", font=font_tit_gigante, fill=COR_TEXTO)

    d1.text((450, 720), "NOTA GERAL", font=font_sub, fill=COR_DESTAQUE)
    d1.text((480, 780), f"{nota_geral:.1f}", font=font_tit_gigante, fill=COR_DESTAQUE)

    d1.text((780, 720), "BACKS", font=font_sub, fill=(150, 150, 150))
    d1.text((800, 780), f"{nota_backs:.1f}", font=font_tit_gigante, fill=COR_TEXTO)

    # Destaques
    d1.text((80, 1000), f"🟢 FORTE: {ponto_forte.upper()}", font=font_titulo, fill=(50, 205, 50))
    d1.text((80, 1100), f"🔴 CORRIGIR: {ponto_fraco.upper()}", font=font_titulo, fill=(220, 20, 60))
    
    img1.save("1_Capa_Report.jpg", quality=100)
    arquivos_gerados.append("1_Capa_Report.jpg")


    # ==========================================
    # SLIDE 2: COMENTÁRIOS DO TREINADOR
    # ==========================================
    img2 = Image.new('RGB', (LARGURA, ALTURA), color=COR_FUNDO)
    d2 = ImageDraw.Draw(img2)

    d2.text((80, 100), "ANÁLISE TÁTICA", font=font_titulo, fill=COR_TEXTO)
    d2.line([(80, 200), (1000, 200)], fill=COR_DESTAQUE, width=4)

    y_base = 250
    if comentarios['geral']:
        d2.text((80, y_base), "VISÃO GERAL:", font=font_sub, fill=COR_DESTAQUE)
        y_base = desenhar_texto_quebrado(d2, comentarios['geral'], 80, y_base + 60, font_texto, COR_TEXTO, 45) + 60
    
    if comentarios['forwards']:
        d2.text((80, y_base), "PACK DE FORWARDS:", font=font_sub, fill=(150, 150, 150))
        y_base = desenhar_texto_quebrado(d2, comentarios['forwards'], 80, y_base + 60, font_texto, COR_TEXTO, 45) + 60

    if comentarios['backs']:
        d2.text((80, y_base), "LINHA DOS BACKS:", font=font_sub, fill=(150, 150, 150))
        desenhar_texto_quebrado(d2, comentarios['backs'], 80, y_base + 60, font_texto, COR_TEXTO, 45)

    img2.save("2_Analise.jpg", quality=100)
    arquivos_gerados.append("2_Analise.jpg")


    # ==========================================
    # SLIDE 3: O COMPILADO DOS VOTOS
    # ==========================================
    img3 = Image.new('RGB', (LARGURA, ALTURA), color=COR_FUNDO)
    d3 = ImageDraw.Draw(img3)

    d3.text((80, 100), "TERMOSTATO DA EQUIPE", font=font_titulo, fill=COR_TEXTO)
    d3.line([(80, 200), (1000, 200)], fill=COR_DESTAQUE, width=4)

    y_votos = 250
    for cat in categorias:
        if not df[cat].dropna().empty:
            # Conta os votos (1 a 4)
            votos = df[cat].value_counts().to_dict()
            v1 = votos.get(1.0, 0)
            v2 = votos.get(2.0, 0)
            v3 = votos.get(3.0, 0)
            v4 = votos.get(4.0, 0)
            total = v1 + v2 + v3 + v4

            d3.text((80, y_votos), cat.upper(), font=font_sub, fill=COR_DESTAQUE)
            
            # Desenha as barras horizontais de votação
            largura_barra = 700
            d3.rectangle([(350, y_votos + 15), (350 + largura_barra, y_votos + 45)], fill=(30, 40, 55))
            
            # Pinta a barra de acordo com os votos bons (3 e 4)
            bons = v3 + v4
            if total > 0:
                percentual_bom = bons / total
                d3.rectangle([(350, y_votos + 15), (350 + (largura_barra * percentual_bom), y_votos + 45)], fill=(50, 205, 50))

            texto_votos = f"{bons} votos Positivos | {v1+v2} Negativos"
            d3.text((350, y_votos - 25), texto_votos, font=font_pequena, fill=COR_TEXTO)

            y_votos += 110

    img3.save("3_Votacao.jpg", quality=100)
    arquivos_gerados.append("3_Votacao.jpg")


    # ==========================================
    # SLIDE 4: O RADAR
    # ==========================================
    img4 = Image.new('RGB', (LARGURA, ALTURA), color=COR_FUNDO)
    d4 = ImageDraw.Draw(img4)

    d4.text((80, 100), "RADIOGRAFIA DE SISTEMA", font=font_titulo, fill=COR_TEXTO)
    d4.line([(80, 200), (1000, 200)], fill=COR_DESTAQUE, width=4)

    centro_x, centro_y = 540, 750
    raio_max = 350

    for i in range(1, 5):
        r = (i / 4) * raio_max
        pontos_teia = []
        for j in range(9):
            angulo = math.radians(j * 40 - 90)
            x = centro_x + r * math.cos(angulo)
            y = centro_y + r * math.sin(angulo)
            pontos_teia.append((x, y))
            if i == 4: 
                d4.line([(centro_x, centro_y), (x, y)], fill=(50, 60, 80), width=2)
        d4.polygon(pontos_teia, outline=(50, 60, 80))

    for j, cat in enumerate(categorias):
        angulo = math.radians(j * 40 - 90)
        x_texto = centro_x + (raio_max + 60) * math.cos(angulo)
        y_texto = centro_y + (raio_max + 60) * math.sin(angulo)
        d4.text((x_texto, y_texto), cat.upper(), font=font_pequena, fill=(200, 200, 200), anchor="mm")

    pontos_time = []
    lista_medias = [medias.get(cat, 1) for cat in categorias]
    for j, media in enumerate(lista_medias):
        r = (media / 4) * raio_max
        angulo = math.radians(j * 40 - 90)
        x = centro_x + r * math.cos(angulo)
        y = centro_y + r * math.sin(angulo)
        pontos_time.append((x, y))
        d4.ellipse([(x-10, y-10), (x+10, y+10)], fill=COR_DESTAQUE) 
    
    d4.polygon(pontos_time, outline=COR_DESTAQUE, width=8)

    img4.save("4_Radar.jpg", quality=100)
    arquivos_gerados.append("4_Radar.jpg")

    return arquivos_gerados
