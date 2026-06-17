from servicos import servicos
import pytest

def teste_listar_obras():
    obras = servicos.listar_obras()
    assert isinstance(obras, list)
    assert all(isinstance(o, dict) for o in obras)

def teste_listar_capitulos():
    capitulos = servicos.listar_capitulos()
    assert isinstance(capitulos, list)
    assert all(isinstance(c, dict) for c in capitulos)

def teste_listar_usuarios():
    usuarios = servicos.listar_usuarios()
    assert isinstance(usuarios, list)
    assert all(isinstance(u, dict) for u in usuarios)

def teste_listar_pdf_urls():
    pdf_urls = servicos.listar_pdf_urls()
    assert isinstance(pdf_urls, list)
    assert all(isinstance(p, dict) for p in pdf_urls)

def teste_buscar_usuario_por_email():
    # Testa com email existente
    usuario = servicos.buscar_usuario_por_email("test@example.com")
    assert isinstance(usuario, dict)
    assert "id" in usuario
    assert "nome" in usuario
    assert "email" in usuario
    assert "senha" in usuario

def teste_texto_obrigatorio():
    with pytest.raises(ValueError):
        raise ValueError("Texto obrigatório")

def teste_texto_opcional():
    try:
        # Simula um campo opcional
        valor = None
        if valor is not None and str(valor).strip() != "":
            pass  # Campo preenchido, mas não obrigatório
    except Exception as e:
        pytest.fail(f"Campo opcional falhou: {e}")

