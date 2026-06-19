import unittest
from unittest.mock import MagicMock, patch

import servico
from servico import listar_obras


class TestServico(unittest.TestCase):
    def test_listar_obras(self):
        obra_fake = MagicMock()
        obra_fake.to_dict.return_value = {"id": 1, "titulo": "Obras"}

        session_fake = MagicMock()
        session_fake.scalars.return_value.all.return_value = [obra_fake]

        with patch.object(servico, "SessionLocal", return_value=session_fake):
            resultado = listar_obras()  # sem argumentos!

        self.assertEqual(resultado, [{"id": 1, "titulo": "Obras"}])

# def teste_listar_capitulos():
#     capitulos = listar_capitulos()
#     assert isinstance(capitulos, list)
#     assert all(isinstance(c, dict) for c in capitulos)
# def teste_listar_capitulos_vazia():
#     with pytest.raises(ValueError):
#         raise ValueError("Lista de capítulos está vazia")

# def teste_listar_usuarios():
#     usuarios = listar_usuarios()
#     assert isinstance(usuarios, list)
#     assert all(isinstance(u, dict) for u in usuarios)
# def teste_listar_usuarios_vazia():
#     with pytest.raises(ValueError):
#         raise ValueError("Lista de usuários está vazia")

# def teste_listar_pdf_urls():
#     pdf_urls = listar_pdf_urls()
#     assert isinstance(pdf_urls, list)
#     assert all(isinstance(p, dict) for p in pdf_urls)
# def teste_listar_pdf_urls_vazia():
#     with pytest.raises(ValueError):
#         raise ValueError("Lista de PDF URLs está vazia")

# def teste_buscar_usuario_por_email():
#     # Testa com email existente
#     usuario = buscar_usuario_por_email("test@example.com")
#     assert isinstance(usuario, dict)
#     assert "id" in usuario
#     assert "nome" in usuario
#     assert "email" in usuario
#     assert "senha" in usuario
# def teste_buscar_usuario_por_email_inexistente():
#     with pytest.raises(ValueError):
#         raise ValueError("Usuário não encontrado")
    
# def teste_texto_obrigatorio():
#     with pytest.raises(ValueError):
#         raise ValueError("Texto obrigatório")

# def teste_texto_opcional():
#     try:
#         # Simula um campo opcional
#         valor = None
#         if valor is not None and str(valor).strip() != "":
#             pass  # Campo preenchido, mas não obrigatório
#     except Exception as e:
#         pytest.fail(f"Campo opcional falhou: {e}")



