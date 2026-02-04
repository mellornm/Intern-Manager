import requests
import webbrowser
from packaging import version
from PySide6.QtWidgets import QMessageBox
from config import VERSION, REPO_URL


def check_for_updates(parent_window):
    try:
        # Timeout curto para não ficar tentando eternamente se sem internet
        response = requests.get(REPO_URL, timeout=3)

        if response.status_code == 200:
            data = response.json()
            latest_tag = data["tag_name"]  # Ex: "v1.1.0"
            clean_latest = latest_tag.lstrip("v")  # Remove o 'v'

            # Se a versão do GitHub for maior que a local
            if version.parse(clean_latest) > version.parse(VERSION):
                reply = QMessageBox.question(
                    parent_window,
                    "Atualização Disponível",
                    f"A versão {latest_tag} está disponível! Deseja baixar agora?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )

                if reply == QMessageBox.StandardButton.Yes:
                    # Abre a página de releases no navegador padrão
                    webbrowser.open(data["html_url"])

    except Exception as e:
        print(f"Erro ao verificar updates: {e}")
