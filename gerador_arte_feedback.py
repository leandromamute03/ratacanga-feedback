from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import math

def criar_arte_resumo_feedback(df, adversario="Adversário"):
    LARGURA, ALTURA = 1080, 1350
    # Fundo Dark Mode institucional
    fundo = Image.new('RGB', (LARGURA, ALTURA), color=(15, 20, 30))
    draw = ImageDraw.Draw(fundo)

    try:
        font_titulo = ImageFont.truetype("fonte_padrao.ttf", 90)
        font_sub = ImageFont.truetype("fonte_padrao.ttf", 45)
        font_destaque = ImageFont.truetype("fonte_padrao.ttf", 110)
        font_radar = ImageFont.truetype("fonte_padrao.ttf", 26)
    except:
        font_titulo = font_sub = font_destaque = font_radar = ImageFont.load_default()

    # --- CÁLCULOS MATEMÁTICOS ---
    nota_geral = df['Nota Pessoal'].mean() if not df.empty else 0
    df_forwards = df[df['Setor'] == 'Forward']
    nota_forwards = df_forwards['Nota Pessoal'].mean() if not df_forwards.empty else 0
    df_backs = df[df['Setor'] == 'Back']
    nota_backs = df_backs['Nota Pessoal'].mean() if not df_backs.empty else 0

    categorias = ['Foco', 'Fortaleza', 'Apoio', 'RELOAD', 'Espaço', 'Disciplina', 'Anarquia', 'Reinicio', 'Adaptacao']
    medias = [df[cat].mean() if not df[cat].dropna().empty else 1 for cat in categorias]

    # --- CABEÇALHO ---
    draw.text((80, 70), "RELATÓRIO DE PERFORMANCE", font=font_titulo, fill=(255, 255, 255))
    draw.text((80, 180), f"Pós-Jogo vs {adversario}", font=font_sub, fill=(150, 150, 150))
    draw.line([(80, 250), (1000, 250)], fill=(255, 215, 0), width=4) # Linha Ouro

    # --- O GRÁFICO DE RADAR (Desenhado do Zero em PIL) ---
    centro_x, centro_y = 540, 680
    raio_max = 300

    # 1. Desenha as linhas da teia
    for i in range(1, 5):
        r = (i / 4) * raio_max
        pontos_teia = []
        for j in range(9):
            angulo = math.radians(j * 40 - 90)
            x = centro_x + r * math.cos(angulo)
            y = centro_y + r * math.sin(angulo)
            pontos_teia.append((x, y))
            if i == 4: # Linhas que vão do centro até a borda
                draw.line([(centro_x, centro_y), (x, y)], fill=(50, 60, 80), width=2)
        draw.polygon(pontos_teia, outline=(50, 60, 80))

    # 2. Escreve os nomes das categorias ao redor do radar
    for j, cat in enumerate(categorias):
        angulo = math.radians(j * 40 - 90)
        x_texto = centro_x + (raio_max + 40) * math.cos(angulo)
        y_texto = centro_y + (raio_max + 40) * math.sin(angulo)
        draw.text((x_texto, y_texto), cat.upper(), font=font_radar, fill=(200, 200, 200), anchor="mm")

    # 3. Desenha a "Mancha" de performance do time
    pontos_time = []
    for j, media in enumerate(medias):
        r = (media / 4) * raio_max
        angulo = math.radians(j * 40 - 90)
        x = centro_x + r * math.cos(angulo)
        y = centro_y + r * math.sin(angulo)
        pontos_time.append((x, y))
        draw.ellipse([(x-8, y-8), (x+8, y+8)], fill=(255, 215, 0)) # Pontinhos de marcação
    
    draw.polygon(pontos_time, outline=(255, 215, 0), width=6)

    # --- RODAPÉ (NOTAS DOS SETORES) ---
    y_rodape = 1100
    draw.line([(80, y_rodape), (1000, y_rodape)], fill=(100, 100, 100), width=2)
    
    draw.text((150, y_rodape + 40), "FORWARDS", font=font_sub, fill=(150, 150, 150))
    draw.text((180, y_rodape + 100), f"{nota_forwards:.1f}", font=font_destaque, fill=(255, 255, 255))

    draw.text((450, y_rodape + 40), "TIME GERAL", font=font_sub, fill=(255, 215, 0))
    draw.text((470, y_rodape + 100), f"{nota_geral:.1f}", font=font_destaque, fill=(255, 215, 0))

    draw.text((800, y_rodape + 40), "BACKS", font=font_sub, fill=(150, 150, 150))
    draw.text((810, y_rodape + 100), f"{nota_backs:.1f}", font=font_destaque, fill=(255, 255, 255))

    nome_arquivo = "resumo_feedback_instagram.jpg"
    fundo.save(nome_arquivo, quality=100)
    return nome_arquivo
