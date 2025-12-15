# Portal Corporativo Mendonça Galvão Contadores Associados

Single Page Application (SPA) desenvolvida em Flask que centraliza o acesso aos sistemas internos da empresa.

## 📋 Descrição

Este portal corporativo oferece uma interface moderna, minimalista e responsiva para que os colaboradores da Mendonça Galvão Contadores Associados acessem de forma rápida e segura todos os sistemas internos necessários para o trabalho diário.

### Sistemas Integrados

- **Portal do Colaborador**: Gestão de informações pessoais, contracheques, férias e benefícios
- **Sistema de Cálculo de Comissão**: Cálculo automático e transparente de comissões

## 🚀 Tecnologias Utilizadas

- **Backend**: Python 3.x + Flask 3.0.0
- **Frontend**: HTML5, CSS3 (Vanilla), JavaScript (Vanilla)
- **Design**: Mobile-first, responsivo, minimalista corporativo
- **Fontes**: Google Fonts (Inter, Poppins)

## 📁 Estrutura do Projeto

```
portal-mg/
│
├── app.py                          # Aplicação Flask principal
├── requirements.txt                # Dependências Python
├── README.md                       # Este arquivo
│
├── templates/
│   └── index.html                  # Template da landing page
│
└── static/
    ├── css/
    │   ├── reset.css              # CSS reset/normalize
    │   └── styles.css             # Estilos principais
    │
    ├── js/
    │   └── main.js                # JavaScript (FAQ accordion, animações)
    │
    └── img/
        ├── logo-mg.png            # Logo Mendonça Galvão
        ├── logo-nucleo.png        # Logo Núcleo Digital
        ├── icon-portal.svg        # Ícone Portal do Colaborador
        └── icon-comissao.svg      # Ícone Sistema de Comissão
```

## 🔧 Instalação e Execução

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Passo a Passo

1. **Clone ou baixe o projeto**

2. **Navegue até o diretório do projeto**
   ```bash
   cd portal-mg
   ```

3. **Crie um ambiente virtual (recomendado)**
   ```bash
   python -m venv venv
   ```

4. **Ative o ambiente virtual**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

5. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

6. **Execute a aplicação**
   ```bash
   python app.py
   ```

7. **Acesse no navegador**
   ```
   http://localhost:5000
   ```

## 🎨 Customização

### Cores

As cores podem ser ajustadas no arquivo `static/css/styles.css` através das variáveis CSS em `:root`:

```css
:root {
  --bg-primary: #0a0a0a;           /* Fundo escuro principal */
  --accent-yellow: #fbbf24;        /* Botão CTA (amarelo) */
  --accent-blue: #3b82f6;          /* Detalhe Núcleo Digital (azul) */
  --accent-green: #10b981;         /* Detalhe Núcleo Digital (verde) */
  /* ... outras variáveis */
}
```

### Textos

Os textos principais podem ser editados em:
- **app.py**: Dados dos sistemas e FAQ (variáveis `sistemas` e `faq_items`)
- **templates/index.html**: Títulos, descrições e microcópias (procure por comentários `<!-- CUSTOMIZAÇÃO: ... -->`)

### Logos e Ícones

Substitua os arquivos em `static/img/`:
- `logo-mg.png`: Logo principal da empresa (recomendado: 200x50px, PNG transparente)
- `logo-nucleo.png`: Logo Núcleo Digital (recomendado: 300x100px, PNG transparente)
- `icon-portal.svg`: Ícone Portal do Colaborador (recomendado: 64x64px, SVG ou PNG)
- `icon-comissao.svg`: Ícone Sistema de Comissão (recomendado: 64x64px, SVG ou PNG)

### Adicionar Novos Sistemas

Edite o arquivo `app.py` e adicione um novo item no array `sistemas`:

```python
sistemas = [
    # ... sistemas existentes ...
    {
        'id': 'novo-sistema',
        'titulo': 'Nome do Novo Sistema',
        'descricao': 'Descrição do que o sistema faz...',
        'url': 'https://url-do-sistema.com',
        'icone': 'icon-novo-sistema.svg',
        'cta': 'Acessar Sistema'
    }
]
```

## 🌐 Deploy em Produção

### Configurações Importantes

Antes de fazer deploy em produção, altere as seguintes configurações em `app.py`:

```python
# Altere a SECRET_KEY para uma chave segura e única
app.config['SECRET_KEY'] = 'sua-chave-secreta-aqui'

# Desabilite o modo DEBUG
app.config['DEBUG'] = False

# Não execute com app.run() em produção
# Use um servidor WSGI como Gunicorn ou uWSGI
```

### Exemplo com Gunicorn

1. Instale o Gunicorn:
   ```bash
   pip install gunicorn
   ```

2. Execute a aplicação:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

### Variáveis de Ambiente

Para maior segurança, use variáveis de ambiente para configurações sensíveis:

```python
import os
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key')
```

## 📱 Responsividade

O design é **mobile-first** e responsivo, com breakpoints em:
- **Mobile**: < 768px (1 coluna)
- **Tablet**: 768px - 1023px (2 colunas)
- **Desktop**: ≥ 1024px (2 colunas, espaçamentos maiores)

## ♿ Acessibilidade

- Estrutura HTML5 semântica
- Atributos ARIA em elementos interativos
- Contraste de cores adequado (WCAG AA)
- Links externos com `rel="noopener noreferrer"` para segurança
- Navegação por teclado funcional

## 📄 Licença

© 2025 Mendonça Galvão Contadores Associados. Todos os direitos reservados.

## 🆘 Suporte

Para dúvidas ou problemas técnicos, entre em contato:
- **E-mail**: suporte@mgcontadores.com.br
- **Ramal**: 100

---

**Desenvolvido por**: Núcleo Digital MG  
**Data**: Dezembro 2025
