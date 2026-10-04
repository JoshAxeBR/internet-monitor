# Internet Monitor

Aplicativo desktop para monitorar o consumo de internet em tempo real, com:
- velocidade de download e upload em KB/s ou MB/s
- histórico de uso em gráfico em tempo real
- interface para escolher a placa de rede
- total consumido durante a sessão

## Requisitos

- Python 3.10+
- Linux, Windows ou macOS

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

## Como funciona

O aplicativo lê os contadores de rede do sistema via `psutil` e calcula a diferença entre amostras para obter a taxa de tráfego em tempo real.

## Observação

O monitor mostra o consumo de dados na rede do computador em tempo real, não o uso de dados do provedor (banda contratada).