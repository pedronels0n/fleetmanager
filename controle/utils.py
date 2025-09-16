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

import requests
from datetime import datetime, timedelta

API_URL_TODOS = "https://ws.sisatec.com.br/api/abastecimento"
API_URL_DATA = "https://ws.sisatec.com.br/api/abastecimento/byData"
API_URL_DATA_STATUS = "https://ws.sisatec.com.br/api/abastecimento/byDataAndStatus"

def normalizar_valores(abastecimentos):
    """Converte campos numéricos que vêm como string com vírgula."""
    for item in abastecimentos:
        for campo in ["valor", "valorLitro", "quantidadeLitros"]:
            if campo in item and isinstance(item[campo], str):
                item[campo] = item[campo].replace(",", ".")
    return abastecimentos


def buscar_abastecimentos_recentes():
    """
    Busca apenas os abastecimentos do dia atual.
    """
    hoje = datetime.now()
    data_inicio_str = hoje.strftime("%m-%d-%Y")
    data_fim_str = hoje.strftime("%m-%d-%Y")
    #/@codigo/@key/@dataInicio/@dataFim/@status/@pagina

    url = f"{API_URL_DATA_STATUS}/{API_CODIGO}/{API_KEY}/{data_inicio_str}/{data_fim_str}/2/1"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        dados = response.json()

        # A API retorna lista direta ou dentro de "abastecimentos"
        abastecimentos = dados.get("abastecimentos", dados)

        return normalizar_valores(abastecimentos)

    except Exception as e:
        print(f"Erro ao consultar API (recentes): {e}")
        return []


def buscar_abastecimentos_por_data(data_inicio=None, data_fim=None, dias=30):
    """
    Busca abastecimentos filtrando por intervalo de datas.
    Se não passar datas, usa últimos `dias` (padrão = 30).
    Datas devem vir no formato yyyy-mm-dd.
    """
    try:
        if data_inicio and data_fim:
            data_inicio = datetime.strptime(data_inicio, "%Y-%m-%d")
            data_fim = datetime.strptime(data_fim, "%Y-%m-%d")
        else:
            data_fim = datetime.now()
            data_inicio = data_fim - timedelta(days=dias)

        data_inicio_str = data_inicio.strftime("%m-%d-%Y")
        data_fim_str = data_fim.strftime("%m-%d-%Y")

        url = f"{API_URL_DATA_STATUS}/{API_CODIGO}/{API_KEY}/{data_inicio_str}/{data_fim_str}/2"

        response = requests.get(url, timeout=10)
        response.raise_for_status()
        dados = response.json()

        abastecimentos = dados.get("abastecimentos", dados)

        return normalizar_valores(abastecimentos)

    except Exception as e:
        print(f"Erro ao consultar API (por data): {e}")
        return []




LOGIN_URL = "https://sistema.primebeneficios.com.br/Default.aspx"

def acessar_abastecimento_externo(cod_abastecimento):
    """
    Faz login no site externo e retorna o HTML da página do abastecimento.
    """
    PAGINA_PROTEGIDA = f"https://sistema.primebeneficios.com.br/Admin/PopUp_Consulta_Abastecimento.aspx?id={cod_abastecimento}"

    
    return PAGINA_PROTEGIDA
