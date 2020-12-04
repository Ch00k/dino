import logging
from typing import Any, Callable, Dict, List, Tuple

from pynetdicom import AE, ALL_TRANSFER_SYNTAXES, acse, debug_logger, evt
from pynetdicom.events import InterventionEvent
from pynetdicom.presentation import PresentationContext
from pynetdicom.presentation import negotiate_as_acceptor as original_negotiator
from pynetdicom.sop_class import _STORAGE_CLASSES

from dino import config

logging.basicConfig(
    level=logging.DEBUG if config.debug else logging.WARNING,
    format="%(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

if config.debug:
    debug_logger()


# to monkey-patch in order to set ourselves into promiscuous mode, i.e. negotiate that
# we accept any SOP class that the SCU requests
def promiscuous_negotiator(
    requestor_contexts: List[PresentationContext],
    acceptor_contexts: List[PresentationContext],
    roles: Dict[str, Any] = None,
) -> Any:
    acceptor_abstract_syntaxes = [c.abstract_syntax for c in acceptor_contexts]

    counter = 1

    for context in requestor_contexts:
        # TODO: Check for cx.abstract_syntax.is_private?
        if context.abstract_syntax in acceptor_abstract_syntaxes:
            continue

        # We need to mutate the abstract syntax classes dict, because it is being
        # looked up when a DIMSE message is received
        if context.abstract_syntax not in _STORAGE_CLASSES.values():
            _STORAGE_CLASSES[f"PrivateSOPClass{counter}"] = context.abstract_syntax
            counter += 1

        # Add all transfer syntaxes to the context
        context.transfer_syntax = ALL_TRANSFER_SYNTAXES

        # Add our new context the list of our supported contexts
        acceptor_contexts.append(context)

    return original_negotiator(requestor_contexts, acceptor_contexts, roles)


acse.negotiate_as_acceptor = promiscuous_negotiator


def handle_store(event: InterventionEvent, logger: logging.Logger = None) -> int:
    return 0x0000


class SCP:
    def __init__(self, host: str, port: int, ae_title: str):
        self.address = (host, port)
        self.ae = AE(ae_title=ae_title)
        self.create_context()
        self.handlers: List[Tuple] = []

    def create_context(self) -> None:
        for storage_class in _STORAGE_CLASSES.values():
            self.ae.add_supported_context(
                abstract_syntax=storage_class,
                transfer_syntax=ALL_TRANSFER_SYNTAXES,
            )

    def add_handler(
        self, event_type: InterventionEvent, func: Callable, args: Tuple
    ) -> None:
        handler = (event_type, func, args)
        self.handlers.append(handler)

    def start(self, block: bool = True) -> None:
        self.ae.start_server(
            address=self.address,
            block=block,
            evt_handlers=self.handlers,
        )

    def stop(self) -> None:
        self.ae.shutdown()


if __name__ == "__main__":
    scp = SCP(config.scp_host, config.scp_port, config.scp_ae_title)
    scp.add_handler(
        event_type=evt.EVT_C_STORE,
        func=handle_store,
        args=(logging.getLogger("pynetdicom"),),
    )
    scp.start()
