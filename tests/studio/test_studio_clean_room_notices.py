from quantumbridge.studio.catalog_service import list_ecosystem_projects
from quantumbridge.studio.workflow_registry import list_workflows


def test_studio_clean_room_notices_and_no_official_claims():
    for project in list_ecosystem_projects():
        assert project.provenance["copied_upstream_source"] is False
        assert project.provenance["official_endorsement"] is False
        assert project.provenance["production_ready"] is False
    for workflow in list_workflows():
        joined = "\n".join(workflow.warnings).lower()
        assert "official" in joined
        assert "production" in joined
        assert workflow.production_ready is False
