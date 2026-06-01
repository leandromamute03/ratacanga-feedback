from PIL import Image, ImageDraw, ImageFont
import pandas as pd

def criar_arte_resumo_feedback(df, adversario="Adversário"):
    LARGURA, ALTURA = 1080, 1350
    # Fundo azul claro inspirado na sua arte original
    fundo = Image.new('RGB', (LARGURA, ALTURA), color=(180, 210, 255))
    draw = ImageDraw.Draw(fundo)

    try:
        font_titulo = ImageFont.truetype("fonte_padrao.ttf", 120)
        font_header = ImageFont.truetype("fonte_padrao.ttf", 60)
        font_destaque = ImageFont.truetype("fonte_padrao.ttf", 90)
        font_texto = ImageFont.truetype("fonte_padrao.ttf", 45)
    except:
        font_titulo = font_header = font_destaque = font_texto = ImageFont.load_default()

    # --- CÁLCULOS MATEMÁTICOS AUTOMÁTICOS ---
    nota_geral = df['Nota Pessoal'].mean() if not df.empty else 0
    
    df_forwards = df[df['Setor'] == 'Forward']
    nota_forwards = df_forwards['Nota Pessoal'].mean() if not df_forwards.empty else 0
    
    df_backs = df[df['Setor'] == 'Back']
    nota_backs = df_backs['Nota Pessoal'].mean() if not df_backs.empty else 0

    # Descobrindo o Ponto Forte e o Ponto Fraco automaticamente
    categorias_taticas = ['Foco', 'Fortaleza', 'Apoio', 'RELOAD', 'Espaço', 'Disciplina', 'Anarquia', 'Reinicio', 'Adaptacao']
    medias_taticas = {cat: df[cat].mean() for cat in categorias_taticas if not df[cat].dropna().empty}
    
    ponto_forte = max(medias_taticas, key=medias_taticas.get) if medias_taticas else "N/A"
    ponto_fraco = min(medias_taticas, key=medias_taticas.get) if medias_taticas else "N/A"

    # --- DESENHO DA ARTE ---
    # Tarja preta lateral estilo caderno
    draw.rectangle([(0, 0), (120, ALTURA)], fill=(20, 40, 80))
    
    # Textos do Cabeçalho
    draw.text((180, 80), "FEEDBACK", font=font_titulo, fill=(0, 0, 0))
    draw.text((180, 220), f"Pós-Jogo vs {adversario}", font=font_header, fill=(100, 100, 100))
    draw.line([(180, 300), (980, 300)], fill=(0, 0, 0), width=5)

    # Notas (Métricas Principais)
    draw.text((180, 400), "Nota Geral do Jogo:", font=font_header, fill=(0, 0, 0))
    draw.text((850, 380), f"{nota_geral:.1f}", font=font_destaque, fill=(20, 40, 80))

    draw.text((180, 520), "Nota Forwards:", font=font_header, fill=(0, 0, 0))
    draw.text((850, 500), f"{nota_forwards:.1f}", font=font_destaque, fill=(20, 40, 80))

    draw.text((180, 640), "Nota Backs:", font=font_header, fill=(0, 0, 0))
    draw.text((850, 620), f"{nota_backs:.1f}", font=font_destaque, fill=(20, 40, 80))

    draw.line([(180, 780), (980, 780)], fill=(0, 0, 0), width=5)

    # Destaques Culturais (Positivo e Negativo)
    draw.text((180, 850), "🟢 Ponto Forte:", font=font_destaque, fill=(0, 100, 0))
    draw.text((180, 950), f"- Atitude em: {ponto_forte}", font=font_texto, fill=(0, 0, 0))

    draw.text((180, 1050), "🔴 Ponto a Melhorar:", font=font_destaque, fill=(150, 0, 0))
    draw.text((180, 1150), f"- Deficiência em: {ponto_fraco}", font=font_texto, fill=(0, 0, 0))

    # Tenta colar o logo no rodapé
    try:
        logo = Image.open("logo_ratacanga.png").convert("RGBA")
        logo.thumbnail((200, 200))
        fundo.paste(logo, (LARGURA//2 - 50, 1100), logo)
    except:
        pass

    nome_arquivo = "resumo_feedback_instagram.jpg"
    fundo.save(nome_arquivo, quality=100)
    return nome_arquivo