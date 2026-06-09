from quantumbridge.studio.catalog_service import (
    filter_ecosystem_projects,
    get_clean_room_boundary_notice,
    get_project_status_summary,
    list_ecosystem_projects,
    search_ecosystem_projects,
)


def test_catalog_projects_can_be_listed_and_searched():
    projects = list_ecosystem_projects()
    assert len(projects) >= 10
    assert all(project.project_id for project in projects)
    assert search_ecosystem_projects("qiskit")
    assert filter_ecosystem_projects(studio_ready="partial")


def test_catalog_status_and_clean_room_notice():
    summary = get_project_status_summary()
    assert summary["project_count"] >= 10
    assert summary["cloud_access"] is False
    notice = get_clean_room_boundary_notice(list_ecosystem_projects()[0].project_id)
    assert notice["copied_upstream_source"] is False
    assert notice["official_endorsement"] is False
