import requests
from datetime import datetime, timedelta

API_URL = "https://ws.sisatec.com.br/api/abastecimento/byDataAndStatusAndPlaca"
API_CODIGO = "11972"
API_KEY = "BB63614CE75185247F17C7C0FE81FCB0C9FE0E12"

def buscar_abastecimentos(placa, dias=30):
    """
    Consulta os últimos abastecimentos de um veículo pela placa,
    apenas com status = 2, nos últimos `dias` dias.
    """
    data_fim = datetime.now()
    data_inicio = data_fim - timedelta(days=dias)

    # Formato MM-dd-yyyy exigido pela API
    data_inicio_str = data_inicio.strftime("%m-%d-%Y")
    data_fim_str = data_fim.strftime("%m-%d-%Y")

    # Monta a URL com status = 2
    url = f"{API_URL}/{API_CODIGO}/{API_KEY}/{data_inicio_str}/{data_fim_str}/2/{placa}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        dados = response.json()

        # Pega apenas a lista de abastecimentos
        abastecimentos = dados.get("abastecimentos", [])

        # Normalizar valores numéricos
        for item in abastecimentos:
            for campo in ["valor", "valorLitro", "quantidadeLitros"]:
                if campo in item and isinstance(item[campo], str):
                    item[campo] = item[campo].replace(",", ".")
        return abastecimentos
    except Exception as e:
        print(f"Erro ao consultar API: {e}")
        return []
