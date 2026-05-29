from database import SessionLocal
import models

def criar_dados_admin():
    db = SessionLocal()
    try:
        # 1. Criar a barbearia com slug admin
        barbearia_admin = models.Barbearia(
            nome="Administração Central",
            slug="admin",
            ativa=True
        )
        db.add(barbearia_admin)
        db.commit()
        db.refresh(barbearia_admin)

        # 2. Criar o usuário admin vinculado à barbearia criada
        usuario_admin = models.Usuario(
            barbearia_id=barbearia_admin.id,
            nome="Admin Principal",
            email="admin@admin.com",
            senha_hash="admin123", # Altere para a senha desejada
            tipo="admin",
            telefone="00000000000"
        )
        db.add(usuario_admin)
        db.commit()
        db.refresh(usuario_admin)

        print(f"Sucesso! Barbearia '{barbearia_admin.slug}' criada (ID: {barbearia_admin.id}).")
        print(f"Usuário '{usuario_admin.email}' (Senha: admin123) criado com tipo '{usuario_admin.tipo}'.")
    
    except Exception as e:
        db.rollback()
        print(f"Erro ao criar registros: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    criar_dados_admin()