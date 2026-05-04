from tenacity import retry, stop_after_attempt, wait_exponential
import structlog

logger = structlog.get_logger(__name__)

def resilience_retry(attempts=3, min_wait=1, max_wait=10):
    return retry(
        stop=stop_after_attempt(attempts),
        wait=wait_exponential(multiplier=min_wait, max=max_wait),
        before_sleep=lambda retry_state: logger.warning(
            "Retrying operation",
            attempt=retry_state.attempt_number,
            next_wait=retry_state.next_action.sleep
        )
    )
