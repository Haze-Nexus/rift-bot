import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

class BancoDados:
    SALDO_INICIAL = 20

    def __init__(self):
        self.uri = os.getenv("DATABASE_URL")
        self.client = MongoClient(self.uri)
        self.db = self.client["haze_nexus"]
        self.collection = self.db["usuarios"]

    def alterar_hazium(self, user_id, quantidade):
    # Primeiro tentamos inserir o usuário caso ele não exista
        self.collection.update_one(
            {"_id": user_id},
            {"$setOnInsert": {"hazium": self.SALDO_INICIAL}},
            upsert=True
        )

        self.collection.update_one(
            {"_id": user_id},
            {"$inc": {"hazium": quantidade}}
    )

    def ver_saldo(self, user_id):
        usuario = self.collection.find_one({"_id": user_id})
        if usuario:
            return usuario.get("hazium", self.SALDO_INICIAL)
        return self.SALDO_INICIAL

    def pegar_ranking(self):

        ranking = self.collection.find().sort("hazium", -1).limit(10)

        return [(u["_id"], u["hazium"]) for u in ranking]


db = BancoDados()
