from database import engine
import models

print("A apagar tabelas antigas...")
models.Base.metadata.drop_all(bind=engine)

print("A criar tabelas novas com a estrutura de Barbearias...")
models.Base.metadata.create_all(bind=engine)

print("Banco de dados atualizado com sucesso!")