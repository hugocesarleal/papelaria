
## Descrição

Este projeto é um sistema de gestão de vendas desenvolvido em Django para uma papelaria. Ele permite gerenciar itens em estoque, adicionar itens ao carrinho, concluir vendas e gerar comprovantes de pagamento. O sistema também possui um painel de administração para gerenciar vendas e usuários.

Este projeto é o trabalho final da disciplina de Desenvolvimento Web e será utilizado pelo Diretório Central dos Estudantes (DCE) Guy Torres do IFMG *Campus* Bambuí. O sistema será hospedado no site [dceguytorres.com](https://dceguytorres.com).

## Requisitos

- Python 3.8+
- Django 3.2+
- SQLite (ou outro banco de dados de sua preferência)

## Instalação

1. Clone o repositório:

    ```bash
    git clone https://github.com/hugocesarleal/papelaria.git
    cd papelaria
    ```

2. Crie um ambiente virtual e ative-o:

    ```bash
    python -m venv venv
    source venv/bin/activate  # No Windows use `venv\Scripts\activate`
    ```

3. Instale as dependências:

    ```bash
    pip install -r requirements.txt
    ```

4. Configure o arquivo [.env](http://_vscodecontentref_/2) com as variáveis de ambiente necessárias. Use o arquivo `.env.example` como referência.

5. Inicialize o banco de dados:

    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

6. Crie um superusuário para acessar o painel de administração:

    ```bash
    python manage.py createsuperuser
    ```

7. Inicie o servidor de desenvolvimento:

    ```bash
    python manage.py runserver
    ```

8. Acesse o sistema no navegador:

    ```
    http://127.0.0.1:8000/
    ```

## Funcionalidades

- **Gerenciamento de Estoque**: Adicionar, editar e remover itens do estoque.
- **Carrinho de Compras**: Adicionar itens ao carrinho, remover itens e limpar o carrinho.
- **Concluir Venda**: Processar a venda, verificar estoque e gerar comprovantes de pagamento.
- **Painel de Administração**: Gerenciar vendas e usuários, aplicar filtros e visualizar detalhes das vendas.

## Estrutura de Diretórios

- **avisos/**: Gerenciamento de avisos e notificações.
- **clientes/**: Gerenciamento de clientes.
- **config/**: Configurações do projeto.
- **core/**: Funcionalidades centrais e utilitários.
- **duvidas/**: Gerenciamento de dúvidas e suporte.
- **estoque/**: Gerenciamento de itens em estoque.
- **horarios/**: Gerenciamento de horários de funcionamento.
- **media/**: Arquivos de mídia, como comprovantes de pagamento.
- **pontos/**: Gerenciamento de pontos de fidelidade.
- **static/**: Arquivos estáticos, como CSS e JavaScript.
- **usuarios/**: Gerenciamento de usuários.
- **vendas/**: Funcionalidades relacionadas às vendas.