# 🧠 Sentiment Analysis API - HeadOffice

API de análise de sentimento em português para conversas de WhatsApp e documentos.

## 📁 Estrutura do Projeto

### **🚀 Arquivos de Produção (Essenciais)**
Necessários para rodar a API:

- `app.py` - Aplicação Flask principal
- `sentiment.py` - Modelo de análise de sentimento (versão otimizada)
- `file_parser.py` - Parser de PDF, DOCX e TXT
- `preload_model.py` - Pré-carregamento do modelo PyTorch
- `requirements.txt` - Dependências Python
- `Dockerfile` - Configuração de build Docker
- `docker-compose.yml` - Orquestração Docker
- `.dockerignore` - Otimização do build
- `run_api.sh` - Script de execução (opcional)

### **📚 Documentação**
- `README.md` - Este arquivo
- `DEPLOY.md` - Instruções de deployment
- `ANALYSIS_REPORT.md` - Relatório de performance do modelo

### **🧪 Scripts de Teste/Desenvolvimento**
Úteis para desenvolvimento mas NÃO necessários em produção:

- `test_client.py` - Cliente de teste da API
- `test_files.py` - Teste de parser de arquivos
- `test_pdf_upload.py` - Teste de upload de PDF
- `test_local.py` - Testes locais do modelo
- `analyze_results.py` - Análise de resultados em lote
- `validate_model.py` - Validação cruzada com ground truth
- `compare_versions.py` - Comparação de versões do modelo
- `mock_wapp_conversations.py` - Gerador de datasets de teste

### **🗑️ Arquivos para DELETAR**
Versões antigas/redundantes:

- ❌ `analise_sentimentos.py` - Versão antiga (substituída por sentiment.py)
- ❌ `sentiment_backup.py` - Backup desnecessário
- ❌ `sentiment_improved.py` - Redundante (já copiado para sentiment.py)
- ❌ `measure_sentiment.py` - Script de teste obsoleto
- ❌ `verify_real_data.py` - Script de verificação obsoleto
- ❌ `Timeline - Clinica da Cidade` - Arquivo de dados de teste
- ❌ `headoffice_ai_exported_data_*.json` - Dados de teste (muito grandes)

### **🚫 Arquivos no .gitignore**
Gerados automaticamente e não devem estar no Git:

- `__pycache__/` - Cache Python
- `*.pyc`, `*.pyo` - Bytecode compilado
- `*.json` - Dados de teste
- `*.csv` - Resultados temporários
- `*.pdf` - Documentos de teste
- `*.lock`, `*~lock*` - Lock files

## 🎯 Como Usar

### **Produção (VPS)**
```bash
git clone https://github.com/ivanegri/Analise-Sentimentos-HeadOffice.git
cd Analise-Sentimentos-HeadOffice
docker-compose up -d --build
```

### **Desenvolvimento/Testes**
```bash
# Gerar dataset de teste
python mock_wapp_conversations.py

# Analisar via API
python analyze_results.py

# Validar performance
python validate_model.py

# Comparar versões
python compare_versions.py
```

## 📊 Performance do Modelo

Veja `ANALYSIS_REPORT.md` para detalhes completos.

**Acurácia Geral**: ~48% (7 níveis de sentimento)

**Por Categoria**:
- Very Negative (0-15): 100%
- Neutral (45-55): 92.7%
- Very Positive (85-100): 100%

## 🔧 Tecnologias

- **Framework**: Flask
- **Modelo**: PyTorch + Pysentimiento (RoBERTa PT-BR)
- **Deploy**: Docker + Gunicorn
- **Parsers**: PyPDF, python-docx
