from typing import Dict, List, Optional
from collections import deque
import random
from models import ServiceConfig, ServiceMode, SequenceConfig, LogEntry, PendingRequest


class InMemoryStorage:
    def __init__(self):
        self.configs: Dict[str, ServiceConfig] = {
            "payment": ServiceConfig(
                mode=ServiceMode.AUTO_SUCCESS,
                timeout_seconds=30,
                default_response="SUCCESS"
            ),
            "fiscal": ServiceConfig(
                mode=ServiceMode.AUTO_SUCCESS,
                timeout_seconds=30,
                default_response="OK"
            ),
            "kds": ServiceConfig(
                mode=ServiceMode.AUTO_SUCCESS,
                timeout_seconds=30,
                default_response="OK"
            )
        }

        self.logs: deque = deque(maxlen=1000)
        self.pending_requests: Dict[str, PendingRequest] = {}

        # Counters for generating IDs
        self.payment_id_counter = 1809
        self.fiscal_doc_counter = 1
        self.kds_ticket_counter = 1

    def get_config(self, service: str) -> ServiceConfig:
        return self.configs.get(service)

    def update_config(self, service: str, config: ServiceConfig):
        # Generate sequence if needed
        if config.mode == ServiceMode.SEQUENCE and config.sequence_config:
            sequence = (
                ["SUCCESS"] * config.sequence_config.success_count +
                ["FAILURE"] * config.sequence_config.failure_count
            )
            random.shuffle(sequence)
            config.sequence_config.remaining = sequence

        self.configs[service] = config

    def get_all_configs(self) -> Dict[str, ServiceConfig]:
        return self.configs

    def add_log(self, log: LogEntry):
        self.logs.append(log)

    def get_logs(self, limit: int = 100) -> List[LogEntry]:
        return list(self.logs)[-limit:]

    def add_pending_request(self, request: PendingRequest):
        self.pending_requests[request.request_id] = request

    def get_pending_request(self, request_id: str) -> Optional[PendingRequest]:
        return self.pending_requests.get(request_id)

    def remove_pending_request(self, request_id: str):
        if request_id in self.pending_requests:
            del self.pending_requests[request_id]

    def get_next_payment_id(self) -> int:
        self.payment_id_counter += 1
        return self.payment_id_counter

    def get_next_fiscal_doc_number(self) -> str:
        doc_num = f"FD-TEST-{self.fiscal_doc_counter:04d}"
        self.fiscal_doc_counter += 1
        return doc_num

    def get_next_kds_ticket_id(self) -> str:
        ticket_id = f"KDS-TEST-{self.kds_ticket_counter:04d}"
        self.kds_ticket_counter += 1
        return ticket_id

    def get_next_sequence_response(self, service: str) -> Optional[str]:
        config = self.configs.get(service)
        if not config or not config.sequence_config or not config.sequence_config.remaining:
            return None

        response = config.sequence_config.remaining.pop(0)

        # Regenerate sequence if empty
        if not config.sequence_config.remaining:
            sequence = (
                ["SUCCESS"] * config.sequence_config.success_count +
                ["FAILURE"] * config.sequence_config.failure_count
            )
            random.shuffle(sequence)
            config.sequence_config.remaining = sequence

        return response


# Global storage instance
storage = InMemoryStorage()
