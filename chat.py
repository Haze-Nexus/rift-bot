import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from google.api_core import exceptions
from database import db

# Dicionário para manter o histórico na RAM
memorias = {}


class ChatBotIA:
    @staticmethod
    async def chat(Token, ctx, pergunta):
        user_id = ctx.author.id

        # 1. Verificação de Saldo antes de gastar
        saldo_atual = db.ver_saldo(user_id)
        if saldo_atual < 2:
            return await ctx.send(
                f"❌ {ctx.author.mention}, tu tá zerado guri! Precisa de 2 Hazium pra conversar."
            )

        # 2. Configuração Inicial
        genai.configure(api_key=Token) # type: ignore

        if user_id not in memorias:
            memorias[user_id] = []

        safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }

        # Use o modelo 2.0-flash (o mais atual e rápido)
        model = genai.GenerativeModel(  # type: ignore
            model_name="gemini-2.5-flash-lite",
            system_instruction=(
                "Seu nome é Rift. Você é um bot de Discord brasileiro, confiante, sarcástico e inteligente. "
                "Você ama 'programação' (codar na base da intuição e pressa). "
                "Use gírias como 'tu', 'tmj', 'demorô', 'Frontenzo', 'Reacteiro'. "
                "Se o assunto for sério (debug/ajuda real), pare de brincar e ajude profissionalmente. "
                "Piada interna: 'PJ não tem aposentadoria né papai'"
                "Você usa girias do Mano Deyvin (Influencer)" 
                "Você gosta de ajudar todo mundo da aréa da Tech."
            ),
            safety_settings=safety_settings,
        )

        # 3. Processamento da Mensagem
        async with ctx.typing():
            try:
                # Cobrança do Hazium
                db.alterar_hazium(user_id, -2)
                await ctx.send(
                    f"🪙 **-2 Hazium** | {ctx.author.name}, processando tua dúvida..."
                )

                chat_session = model.start_chat(history=memorias[user_id])
                response = chat_session.send_message(pergunta)

                if not response.candidates or not response.candidates[0].content.parts:
                    return await ctx.send(
                        "Bah, o Google me censurou aqui kkkk. Refaz a pergunta."
                    )

                # Atualiza memória e limita a 10 mensagens (para economizar tokens)
                memorias[user_id] = chat_session.history[-10:]

                # Envia a resposta (cortando se for maior que 2000 caracteres)
                resposta_texto = response.text
                if len(resposta_texto) > 2000:
                    await ctx.send(resposta_texto[:1990] + "...")
                else:
                    await ctx.send(resposta_texto)

            except exceptions.ResourceExhausted:
                await ctx.send("😫 Minha cota gratuita estourou! Espera um minuto aí.")
            except Exception as e:
                print(f"Erro no Chat: {e}")
                await ctx.send(f"Ih, deu erro na minha cabeça de lata: {e}")
