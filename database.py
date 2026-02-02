import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()


class BancoDados:
    SALDO_INICIAL = 20

    def __init__(self):
        # A URL você pega no site do MongoDB Atlas (ex: mongodb+srv://...)
        self.uri = os.getenv("MONGO_URI")
        self.client = MongoClient(self.uri)
        # Define o nome do banco de dados e da coleção (tabela)
        self.db = self.client["haze_nexus"]
        self.collection = self.db["usuarios"]

    def alterar_hazium(self, user_id, quantidade):
        # update_one com upsert=True faz o papel do "INSERT OR IGNORE" e do "UPDATE" ao mesmo tempo
        self.collection.update_one(
            {"_id": user_id},  # Busca pelo ID do usuário
            {
                "$inc": {"hazium": quantidade},  # Incrementa o saldo
                "$setOnInsert": {
                    "hazium": (
                        self.SALDO_INICIAL + quantidade
                        if quantidade < 0
                        else self.SALDO_INICIAL + quantidade
                    )
                },
            },
            upsert=True,  # Se não existir, ele cria
        )
        # Nota: A lógica acima garante que novos usuários comecem com o saldo base + a alteração atual.

    def ver_saldo(self, user_id):
        usuario = self.collection.find_one({"_id": user_id})
        if usuario:
            return usuario.get("hazium", self.SALDO_INICIAL)
        return self.SALDO_INICIAL

    def pegar_ranking(self):
        # Busca todos, ordena pelo hazium de forma decrescente (-1) e limita a 10
        ranking = self.collection.find().sort("hazium", -1).limit(10)
        # Converte para o formato de tupla (user_id, hazium) para manter compatibilidade com seu código antigo
        return [(u["_id"], u["hazium"]) for u in ranking]


db = BancoDados()
