
from flask import Flask, render_template, request, send_file, redirect, url_for
from fpdf import FPDF
from io import BytesIO
import os

app = Flask(__name__)

FILA = []

# Caminhos dos modelos de fundo
MODELOS = {
    "modelo01.jpg": "static/modelos/modelo01.jpg",
    "modelo02.jpg": "static/modelos/modelo02.jpg",
    "modelo03.jpg": "static/modelos/modelo03.jpg"
}

# Caminho para as fontes personalizadas
FONT_DIR = "static/fonts"

class CartazPDF(FPDF):
    def header(self):
        pass

    def footer(self):
        pass

    def add_oferta(self, item):
        self.add_page()
        self.image(MODELOS[item["modelo"]], x=0, y=0, w=210, h=297)

        # Adiciona fontes personalizadas
        self.add_font("Lobster", "", os.path.join(FONT_DIR, "Lobster-Regular.ttf"), uni=True)
        self.add_font("Pacifico", "", os.path.join(FONT_DIR, "Pacifico-Regular.ttf"), uni=True)
        self.add_font("Bebas", "", os.path.join(FONT_DIR, "BebasNeue-Regular.ttf"), uni=True)
        self.add_font("JustAnotherHand", "", os.path.join(FONT_DIR, "JustAnotherHand-Regular.ttf"), uni=True)
        self.add_font("CaveatBrush", "", os.path.join(FONT_DIR, "CaveatBrush-Regular.ttf"), uni=True)
        self.add_font("Michegar", "", os.path.join(FONT_DIR, "Michegar.ttf"), uni=True)


        # Extrair campos com segurança
        produto = str(item.get("produto", "")).strip().upper()
        preco_normal = str(item.get("preco_normal", ""))
        preco_oferta = str(item.get("preco_oferta", ""))
        tipo = str(item.get("tipo", ""))
        validade = str(item.get("validade", ""))

        # Nome do produto
        partes = produto.split(" ", 1)
        parte1 = partes[0]
        parte2 = partes[1] if len(partes) > 1 else ""

        self.set_font("JustAnotherHand", "", 110)
        self.set_text_color(0, 0, 0)
        self.set_xy(10, 80)
        self.cell(190, 15, parte1, align="C")

        if parte2:
            self.set_font("JustAnotherHand", "", 80)
            self.set_xy(10, 110)
            self.cell(190, 15, parte2, align="C")

        # Preço normal
        self.set_font("JustAnotherHand", "", 32)
        self.set_text_color(0, 0, 0)
        self.set_xy(20, 135)
        self.cell(170, 10, f"de R$ {preco_normal} por", align="L")

        # Preço oferta
        # Preço oferta - separando símbolo, valor e centavos
        try:
            valor_inteiro, centavos = preco_oferta.split(",")
        except ValueError:
            valor_inteiro = preco_oferta
            centavos = ""

        # Definir tamanho da fonte com base no número de dígitos do valor inteiro
        num_digitos = len(valor_inteiro)

        if num_digitos == 1:
            tamanho_valor = 520
        elif num_digitos == 2:
            tamanho_valor = 380
        elif num_digitos == 3:
            tamanho_valor = 160
        else:
            tamanho_valor = 130  # Prevenção para casos maiores

        # R$ pequeno - preto sombra
        # self.set_font("JustAnotherHand", "", 50)
        # self.set_text_color(0, 0, 0)
        # self.set_xy(40, 175)
        # self.cell(0, 0, "R$")

        # R$ pequeno - vermelho frente
        # self.set_text_color(255, 0, 0)
        # self.set_xy(39, 174)
        # self.cell(0, 0, "R$")

        # Valor inteiro grande - preto sombra
        self.set_font("Michegar", "", tamanho_valor)
        self.set_text_color(0, 0, 0)
        self.set_xy(58, 188)
        self.cell(80, 30, valor_inteiro, align="R")

        # Valor inteiro grande - vermelho frente
        self.set_text_color(255, 0, 0)
        self.set_xy(55, 185)
        self.cell(80, 30, valor_inteiro, align="R")

        # Centavos pequenos - preto sombra
        if centavos:
            self.set_font("Michegar", "", 120)
            self.set_text_color(0, 0, 0)
            self.set_xy(142, 175)
            self.cell(0, 0, f",{centavos}")

            # Centavos pequenos - vermelho frente
            self.set_text_color(255, 0, 0)
            self.set_xy(140, 173)
            self.cell(0, 0, f",{centavos}")

        # Unidade - preto sombra
        self.set_font("Michegar", "", 80)
        self.set_text_color(0, 0, 0)
        self.set_xy(11, 221)
        self.cell(175, 15, tipo, align="R")

        # Unidade - branco
        self.set_font("Michegar", "", 80)
        self.set_text_color(255, 255, 255)
        self.set_xy(10, 220)
        self.cell(175, 15, tipo, align="R")

        # Validade
        self.set_font("JustAnotherHand", "", 32)
        self.set_text_color(0, 0, 0)
        self.set_xy(100, 265)
        self.cell(100, 10, f"Oferta válida: {validade}", align="L")

@app.route("/")
def index():
    return render_template("index.html", cartazes=FILA, modelos=MODELOS)

@app.route("/adicionar", methods=["POST"])
def adicionar():
    item = {
        "produto": str(request.form.get("produto", "")),
        "preco_normal": str(request.form.get("preco_normal", "")),
        "preco_oferta": str(request.form.get("preco_oferta", "")),
        "tipo": str(request.form.get("tipo", "")),
        "validade": str(request.form.get("validade", "")),
        "modelo": str(request.form.get("modelo", "modelo01.jpg"))
    }
    FILA.append(item)
    return redirect(url_for("index"))

@app.route("/limpar")
def limpar():
    FILA.clear()
    return redirect(url_for("index"))

@app.route("/gerar")
def gerar():
    pdf = CartazPDF("P", "mm", "A4")
    for item in FILA:
        pdf.add_oferta(item)

    pdf_bytes = pdf.output(dest="S").encode("latin1")
    buffer = BytesIO(pdf_bytes)
    buffer.seek(0)
    return send_file(buffer, as_attachment=False, download_name="cartazes.pdf", mimetype="application/pdf")

if __name__ == "__main__":
    app.run(debug=True)
