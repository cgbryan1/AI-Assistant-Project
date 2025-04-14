# from sqlalchemy import Boolean, Integer, String, DateTime
# from sqlalchemy.orm import Mapped, mapped_column, relationship
# from typing import Self, List
# from datetime import datetime, timezone


# from ..entity_base import EntityBase
# from ...models import User, PublicUser, Students
# from ..article_author_entity import article_author_table
# from ...models.coworking import SeatDetails
# from ...models.coworking.seat import SeatIdentity, Seat
# from .reservation_entity import ReservationEntity


# __authors__ = ["Manasi Chaudhary", "Emma Coye", "Caroline Bryan", "Kathryn Brown"]
# __copyright__ = "Copyright 2023 - 2024"
# __license__ = "MIT"


# class StudentsEntity(EntityBase):
#     """Entity for Students, Story 1"""

#     # Use to store attendance (TODO seperate from AI Log)

#     __tablename__ = "student_attendance"

#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     student_pid: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
#     student_onyen: Mapped[str] = mapped_column(String, unique=True, nullable=False)
#     first_name: Mapped[str] = mapped_column(String, nullable=False)
#     last_name: Mapped[str] = mapped_column(String, nullable=False)

#     # Present/not
#     is_present: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
#     # Ghost mode (TODO -- see if we actually need it)
#     is_ghost_mode: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
#     # Timestamp (TODO not sure if there's eastern version of UTC)
#     last_checked_in: Mapped[datetime] = mapped_column(
#         DateTime, default=datetime.now(timezone.utc), nullable=False
#     )
#     # Reservation information -- TODO
#     reservations: Mapped[List[ReservationEntity]] = relationship(
#         "ReservationEntity", back_populates="student"
#     )

#     def to_model(self) -> Students:
#         # TODO match values to model
#         """Convert entity to model"""
#         return Students(
#             id=self.id,
#             pid=self.student_pid,
#             onyen=self.student_onyen,
#             first_name=self.first_name,
#             last_name=self.last_name,
#             is_present=self.is_present,
#             is_ghost_mode=self.is_ghost_mode,
#             last_checked_in=self.last_checked_in,
#         )

#     @classmethod
#     def from_model(cls, model: Students) -> Self:
#         # TODO match values to model
#         """Create an StudentsEntity from a Students model.

#         Args:
#             model (Students): The model to create the entity from.

#         Returns:
#             Self: The entity (not yet persisted)."""

#         return cls(
#             id=model.id,
#             student_pid=model.pid,
#             student_onyen=model.onyen,
#             first_name=model.first_name,
#             last_name=model.last_name,
#             is_present=model.is_present,
#             is_ghost_mode=model.is_ghost_mode,
#             last_checked_in=model.last_checked_in,
#         )
