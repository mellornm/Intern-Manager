"""
Dependency Injection Container for Intern Manager Web UI.

Provides pure dependency injection for all repositories and services,
ensuring UI views receive services directly without instantiating
repositories or coupling to data access layers.
"""

from dataclasses import dataclass
from typing import Optional

# Repositories
from repository.document_repo import DocumentRepository
from repository.evaluation_criteria_repo import EvaluationCriteriaRepository
from repository.grade_repo import GradeRepository
from repository.intern_repo import InternRepository
from repository.meeting_repo import MeetingRepository
from repository.observation_repo import ObservationRepository
from repository.venue_repo import VenueRepository
from repository.visit_repo import VisitRepository

# Services
from services.communication_service import CommunicationService
from services.document_service import DocumentService
from services.evaluation_criteria_service import EvaluationCriteriaService
from services.export_service import ExportService
from services.grade_service import GradeService
from services.import_service import ImportService
from services.intern_service import InternService
from services.meeting_service import MeetingService
from services.observation_service import ObservationService
from services.report_service import ReportService
from services.venue_service import VenueService
from services.visit_service import VisitService


@dataclass(frozen=True)
class ServiceContainer:
    """Immutable container holding all domain repositories and services."""

    # Repositories
    repo_venue: VenueRepository
    repo_intern: InternRepository
    repo_doc: DocumentRepository
    repo_obs: ObservationRepository
    repo_criteria: EvaluationCriteriaRepository
    repo_grade: GradeRepository
    repo_meeting: MeetingRepository
    repo_visit: VisitRepository

    # Services
    venue_service: VenueService
    intern_service: InternService
    document_service: DocumentService
    observation_service: ObservationService
    meeting_service: MeetingService
    visit_service: VisitService
    criteria_service: EvaluationCriteriaService
    grade_service: GradeService
    report_service: ReportService
    communication_service: CommunicationService
    import_service: ImportService
    export_service: ExportService


_container: Optional[ServiceContainer] = None


def create_service_container() -> ServiceContainer:
    """
    Builds and wires all application repositories and services using pure dependency injection.
    """
    # 1. Repositories
    repo_venue = VenueRepository()
    repo_intern = InternRepository()
    repo_doc = DocumentRepository()
    repo_obs = ObservationRepository()
    repo_criteria = EvaluationCriteriaRepository()
    repo_grade = GradeRepository()
    repo_meeting = MeetingRepository()
    repo_visit = VisitRepository()

    # 2. Services
    venue_service = VenueService(repo_venue)
    intern_service = InternService(repo_intern)
    document_service = DocumentService(repo_doc)
    observation_service = ObservationService(repo_obs)
    meeting_service = MeetingService(repo_meeting)
    visit_service = VisitService(repo_visit)
    criteria_service = EvaluationCriteriaService(repo_criteria)
    grade_service = GradeService(repo=repo_grade, criteria_repo=repo_criteria)
    report_service = ReportService()
    communication_service = CommunicationService()

    import_service = ImportService(
        intern_service=intern_service,
        venue_service=venue_service,
        document_service=document_service,
    )
    export_service = ExportService()

    return ServiceContainer(
        repo_venue=repo_venue,
        repo_intern=repo_intern,
        repo_doc=repo_doc,
        repo_obs=repo_obs,
        repo_criteria=repo_criteria,
        repo_grade=repo_grade,
        repo_meeting=repo_meeting,
        repo_visit=repo_visit,
        venue_service=venue_service,
        intern_service=intern_service,
        document_service=document_service,
        observation_service=observation_service,
        meeting_service=meeting_service,
        visit_service=visit_service,
        criteria_service=criteria_service,
        grade_service=grade_service,
        report_service=report_service,
        communication_service=communication_service,
        import_service=import_service,
        export_service=export_service,
    )


def get_container() -> ServiceContainer:
    """Returns the globally initialized service container."""
    global _container
    if _container is None:
        _container = create_service_container()
    return _container
