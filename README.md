# devops-ci-cd

Projeto-laboratório para estudar e praticar conceitos de **DevOps**, **Integração Contínua (CI)** e **Entrega Contínua (CD)** usando Python, Makefile, pytest e automação com GitHub.

## Estrutura inicial

```
devops-ci-cd/
├── 01-dev-desktop-local/
│   ├── app.py
│   ├── test_app.py
│   ├── requirements.txt
│   └── Makefile
├── .gitignore
└── README.md
```

## Como rodar localmente

```bash
cd 01-dev-desktop-local
python3 -m venv .venv
source .venv/bin/activate
make install
make test
```

## Comandos úteis (Makefile)

- `make install` — instala as dependências listadas em `requirements.txt`
- `make test` — executa os testes automatizados

## Requisitos

- Python 3.8+
- [Git](https://git-scm.com/)
- [GitHub CLI (gh)](https://cli.github.com/) (opcional, para automatizar criação do repositório)

## Próximos passos

- Adicionar workflows de CI/CD (ex: GitHub Actions)
- Incluir exemplos de deploy
- Explorar Docker, Kubernetes, etc

---
