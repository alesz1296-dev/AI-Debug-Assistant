from collections import defaultdict
from threading import Lock


class MetricsRegistry:
    def __init__(self) -> None:
        self._lock = Lock()
        self.reset()

    def reset(self) -> None:
        with self._lock:
            self.http_requests_total: dict[tuple[str, str, str], int] = defaultdict(int)
            self.http_request_latency_ms_sum: dict[tuple[str, str], float] = defaultdict(float)
            self.http_request_latency_ms_count: dict[tuple[str, str], int] = defaultdict(int)
            self.readiness_checks_total: dict[str, int] = defaultdict(int)
            self.readiness_degraded_total: dict[str, int] = defaultdict(int)
            self.query_requests_total = 0
            self.query_latency_ms_sum = 0.0
            self.query_latency_ms_count = 0
            self.query_retrieval_hits_total = 0
            self.query_confidence_sum = 0.0
            self.query_confidence_count = 0
            self.ingestion_enqueue_success_total: dict[str, int] = defaultdict(int)
            self.ingestion_queue_unavailable_total: dict[tuple[str, str], int] = defaultdict(int)
            self.ingestion_jobs_processed_total: dict[tuple[str, str], int] = defaultdict(int)
            self.evaluation_runs_total = 0
            self.evaluation_runs_passed_total = 0
            self.evaluation_runs_failed_total = 0
            self.evaluation_weak_evidence_warning_total = 0
            self.evaluation_no_evidence_warning_total = 0

    def record_http_request(
        self,
        method: str,
        path: str,
        status_code: int,
        latency_ms: float,
    ) -> None:
        with self._lock:
            status = str(status_code)
            self.http_requests_total[(method, path, status)] += 1
            self.http_request_latency_ms_sum[(method, path)] += latency_ms
            self.http_request_latency_ms_count[(method, path)] += 1

    def record_readiness_check(self, status: str, degraded_reasons: list[str]) -> None:
        with self._lock:
            self.readiness_checks_total[status] += 1
            for reason in degraded_reasons:
                self.readiness_degraded_total[reason] += 1

    def record_query(self, latency_ms: int, citations_count: int, confidence: float) -> None:
        with self._lock:
            self.query_requests_total += 1
            self.query_latency_ms_sum += latency_ms
            self.query_latency_ms_count += 1
            self.query_retrieval_hits_total += citations_count
            self.query_confidence_sum += confidence
            self.query_confidence_count += 1

    def record_ingestion_enqueue_success(self, kind: str) -> None:
        with self._lock:
            self.ingestion_enqueue_success_total[kind] += 1

    def record_ingestion_queue_unavailable(self, operation: str, kind: str) -> None:
        with self._lock:
            self.ingestion_queue_unavailable_total[(operation, kind)] += 1

    def record_ingestion_job_processed(self, kind: str, status: str) -> None:
        with self._lock:
            self.ingestion_jobs_processed_total[(kind, status)] += 1

    def record_evaluation(
        self,
        passed: bool,
        weak_evidence_case_warning_rate: float,
        no_evidence_case_warning_rate: float,
    ) -> None:
        with self._lock:
            self.evaluation_runs_total += 1
            if passed:
                self.evaluation_runs_passed_total += 1
            else:
                self.evaluation_runs_failed_total += 1
            if weak_evidence_case_warning_rate > 0:
                self.evaluation_weak_evidence_warning_total += 1
            if no_evidence_case_warning_rate > 0:
                self.evaluation_no_evidence_warning_total += 1

    def render_prometheus(self) -> str:
        with self._lock:
            lines: list[str] = []
            lines.extend(
                [
                    "# TYPE enterprise_ai_http_requests_total counter",
                    *[
                        (
                            'enterprise_ai_http_requests_total'
                            f'{{method="{method}",path="{path}",status_code="{status}"}} {count}'
                        )
                        for (method, path, status), count in sorted(
                            self.http_requests_total.items()
                        )
                    ],
                    "# TYPE enterprise_ai_http_request_latency_ms_sum counter",
                    *[
                        (
                            'enterprise_ai_http_request_latency_ms_sum'
                            f'{{method="{method}",path="{path}"}} {value}'
                        )
                        for (method, path), value in sorted(
                            self.http_request_latency_ms_sum.items()
                        )
                    ],
                    "# TYPE enterprise_ai_http_request_latency_ms_count counter",
                    *[
                        (
                            'enterprise_ai_http_request_latency_ms_count'
                            f'{{method="{method}",path="{path}"}} {count}'
                        )
                        for (method, path), count in sorted(
                            self.http_request_latency_ms_count.items()
                        )
                    ],
                    "# TYPE enterprise_ai_readiness_checks_total counter",
                    *[
                        (
                            'enterprise_ai_readiness_checks_total'
                            f'{{status="{status}"}} {count}'
                        )
                        for status, count in sorted(self.readiness_checks_total.items())
                    ],
                    "# TYPE enterprise_ai_readiness_degraded_total counter",
                    *[
                        (
                            'enterprise_ai_readiness_degraded_total'
                            f'{{reason="{reason}"}} {count}'
                        )
                        for reason, count in sorted(self.readiness_degraded_total.items())
                    ],
                    "# TYPE enterprise_ai_query_requests_total counter",
                    f"enterprise_ai_query_requests_total {self.query_requests_total}",
                    "# TYPE enterprise_ai_query_latency_ms_sum counter",
                    f"enterprise_ai_query_latency_ms_sum {self.query_latency_ms_sum}",
                    "# TYPE enterprise_ai_query_latency_ms_count counter",
                    f"enterprise_ai_query_latency_ms_count {self.query_latency_ms_count}",
                    "# TYPE enterprise_ai_query_retrieval_hits_total counter",
                    f"enterprise_ai_query_retrieval_hits_total {self.query_retrieval_hits_total}",
                    "# TYPE enterprise_ai_query_confidence_sum counter",
                    f"enterprise_ai_query_confidence_sum {self.query_confidence_sum}",
                    "# TYPE enterprise_ai_query_confidence_count counter",
                    f"enterprise_ai_query_confidence_count {self.query_confidence_count}",
                    "# TYPE enterprise_ai_ingestion_enqueue_success_total counter",
                    *[
                        (
                            'enterprise_ai_ingestion_enqueue_success_total'
                            f'{{kind="{kind}"}} {count}'
                        )
                        for kind, count in sorted(self.ingestion_enqueue_success_total.items())
                    ],
                    "# TYPE enterprise_ai_ingestion_queue_unavailable_total counter",
                    *[
                        (
                            'enterprise_ai_ingestion_queue_unavailable_total'
                            f'{{operation="{operation}",kind="{kind}"}} {count}'
                        )
                        for (operation, kind), count in sorted(
                            self.ingestion_queue_unavailable_total.items()
                        )
                    ],
                    "# TYPE enterprise_ai_ingestion_jobs_processed_total counter",
                    *[
                        (
                            'enterprise_ai_ingestion_jobs_processed_total'
                            f'{{kind="{kind}",status="{status}"}} {count}'
                        )
                        for (kind, status), count in sorted(
                            self.ingestion_jobs_processed_total.items()
                        )
                    ],
                    "# TYPE enterprise_ai_evaluation_runs_total counter",
                    f"enterprise_ai_evaluation_runs_total {self.evaluation_runs_total}",
                    "# TYPE enterprise_ai_evaluation_runs_passed_total counter",
                    (
                        "enterprise_ai_evaluation_runs_passed_total "
                        f"{self.evaluation_runs_passed_total}"
                    ),
                    "# TYPE enterprise_ai_evaluation_runs_failed_total counter",
                    (
                        "enterprise_ai_evaluation_runs_failed_total "
                        f"{self.evaluation_runs_failed_total}"
                    ),
                    "# TYPE enterprise_ai_evaluation_weak_evidence_warning_total counter",
                    (
                        "enterprise_ai_evaluation_weak_evidence_warning_total "
                        f"{self.evaluation_weak_evidence_warning_total}"
                    ),
                    "# TYPE enterprise_ai_evaluation_no_evidence_warning_total counter",
                    (
                        "enterprise_ai_evaluation_no_evidence_warning_total "
                        f"{self.evaluation_no_evidence_warning_total}"
                    ),
                ]
            )
            return "\n".join(line for line in lines if line) + "\n"


metrics_registry = MetricsRegistry()
