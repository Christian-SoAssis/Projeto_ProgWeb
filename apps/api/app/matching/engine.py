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

try:
    import lightgbm as lgb
except ImportError:
    lgb = None
    logger.warning("LightGBM não está instalado. LTR Matching Engine desativado.")


class MatchingEngine:
    """Interface do motor de matching LightGBM."""

    def __init__(self):
        self.model = None
        self._ready = False
        self.mock_mode = False

    def is_ready(self) -> bool:
        """Retorna True se o modelo LTR está treinado e pronto (ou em modo mock)."""
        if self.mock_mode:
            return True
        return self._ready and self.model is not None and lgb is not None

    def load_model(self, model_file_path: str) -> None:
        """Carrega o modelo do caminho especificado."""
        if lgb is None:
            raise RuntimeError("LightGBM não está instalado. Não é possível carregar o modelo.")
        try:
            self.model = lgb.Booster(model_file=model_file_path)
            self._ready = True
            logger.info(f"Modelo LTR carregado com sucesso de {model_file_path}")
        except Exception as e:
            self._ready = False
            self.model = None
            logger.error(f"Erro ao carregar modelo LTR de {model_file_path}: {e}")
            raise RuntimeError(f"Falha ao carregar modelo LTR: {e}") from e

    def score(self, features: List[dict]) -> List[float]:
        """
        Pontua lista de candidatos com o modelo LTR.
        Retorna lista de scores na mesma ordem.

        Raises:
            RuntimeError: se modelo não está pronto
            ValueError: se features inválidas ou vazias
        """
        from opentelemetry import trace
        tracer = trace.get_tracer(__name__)

        with tracer.start_as_current_span("ltr_scoring") as span:
            span.set_attribute("ltr.candidates_count", len(features) if features else 0)
            span.set_attribute("ltr.mock_mode", self.mock_mode)

            if not self.is_ready():
                raise RuntimeError("Modelo LTR não está pronto. Use matching v0.")

            if not features:
                raise ValueError("A lista de features não pode estar vazia.")

            # Validação básica de features: cada candidato deve ser um dicionário
            for i, feat in enumerate(features):
                if not isinstance(feat, dict):
                    raise ValueError(f"Feature na posição {i} deve ser um dicionário, recebeu {type(feat)}")

            if self.mock_mode:
                scores = []
                for feat in features:
                    score_val = feat.get("mock_score")
                    if score_val is None:
                        # calcula pontuação fictícia
                        score_val = float(feat.get("experience_years", 0)) * 0.1 + float(feat.get("rating", 0)) * 0.5
                    scores.append(float(score_val))
                return scores

            try:
                feature_names = self.model.feature_name()
                data = []
                for feat in features:
                    row = []
                    for name in feature_names:
                        val = feat.get(name)
                        row.append(float(val) if val is not None else 0.0)
                    data.append(row)

                predictions = self.model.predict(data)
                return [float(p) for p in predictions]
            except Exception as e:
                logger.error(f"Erro durante a predição LTR: {e}")
                raise RuntimeError(f"Erro ao processar predição do modelo LTR: {e}") from e


# Instância singleton do engine
matching_engine = MatchingEngine()
