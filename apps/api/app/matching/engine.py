"""
Matching Engine — LightGBM LTR (Learning to Rank)

STATUS: Stub — aguardando dados de treinamento (>= 500 contratos).
Ativação automática quando get_contracts_count() >= 500.
"""
import logging
from typing import List

logger = logging.getLogger(__name__)

# Threshold para ativar LTR (substituir matching v0)
LTR_MIN_CONTRACTS = 500


class MatchingEngine:
    """Interface do motor de matching LightGBM."""

    def __init__(self):
        self.model = None
        self._ready = False

    def is_ready(self) -> bool:
        """Retorna True se o modelo LTR está treinado e pronto."""
        return self._ready and self.model is not None

    def score(self, features: List[dict]) -> List[float]:
        """
        Pontua lista de candidatos com o modelo LTR.
        Retorna lista de scores na mesma ordem.

        Raises:
            RuntimeError: se modelo não está pronto
            ValidationError: se features inválidas
        """
        if not self.is_ready():
            raise RuntimeError("Modelo LTR não está pronto. Use matching v0.")
        # TODO: implementar após treinamento com dados reais
        raise NotImplementedError("LTR v1 pendente de dados de treinamento")


# Instância singleton do engine
matching_engine = MatchingEngine()
