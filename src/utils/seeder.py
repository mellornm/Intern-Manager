from services.evaluation_criteria_service import EvaluationCriteriaService
from core.models.evaluation_criteria import EvaluationCriteria


def seed_default_criteria(service: EvaluationCriteriaService):
    """
    Populates the database with a standard set of evaluation criteria.

    This function acts as a database seeder. It first checks if any criteria
    already exist to avoid duplication. If the table is empty, it inserts
    default criteria (e.g., Field Diary, Intervention Action, Meetings)
    to ensure the system is ready for use upon first launch.

    Args:
        service (EvaluationCriteriaService): The service instance used to
            persist the new criteria.
    """
    existing = service.repo.get_all()
    if len(existing) > 0:
        return

    defaults = [
        EvaluationCriteria(
            name="Diário de Campo",
            weight=3.0,
            description="Entrega e avaliação do diário de campo.",
        ),
        EvaluationCriteria(
            name="Ação de Intervenção",
            weight=1.0,
            description="Entrega e avaliação da ação de intervenção.",
        ),
        EvaluationCriteria(
            name="Cumprimento de Prazos",
            weight=1.0,
            description="Entrega de documentos dentro dos prazos indicados.",
        ),
        EvaluationCriteria(
            name="Avaliação do Supervisor Local",
            weight=3.0,
            description="Nota conferida pelo supervisor do local de estágio.",
        ),
        EvaluationCriteria(
            name="Presença em Reuniões",
            weight=2.0,
            description="Presença nas reuniões de estágio.",
        ),
    ]

    for criteria in defaults:
        service.add_new_criteria(criteria)
