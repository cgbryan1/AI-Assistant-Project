from backend.services.coworking.students import ActiveUserService


class FakeOpenAIService:
    def prompt(self, context, conditional_input, response_model):
        class FakeResponse:
            active_users = {"Fake User": "Room 101"}
            message = "Fake User is in Room 101."

        return FakeResponse()


class FakeUserService:
    pass


class FakeReservationService:
    def list_all_active_and_upcoming_for_rooms(self, user):
        return []

    def list_all_active_and_upcoming_for_xl(self, user):
        return []


class FakeCourseSiteService:
    def get_user_course_sites(self, user):
        return []


class FakeSectionService:
    pass


class FakeUserServiceWithNoMatch:
    def user_exists_by_name(self, name: str) -> bool:
        return False


# Create a fake ActiveUserService instance
active_user_service = ActiveUserService(
    openai_svc=FakeOpenAIService(),
    user_service=FakeUserService(),
    reservation_service=FakeReservationService(),
    course_site_svc=FakeCourseSiteService(),
    section_svc=FakeSectionService(),
)


def test_check_if_active_by_string_success():
    result = active_user_service.check_if_active_by_string("Fake User")
    assert result == "Fake User is in Room 101."
