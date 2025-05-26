import requests
import json
import time


class LumiAPITester:
    """Cliente de teste para a API da Lumi"""

    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session_id = f"test_session_{int(time.time())}"

    def test_connection(self):
        """Testa conexão com a API"""
        try:
            response = requests.get(f"{self.base_url}/")
            print("🔗 Testando conexão...")
            print(f"Status: {response.status_code}")
            print(
                f"Resposta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}"
            )
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Erro na conexão: {e}")
            return False

    def test_chat(self, message):
        """Testa o endpoint de chat"""
        try:
            payload = {"message": message, "session_id": self.session_id}

            print(f"\n💬 Enviando mensagem: {message}")
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                headers={"Content-Type": "application/json"},
            )

            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"🤖 Lumi: {data['response']}")
                return data
            else:
                print(f"❌ Erro: {response.text}")
                return None

        except Exception as e:
            print(f"❌ Erro no chat: {e}")
            return None

    def test_tasks(self):
        """Testa o endpoint de tarefas"""
        try:
            print("\n📋 Obtendo tarefas...")
            response = requests.get(f"{self.base_url}/api/tasks")

            if response.status_code == 200:
                data = response.json()
                print("✅ Tarefas obtidas com sucesso!")
                print(f"Total de tarefas: {len(data['data']['tarefas'])}")
                return data
            else:
                print(f"❌ Erro ao obter tarefas: {response.text}")
                return None

        except Exception as e:
            print(f"❌ Erro: {e}")
            return None

    def run_full_test(self):
        """Executa bateria completa de testes"""
        print("🧪 INICIANDO TESTES DA API LUMI")
        print("=" * 50)

        # Teste de conexão
        if not self.test_connection():
            print("❌ Falha na conexão. Verifique se a API está rodando.")
            return

        # Testes de chat
        messages = [
            "Olá Lumi!",
            "Adicionar tarefa estudar Python para hoje às 14:00",
            "Quais tarefas tenho para hoje?",
            "Como funciona o método Pomodoro?",
        ]

        for msg in messages:
            self.test_chat(msg)
            time.sleep(1)  # Pequena pausa entre requisições

        # Teste de tarefas
        self.test_tasks()

        print("\n✅ Testes concluídos!")


if __name__ == "__main__":
    tester = LumiAPITester()
    tester.run_full_test()
