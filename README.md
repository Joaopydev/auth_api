# Server API

API serverless em Python baseada em AWS Lambda, empacotada em imagem Docker e orquestrada pelo Serverless Framework.

Atualmente expõe três endpoints principais de autenticação:

- **POST `/signin`** – login
- **POST `/signup`** – cadastro
- **GET `/me`** – dados do usuário autenticado

---

## Stack

- **Linguagem:** Python 3.11  
- **Runtime:** `public.ecr.aws/lambda/python:3.11`  
- **Serverless Framework** (deploy para AWS Lambda + API Gateway HTTP API)  
- **Infra:** AWS Lambda + API Gateway HTTP API  
- **Banco de dados:** configurado via variável de ambiente `DATA_BASE_URL` (ex.: Postgres, MySQL, etc.)  
- **Auth:** JWT (chaves configuradas via env `SECRET_JWT_PRIVATE_KEY` e `SECRET_JWT_PUBLIC_KEY`)  
- **Migrações:** Alembic (`alembic/`)

---

## Arquitetura

Principais diretórios:

- **`src/functions/`**  
  - `signin.py` – handler da função Lambda de login  
  - `signup.py` – handler da função de cadastro  
  - `me.py` – handler da rota autenticada

- **`src/controllers/`**  
  - `SigninController.py`, `SignupController.py`, `MeController.py`  
  - Contêm a lógica de negócio de cada endpoint.

- **`src/utils/`**  
  - `parse_event.py`, `parse_protected_event.py` – parse do evento do API Gateway (body, headers, auth, etc.)  
  - `parse_response.py` – converte a resposta da aplicação em `HTTPResponse` esperado pelo API Gateway  
  - `http.py` – helpers HTTP (por exemplo, respostas de erro `unauthorized`).

- **`src/lib/`**  
  - `jwt.py`, `generate_keys.py` – utilitários de JWT.

- **`src/app_types/http.py`**  
  - Tipos auxiliares para request/response HTTP.

- **`alembic/` + `alembic.ini`**  
  - Configuração e scripts de migração do banco.

---

## Handlers das Lambdas

Cada função Lambda tem um `handler` síncrono que chama um `async_handler` interno:

- **Signin** – `src.functions.signin.handler`  
- **Signup** – `src.functions.signup.handler`  
- **Me** – `src.functions.me.handler`

Esses nomes são usados no `serverless.yml` como comando da imagem:

```yaml
functions:
  signin:
    image:
      uri: <seu-registro>/lambda-container:latest
      command:
        - src.functions.signin.handler
  signup:
    image:
      uri: <seu-registro>/lambda-container:latest
      command:
        - src.functions.signup.handler
  me:
    image:
      uri: <seu-registro>/lambda-container:latest
      command:
        - src.functions.me.handler
```

---

## Variáveis de ambiente

Definidas em `serverless.yml`:

- **`DATA_BASE_URL`** – URL de conexão com o banco (ex.: `postgresql+psycopg2://user:pass@host:5432/db`)  
- **`SECRET_JWT_PRIVATE_KEY`** – chave privada usada para assinar tokens JWT  
- **`SECRET_JWT_PUBLIC_KEY`** – chave pública para validar tokens JWT  

No ambiente local, podem ser configuradas via `.env` ou direto no shell antes do deploy.

---

## Docker

Imagem base definida em `Dockerfile`:

```dockerfile
FROM public.ecr.aws/lambda/python:3.11

COPY requirements.txt ${LAMBDA_TASK_ROOT}/

RUN pip install -r ${LAMBDA_TASK_ROOT}/requirements.txt --target ${LAMBDA_TASK_ROOT}

COPY src/ ${LAMBDA_TASK_ROOT}/src/
```

### Build da imagem

(--platform linux/amd64 --provenance=false) - Torna lambda compatível com imagem docker

```bash 
docker buildx build --platform linux/amd64 --provenance=false -t lambda-container:latest .
```

### Push para o ECR

1. Criar/usar um repositório ECR (ex.: `lambda-container`).  
2. Fazer login no ECR e enviar a imagem:

```bash
# exemplo (ajuste account-id, região e tag)
aws ecr get-login-password --region us-east-1 \
  | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

docker tag lambda-container:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/lambda-container:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/lambda-container:latest
```

3. Atualizar o `uri` da imagem em `serverless.yml` se necessário.

---

## Serverless Framework

### Requisitos

- Node.js + npm/yarn  
- Serverless Framework instalado globalmente:

```bash
npm install -g serverless
```

- AWS CLI configurado (`aws configure`) com credenciais válidas.

### Deploy

Na raiz do projeto:

```bash
serverless deploy
```

O comando vai:

- Criar/atualizar as funções Lambda (`signin`, `signup`, `me`)  
- Configurar o API Gateway HTTP API com as rotas:
  - `POST /signin`
  - `POST /signup`
  - `GET /me`

---

## Endpoints

### `POST /signup`

- **Descrição:** Cria um novo usuário.  
- **Body (JSON):** campos de cadastro de usuário (ex.: `email`, `password`, etc.).  
- **Resposta:** deve retornar dados do usuário criado e/ou token de autenticação (detalhes na `SignupController`).

### `POST /signin`

- **Descrição:** Autentica um usuário.  
- **Body (JSON):** credenciais (ex.: `email`, `password`).  
- **Resposta:** token JWT e, opcionalmente, info básica do usuário.

### `GET /me`

- **Descrição:** Retorna dados do usuário autenticado.  
- **Headers:**  
  - `Authorization: Bearer <token_jwt>`  
- **Respostas:**  
  - `200` – dados do usuário.  
  - `401` – se o token não for enviado ou for inválido:
    - `{"error": "Access token not provided."}`  
    - `{"error": "Invalid access token"}`  

---

## Desenvolvimento local

Existem duas formas principais:

1. **Executar apenas a lógica de negócio** chamando diretamente controladores/funções Python (útil para testes unitários).  
2. **Emular Lambda com Docker** usando a imagem base da AWS (opcionalmente com Lambda Runtime Interface Emulator).

Um fluxo simples:

- Criar virtualenv, instalar dependências:

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```
