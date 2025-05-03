from fastapi.testclient import TestClient
from backend.main import app
from backend.services.coworking.openai_request import (
    AIRequestService,
    NoSuchPathException,
)
from backend.services.coworking.students import ActiveUserService
from backend.models.user import User
from datetime import datetime


# from ...models.user import User, NewUser
# import ..test/user_test.py

client = TestClient(app)


class SuccessAIRequestService:
    def determine_request(self, user_prompt: str):
        return "successful AI response!"


class NoSuchPathAIRequestService:
    def determine_request(self, user_prompt: str):
        raise NoSuchPathException()


class ValueErrorAIRequestService:
    def determine_request(self, user_prompt: str):
        raise ValueError()


class GenericErrorAIRequestService:
    def determine_request(self, user_prompt: str):
        raise Exception()


class FakeOpenAIServiceForCheck:
    def prompt(self, system_prompt, user_prompt, response_model):
        class FakeResponse:
            method = "check_user_activity"
            expected_input = "Unreal User"

        return FakeResponse()


class FakeOpenAIServiceCancel:
    def prompt(self, system_prompt, user_prompt, response_model):
        class FakeResponse:
            method = "cancel_reservation"
            expected_input = "2025-05-03 15:00:00"

        return FakeResponse()


class FakeOpenAIService:
    def prompt(self, system_prompt, user_prompt, response_model):
        class FakeResponse:
            method = "check_user_activity"
            expected_input = "Unreal User"

        return FakeResponse()


class FakeUserServiceWithNoMatch:
    """A fake user‐lookup service that never finds anyone."""

    def get_user_by_name(self, name: str):
        # Always return None so ActiveUserService.user_exists(...) is False
        return None


class FakeCourseSiteService:
    """Stub for filling"""

    pass


class FakeSectionService:
    """Stub for SectionService."""

    pass


class FakeReservationService:
    """Fake reservation"""

    def __init__(self):
        self.called = False
        self.called_date = None

    def determine_reservation_to_cancel(self, reservation_date: datetime):
        self.called = True
        self.called_date = reservation_date
        return "Reservation cancelled!"


def test_determine_request_success():
    app.dependency_overrides[AIRequestService] = SuccessAIRequestService
    try:
        response = client.get(
            "/api/ai_request/", params={"user_prompt": "find active users"}
        )
        assert response.status_code == 200
        assert response.json() == "successful AI response!"
    finally:
        app.dependency_overrides = {}


def test_determine_request_no_such_path():
    app.dependency_overrides[AIRequestService] = NoSuchPathAIRequestService
    try:
        response = client.get(
            "/api/ai_request/", params={"user_prompt": "unknown prompt"}
        )
        assert response.status_code == 200
        assert (
            response.json()
            == "The CSXL chat does not currently have any functionality that matches your request. Stay tuned for when you can!"
        )
    finally:
        app.dependency_overrides = {}


def test_determine_request_value_error():
    app.dependency_overrides[AIRequestService] = ValueErrorAIRequestService
    try:
        response = client.get("/api/ai_request/", params={"user_prompt": "bad input"})
        assert response.status_code == 200
        assert (
            response.json()
            == "AI error: please include more information about your request, such as a date or first and last name."
        )
    finally:
        app.dependency_overrides = {}


def test_determine_request_generic_error():
    app.dependency_overrides[AIRequestService] = GenericErrorAIRequestService
    try:
        response = client.get("/api/ai_request/", params={"user_prompt": "error"})
        assert response.status_code == 200
        assert response.json() == "Error"
    finally:
        app.dependency_overrides = {}


def test_check_user_activity_user_not_found():
    fake_logged_in = User(id=1)

    svc = AIRequestService(
        openai_svc=FakeOpenAIServiceForCheck(),
        active_user_svc=ActiveUserService(
            openai_svc=FakeOpenAIService(),
            user_service=FakeUserServiceWithNoMatch(),
            reservation_service=FakeReservationService(),
            course_site_svc=FakeCourseSiteService(),
            section_svc=FakeSectionService(),
        ),
        reservation_svc=FakeReservationService(),
        user=fake_logged_in,
    )

    response = svc.determine_request("is TestUser here?")
    assert (
        response
        == "TestUser does not appear to be a valid user in our system. Please check the name and try again."
    )


def test_check_user_activity_user_found():
    # Check if Sally Student is in XL
    fake_logged_in = User(id=1)

    svc = AIRequestService(
        openai_svc=FakeOpenAIServiceForCheck(),
        active_user_svc=ActiveUserService(
            openai_svc=FakeOpenAIService(),
            user_service=FakeUserServiceWithNoMatch(),
            reservation_service=FakeReservationService(),
            course_site_svc=FakeCourseSiteService(),
            section_svc=FakeSectionService(),
        ),
        reservation_svc=FakeReservationService(),
        user=fake_logged_in,
    )

    response = svc.determine_request("is Sally here?")
    assert response == "Sally is active and currently in Standing Monitor 00."


def test_cancel_single_reservation():
    fake_logged_in = User(id=1)
    svc = AIRequestService(
        openai_svc=FakeOpenAIServiceForCancel(),
        active_user_svc=ActiveUserService(
            openai_svc=FakeOpenAIService(),
            user_service=FakeUserServiceWithNoMatch(),
            reservation_service=FakeReservationService(),
            course_site_svc=FakeCourseSiteService(),
            section_svc=FakeSectionService(),
        ),
        reservation_svc=FakeReservationService(),
        user=fake_logged_in,
    )
    response = svc.determine_request("cancel my reservation")
    assert response == "Reservation cancelled!"


def test_cancel_multiple_reservation():
    """Redefining services to apply to multiple reservations"""
    fake_logged_in = User(id=1)

    class FakeReservationServiceMultiple:
        def __init__(self):
            self.called = False

        def get_current_reservations_for_user(self, subject, focus, state=None):
            # Get two reservations from fake class
            class FakeReservation:
                def __init__(self, start):
                    self.start = start

            # Return fake reservation dates
            return [
                FakeReservation(datetime(2025, 5, 1, 10, 0)),
                FakeReservation(datetime(2025, 5, 2, 11, 0)),
            ]

    def determine_reservation_to_cancel(self, reservation_date):
        # Should be skipped due to multiple reservations
        pytest.skip(
            "determine_reservation_to_cancel should not be invoked for multiple reservations"
        )

    svc = AIRequestService(
        openai_svc=FakeOpenAIServiceForCancel(),
        active_user_svc=ActiveUserService(
            openai_svc=FakeOpenAIService(),
            user_service=FakeUserServiceWithNoMatch(),
            reservation_service=FakeReservationService(),
            course_site_svc=FakeCourseSiteService(),
            section_svc=FakeSectionService(),
        ),
        reservation_svc=FakeReservationServiceMultiple(),
        user=fake_logged_in,
    )
    response = svc.determine_request("cancel my reservation")
    assert (
        response
        == "You have multiple reservations. Please give more information about your reservation so we don't cancel the wrong one!"
    )
