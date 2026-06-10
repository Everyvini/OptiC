import os
from fastapi import FastAPI, Form, HTTPException, responses
from fastapi.responses import HTMLResponse, FileResponse
from supabase import create_client, Client
# Importamos a exceção específica do Supabase para capturar erros de login corretamente
from gotrue.errors import AuthApiError 

app = FastAPI()

# 🛠️ CORREÇÃO 1: URL limpa, sem o "/rest/v1/"
SUPABASE_URL = "https://wcurvwdgezjixosxivfn.supabase.co"

# 🛠️ RECOMENDAÇÃO: Idealmente use a Secret Key aqui se for rodar tudo via backend,
# ou mantenha a publishable se as políticas de RLS permitirem acesso público anônimo.
supabase_key = "INCLUA A CHAVE"

# Inicializa o cliente do Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- ROTAS PARA SERVIR AS PÁGINAS HTML ---

@app.get("/", response_class=HTMLResponse)
def pagina_login():
    """Serve a sua página de login atual"""
    return FileResponse("login.html")

@app.get("/catalogo", response_class=HTMLResponse)
def pagina_catalogo():
    """Serve a sua página de catálogo se o login for bem-sucedido"""
    return FileResponse("catalogo.html")


# --- ROTA DE AUTENTICAÇÃO (BACKEND) ---

@app.post("/auth/login")
def realizar_login(usuario: str = Form(...), senha: str = Form(...)):
    """
    Recebe os dados do formulário HTML, valida no Supabase
    e redireciona para o catálogo em caso de sucesso.
    """
    try:
        # Tenta autenticar o usuário com e-mail e senha
        resposta = supabase.auth.sign_in_with_password({
            "email": usuario, 
            "password": senha
        })
        
        # Se o login foi um sucesso, redireciona o navegador para o catálogo
        return responses.RedirectResponse(url="/catalogo", status_code=303)

    except AuthApiError as auth_err:
        # Captura erros específicos do Supabase (Ex: senha errada, usuário não existe)
        raise HTTPException(
            status_code=401, 
            detail="E-mail ou senha incorretos no sistema."
        )
    except Exception as e:
        # Captura qualquer outro erro inesperado (Ex: falta de conexão com a internet)
        raise HTTPException(
            status_code=500, 
            detail=f"Erro interno no servidor: {str(e)}"
        )

# --- ROTA DOS PRODUTOS ---

@app.get("/api/produtos")
def listar_produtos():
    """Busca os produtos cadastrados na tabela 'produtos'"""
    try:
        dados = supabase.table("produtos").select("*").execute()
        return dados.data
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar produtos: {str(e)}"
        )