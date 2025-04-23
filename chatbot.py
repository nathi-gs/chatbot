from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import re

app = Flask(__name__)

# Estados dos usuários e CNPJs salvos
estado_usuario = {}
cnpjs_usuarios = {}

def validar_cnpj(cnpj):
    padrao = r"^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$|^\d{14}$"
    return re.match(padrao, cnpj)

@app.route("/webhook", methods=["POST"])
def whatsapp():
    numero = request.form.get("From")  # ID do usuário (número do WhatsApp)
    mensagem = request.form.get("Body").strip()
    estado = estado_usuario.get(numero, "inicio")

    resposta = MessagingResponse()

    # Etapa 1: pedir CNPJ
    if estado == "inicio":
        estado_usuario[numero] = "esperando_cnpj"
        resposta.message("Olá! Por favor, informe o CNPJ da empresa para continuar (ex: 12.345.678/0001-99).")
        return str(resposta)

    # Etapa 2: validar e salvar CNPJ
    if estado == "esperando_cnpj":
        if validar_cnpj(mensagem):
            cnpjs_usuarios[numero] = mensagem
            estado_usuario[numero] = "menu_principal"
            resposta.message(
                f"Olá! Eu sou a Nat, assistente virtual financeira. 🤖\n\n"
                f"CNPJ {mensagem} recebido com sucesso! ✅\n\n"
                "Menu principal:\n"
                "1️⃣ Boleto Vencido\n"
                "2️⃣ Dados Bancários\n"
                "3️⃣ Nota Fiscal\n"
                "4️⃣ Falar com atendente"
            )
        else:
            resposta.message("CNPJ inválido. Tente novamente. Ex: 12.345.678/0001-99")
        return str(resposta)

    # Etapa 3: menu principal
    if estado == "menu_principal":
        if mensagem == "1":
            estado_usuario[numero] = "submenu_boleto"
            resposta.message(
                "🧾 Boleto Vencido:\n"
                "1️⃣ Pagamento via Pix\n"
                "2️⃣ Segunda via do boleto\n"
                "3️⃣ TED\n"
                "4️⃣ Voltar ao menu principal"
            )
        elif mensagem == "2":
            estado_usuario[numero] = "submenu_bancos"
            resposta.message(
                "🏦 Escolha o banco para receber os dados:\n"
                "1️⃣ Bradesco\n"
                "2️⃣ Banco do Brasil\n"
                "3️⃣ Voltar ao menu principal"
            )
        elif mensagem == "3":
            estado_usuario[numero] = "submenu_nota_fiscal"
            resposta.message(
                "🧾 Sobre a Nota Fiscal:\n"
                "1️⃣ Não recebi minha nota\n"
                "2️⃣ Enviar nota novamente\n"
                "3️⃣ Voltar ao menu principal"
            )
        elif mensagem == "4":
            resposta.message("👨‍💼 Encaminhando para um atendente... Aguarde um momento.")
        else:
            resposta.message("Escolha uma opção válida de 1 a 4.")
        return str(resposta)

    # Submenu Boleto Vencido
    if estado == "submenu_boleto":
        if mensagem == "1":
            resposta.message("🔗 Chave Pix: ")
        elif mensagem == "2":
            resposta.message("📄 Solicitando a Segunda Via...")
        elif mensagem == "3":
            resposta.message("🏦 Dados para transferência: ")
        elif mensagem == "4":
            estado_usuario[numero] = "menu_principal"
            resposta.message(
                "Menu principal:\n"
                "1️⃣ Boleto Vencido\n"
                "2️⃣ Dados Bancários\n"
                "3️⃣ Nota Fiscal\n"
                "4️⃣ Falar com atendente"
            )
        else:
            resposta.message("Escolha uma opção válida de 1 a 4.")
        return str(resposta)

    # Submenu Dados Bancários
    if estado == "submenu_bancos":
        if mensagem == "1":
            resposta.message("🏦 Bradesco: ")
        elif mensagem == "2":
            resposta.message("🏦 Banco do Brasil: ")
        elif mensagem == "3":
            estado_usuario[numero] = "menu_principal"
            resposta.message(
                "Menu principal:\n"
                "1️⃣ Boleto Vencido\n"
                "2️⃣ Dados Bancários\n"
                "3️⃣ Nota Fiscal\n"
                "4️⃣ Falar com atendente"
            )
        else:
            resposta.message("Escolha uma opção válida de 1 a 3.")
        return str(resposta)

    # Submenu Nota Fiscal
    if estado == "submenu_nota_fiscal":
        if mensagem == "1":
            resposta.message("📭 Vamos verificar o envio. Aguarde um momento.")
        elif mensagem == "2":
            resposta.message("📤 A nota será reenviada para seu e-mail cadastrado.")
        elif mensagem == "3":
            estado_usuario[numero] = "menu_principal"
            resposta.message(
                "Menu principal:\n"
                "1️⃣ Boleto Vencido\n"
                "2️⃣ Dados Bancários\n"
                "3️⃣ Nota Fiscal\n"
                "4️⃣ Falar com atendente"
            )
        else:
            resposta.message("Escolha uma opção válida de 1 a 3.")
        return str(resposta)

    return str(resposta)

if __name__ == "__main__":
    app.run(debug=True)