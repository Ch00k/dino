import itertools
from contextlib import AbstractContextManager
from types import TracebackType
from typing import Any, Optional, Type

from pydicom import Dataset
from pynetdicom import AE, ALL_TRANSFER_SYNTAXES
from pynetdicom.sop_class import _STORAGE_CLASSES


class DICOMStoreException(Exception):
    pass


class SCU(AbstractContextManager):
    def __init__(self, host: str, port: int, ae_title: str) -> None:
        self.host = host
        self.port = port
        self.ae_title = ae_title
        self.association = None

    def __enter__(self) -> Any:
        self.associate()
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        self.disassociate()

    def associate(self) -> None:
        ae = AE()
        self.create_context(ae)
        self.association = ae.associate(
            addr=self.host, port=self.port, ae_title=self.ae_title
        )

    def create_context(self, ae: AE) -> None:
        # TODO: Figure out why providing a list of transfer syntaxes doesn't work
        contexts = itertools.product(_STORAGE_CLASSES, ALL_TRANSFER_SYNTAXES)
        for abstract_syntax, transfer_syntax in contexts:
            ae.add_requested_context(abstract_syntax, transfer_syntax)

    def disassociate(self) -> None:
        if self.association and self.association.is_alive():
            self.association.release()
            self.association = None

    def send(self, dataset: Dataset) -> None:
        if not self.association or not self.association.is_alive():
            self.associate()

        try:
            # TODO: Figure out how to make mypy happy (fuck you mypy!)
            status = self.association.send_c_store(dataset)  # type: ignore
        except Exception as e:
            raise DICOMStoreException(f"Sending {dataset.filename} failed: {e}")
        else:
            # TODO: Can we assume that any non-zero status is an error?
            if not status or status.Status != 0:
                raise DICOMStoreException(
                    f"Sending {dataset.filename} failed: {status}"
                )
