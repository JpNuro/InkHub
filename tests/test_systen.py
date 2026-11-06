#python -m pytest
"""Testes unitários dos serviços de consulta e cadastro do InkHub."""

# Ferramentas para simular sessões e dependências do SQLAlchemy sem banco real.
import unittest
from unittest.mock import MagicMock, patch

import servico


class TestServico(unittest.TestCase):
    """Verifica resultados, persistência e validações da camada de serviços."""

    def _session_com_lista(self, objetos):
        """Cria uma sessão simulada que retorna a lista recebida."""
        session = MagicMock()
        session.scalars.return_value.all.return_value = objetos
        return session

    def test_listar_obras(self):
        """A listagem de obras serializa cada modelo por meio de to_dict."""
        obra_fake = MagicMock()
        obra_fake.to_dict.return_value = {"id": 1, "titulo": "Obra 1"}
        session = self._session_com_lista([obra_fake])

        with patch.object(servico, "SessionLocal", return_value=session):
            resultado = servico.listar_obras()

        self.assertEqual(resultado, [{"id": 1, "titulo": "Obra 1"}])

    def test_listar_capitulos(self):
        """A listagem de capítulos retorna os modelos serializados."""
        capitulo_fake = MagicMock()
        capitulo_fake.to_dict.return_value = {"id": 2, "titulo": "Capítulo 1"}
        session = self._session_com_lista([capitulo_fake])

        with patch.object(servico, "SessionLocal", return_value=session):
            resultado = servico.listar_capitulos()

        self.assertEqual(resultado, [{"id": 2, "titulo": "Capítulo 1"}])

    def test_listar_usuarios(self):
        """A listagem de usuários retorna os modelos serializados."""
        usuario_fake = MagicMock()
        usuario_fake.to_dict.return_value = {"id": 3, "nome": "Ana"}
        session = self._session_com_lista([usuario_fake])

        with patch.object(servico, "SessionLocal", return_value=session):
            resultado = servico.listar_usuarios()

        self.assertEqual(resultado, [{"id": 3, "nome": "Ana"}])

    def test_listar_pdf_urls(self):
        """A listagem de PDFs retorna os registros serializados."""
        pdf_fake = MagicMock()
        pdf_fake.to_dict.return_value = {"id": 4, "url": "https://exemplo.com/a.pdf"}
        session = self._session_com_lista([pdf_fake])

        with patch.object(servico, "SessionLocal", return_value=session):
            resultado = servico.listar_pdf_urls()

        self.assertEqual(resultado, [{"id": 4, "url": "https://exemplo.com/a.pdf"}])

    def test_buscar_usuario_por_email_encontrado(self):
        """A busca por e-mail inclui os dados necessários à autenticação."""
        usuario_fake = MagicMock()
        usuario_fake.id = 7
        usuario_fake.nome = "Carlos"
        usuario_fake.email = "carlos@test.com"
        usuario_fake.senha = "hash123"

        session = MagicMock()
        session.scalar.return_value = usuario_fake

        with patch.object(servico, "SessionLocal", return_value=session):
            resultado = servico.buscar_usuario_por_email("carlos@test.com")

        self.assertEqual(
            resultado,
            {
                "id": 7,
                "nome": "Carlos",
                "email": "carlos@test.com",
                "senha": "hash123",
            },
        )

    def test_buscar_usuario_por_email_inexistente(self):
        """A busca retorna None quando não há usuário para o e-mail."""
        session = MagicMock()
        session.scalar.return_value = None

        with patch.object(servico, "SessionLocal", return_value=session):
            resultado = servico.buscar_usuario_por_email("naoexiste@test.com")

        self.assertIsNone(resultado)

    def test_cadastrar_usuario(self):
        """O cadastro salva usuário, faz hash da senha e confirma a transação."""
        usuario_fake = MagicMock()
        usuario_fake.to_dict.return_value = {
            "id": 10,
            "nome": "Maria",
            "email": "maria@test.com",
        }

        session = MagicMock()

        with (
            patch.object(servico, "SessionLocal", return_value=session),
            patch.object(servico, "Usuario", return_value=usuario_fake),
            patch.object(servico, "generate_password_hash", return_value="hash_maria") as hash_mock,
        ):
            resultado = servico.cadastrar_usuario(
                {"nome": "Maria", "email": "maria@test.com", "senha": "123456"}
            )

        self.assertEqual(
            resultado,
            {"id": 10, "nome": "Maria", "email": "maria@test.com"},
        )
        hash_mock.assert_called_once_with("123456")
        session.add.assert_called_once_with(usuario_fake)
        session.commit.assert_called_once()
        session.refresh.assert_called_once_with(usuario_fake)

    def test_cadastrar_obra(self):
        """O cadastro de obra valida o autor e persiste os metadados."""
        autor_fake = MagicMock()
        autor_fake.id = 99

        obra_fake = MagicMock()
        obra_fake.to_dict.return_value = {
            "id": 1,
            "titulo": "Nova Obra",
            "autor_id": 99,
        }

        session = MagicMock()
        session.get.return_value = autor_fake

        with (
            patch.object(servico, "SessionLocal", return_value=session),
            patch.object(servico, "Obra", return_value=obra_fake),
        ):
            resultado = servico.cadastrar_obra(
                {
                    "titulo_obra": "Nova Obra",
                    "autor_id": "99",
                    "categoria": "Romance",
                    "ano": "2024",
                    "editora": "Editora X",
                }
            )

        self.assertEqual(
            resultado,
            {"id": 1, "titulo": "Nova Obra", "autor_id": 99},
        )
        session.get.assert_called_once_with(servico.Usuario, 99)
        session.add.assert_called_once_with(obra_fake)
        session.commit.assert_called_once()
        session.refresh.assert_called_once_with(obra_fake)

    def test_cadastrar_capitulo(self):
        """O cadastro de capítulo valida obra e retorna o registro criado."""
        obra_fake = MagicMock()
        obra_fake.id = 5
        obra_fake.autor_id = 10

        capitulo_fake = MagicMock()
        capitulo_fake.to_dict.return_value = {
            "id": 8,
            "titulo": "Capítulo 1",
            "numero": 1,
            "obra_id": 5,
        }

        session = MagicMock()
        session.get.return_value = obra_fake

        with (
            patch.object(servico, "SessionLocal", return_value=session),
            patch.object(servico, "Capitulo", return_value=capitulo_fake),
        ):
            resultado = servico.cadastrar_capitulo(
                {
                    "titulo_capitulo": "Capítulo 1",
                    "numero_capitulo": "1",
                    "obra_id": "5",
                    "usuario_id": "10",
                }
            )

        self.assertEqual(
            resultado,
            {"id": 8, "titulo": "Capítulo 1", "numero": 1, "obra_id": 5},
        )
        session.get.assert_called_once_with(servico.Obra, 5)
        session.add.assert_called_once_with(capitulo_fake)
        session.commit.assert_called_once()
        session.refresh.assert_called_once_with(capitulo_fake)

    def test_cadastrar_pdf_url(self):
        """O cadastro de PDF relaciona URL, obra e capítulo."""
        obra_fake = MagicMock()
        obra_fake.id = 12

        capitulo_fake = MagicMock()
        capitulo_fake.obra_id = 12

        pdf_fake = MagicMock()
        pdf_fake.to_dict.return_value = {
            "id": 15,
            "url": "https://cdn.exemplo.com/arquivo.pdf",
            "obra_id": 12,
            "capitulo_id": 3,
        }

        session = MagicMock()
        session.get.side_effect = [obra_fake, capitulo_fake]

        with (
            patch.object(servico, "SessionLocal", return_value=session),
            patch.object(servico, "PdfUrl", return_value=pdf_fake),
        ):
            resultado = servico.cadastrar_pdf_url(
                {
                    "url": "https://cdn.exemplo.com/arquivo.pdf",
                    "obra_id": "12",
                    "capitulo_id": "3",
                }
            )

        self.assertEqual(
            resultado,
            {
                "id": 15,
                "url": "https://cdn.exemplo.com/arquivo.pdf",
                "obra_id": 12,
                "capitulo_id": 3,
            },
        )
        session.add.assert_called_once_with(pdf_fake)
        session.commit.assert_called_once()
        session.refresh.assert_called_once_with(pdf_fake)

    def test_cadastrar_obra_erro_autor_inexistente(self):
        """Uma obra não pode referenciar autor inexistente."""
        session = MagicMock()
        session.get.return_value = None

        with patch.object(servico, "SessionLocal", return_value=session):
            with self.assertRaises(ValueError):
                servico.cadastrar_obra(
                    {
                        "titulo_obra": "Sem autor",
                        "autor_id": "999",
                    }
                )

    def test_cadastrar_capitulo_erro_sem_permissao(self):
        """Usuário que não é dono da obra não pode criar capítulo nela."""
        obra_fake = MagicMock()
        obra_fake.id = 5
        obra_fake.autor_id = 11

        session = MagicMock()
        session.get.return_value = obra_fake

        with patch.object(servico, "SessionLocal", return_value=session):
            with self.assertRaises(ValueError):
                servico.cadastrar_capitulo(
                    {
                        "titulo_capitulo": "Cap 1",
                        "numero_capitulo": "1",
                        "obra_id": "5",
                        "usuario_id": "10",
                    }
                )

    def test_cadastrar_pdf_url_erro_obra_invalida(self):
        """O PDF não é salvo quando sua obra não existe."""
        session = MagicMock()
        session.get.return_value = None

        with patch.object(servico, "SessionLocal", return_value=session):
            with self.assertRaises(ValueError):
                servico.cadastrar_pdf_url(
                    {
                        "url": "https://cdn.exemplo.com/a.pdf",
                        "obra_id": "999",
                    }
                )

    def test_cadastrar_usuario_erro_nome_obrigatorio(self):
        """Nome em branco deve ser rejeitado no cadastro de usuário."""
        with self.assertRaises(ValueError):
            servico.cadastrar_usuario({"nome": "   ", "email": "x@test.com", "senha": "123"})

    def test_cadastrar_obra_erro_titulo_obrigatorio(self):
        """Título em branco deve ser rejeitado no cadastro de obra."""
        with self.assertRaises(ValueError):
            servico.cadastrar_obra({
                "titulo_obra": "   ",
                "autor_id": "1"
            })

    def test_cadastrar_obra_erro_autor_nao_inteiro(self):
        """Identificador de autor que não é inteiro deve ser rejeitado."""
        with self.assertRaises(ValueError):
            servico.cadastrar_obra({
                "titulo_obra": "Obra",
                "autor_id": "abc"
            })

    def test_cadastrar_capitulo_erro_usuario_id_invalido(self):
        """Identificador de usuário inválido deve impedir o cadastro do capítulo."""
        obra_fake = MagicMock()
        obra_fake.id = 5
        obra_fake.autor_id = 10

        session = MagicMock()
        session.get.return_value = obra_fake

        with patch.object(servico, "SessionLocal", return_value=session):
            with self.assertRaises(ValueError):
                servico.cadastrar_capitulo(
                    {
                        "titulo_capitulo": "Capítulo 1",
                        "numero_capitulo": "1",
                        "obra_id": "5",
                        "usuario_id": "abc",
                    }
                )

    def test_cadastrar_pdf_url_erro_url_obrigatoria(self):
        """URL vazia não pode ser cadastrada como arquivo PDF."""
        with self.assertRaises(ValueError):
            servico.cadastrar_pdf_url({
                "url": "   ",
                "obra_id": "1"
            })

    def test_cadastrar_pdf_url_erro_capitulo_nao_pertence_a_obra(self):
        """O cadastro rejeita capítulo que não exista ou não pertença à obra."""
        obra_fake = MagicMock()
        obra_fake.id = 1

        capitulo_fake = None
        session = MagicMock()
        session.get.side_effect = [obra_fake, capitulo_fake]

        with patch.object(servico, "SessionLocal", return_value=session):
            with self.assertRaises(ValueError):
                servico.cadastrar_pdf_url(
                    {
                        "url": "https://cdn.exemplo.com/a.pdf",
                        "obra_id": "1",
                        "capitulo_id": "99",
                    }
                )


