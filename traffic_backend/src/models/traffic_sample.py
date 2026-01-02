"""TrafficSample ORM model."""

from __future__ import annotations

import datetime as dt

from sqlalchemy import DateTime, ForeignKey, Integer, BigInteger, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class TrafficSample(Base):
    """Time-series sample of upload/download rates for a modem."""

    __tablename__ = "traffic_samples"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    modem_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("modems.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    timestamp: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    up_bps: Mapped[int] = mapped_column(BigInteger, nullable=False)
    down_bps: Mapped[int] = mapped_column(BigInteger, nullable=False)

    modem = relationship("Modem", back_populates="samples")


Index("ix_samples_modem_time", TrafficSample.modem_id, TrafficSample.timestamp)
