from app.db.session import SessionLocal
from app.repositories.usuario_repository import UsuarioRepository


def main() -> None:
    with SessionLocal() as db:
        repo = UsuarioRepository(db)
        print("=== USUARIOS EN LA BASE DE DATOS (id, correo, rol, estado) ===")
        for u in repo.list(limit=200):
            print(u.id_usuario, u.correo_electronico, u.rol_id, u.estado)


if __name__ == "__main__":
    main()


