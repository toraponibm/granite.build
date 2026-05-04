# Environment variable constants used exclusively in test contexts.
# These env vars are generally passed to distributed components (i.e. steps, buildrunners, etc)
# that are then responsible for implementing/following their implications.
#
# Kept separate from constants.py to avoid mixing production and test config.

import os

_GBTEST_PREFIX = "GBTEST_"

# Controls whether HF push/pull/exists/delete calls are mocked. Set by tests that
# don't have real HuggingFace access. Propagated to remote jobs/pods via env var so
# they also mock HF calls. Read at call time (not import time) so tests can toggle it
# by setting/unsetting the env var without any patching.
ENV_VAR_GBTEST_MOCK_HF_CALLS = f"{_GBTEST_PREFIX}MOCK_HF_CALLS"


def is_hf_mocked() -> bool:
    """Return True if HF calls should be mocked (GBTEST_MOCK_HF_CALLS=true in env)."""
    return os.getenv(ENV_VAR_GBTEST_MOCK_HF_CALLS, "").lower() == "true"


def enable_hf_mocks() -> None:
    """Enable mocking of HF push/pull/exists/delete for this process and any remote jobs/pods.

    Sets GBTEST_MOCK_HF_CALLS in the environment. Since is_hf_mocked() reads the env
    var at call time, this takes effect immediately for all HfURI method calls without
    any patching. The env var is also forwarded to remote pods so they mock HF calls too.
    """
    os.environ[ENV_VAR_GBTEST_MOCK_HF_CALLS] = "true"


def disable_hf_mocks() -> None:
    """Disable HF mocking by removing GBTEST_MOCK_HF_CALLS from the environment."""
    os.environ.pop(ENV_VAR_GBTEST_MOCK_HF_CALLS, None)


# Causes the supporting environments that implement step-level retry to inject
# an initial failure event to trigger the step retry in the environment, if the step supports retries.
# Any environment that supports retries using Environment.with_retry_handler() will
# be subject to this injection via with_retry_handler().
ENV_VAR_GBTEST_SIMULATE_FAILURE_SCENARIO = f"{_GBTEST_PREFIX}SIMULATE_FAILURE_SCENARIO"


def is_failure_simulated() -> bool:
    """Return True if failure simulation is enabled (GBTEST_SIMULATE_FAILURE_SCENARIO=true in env)."""
    return os.getenv(ENV_VAR_GBTEST_SIMULATE_FAILURE_SCENARIO, "").lower() == "true"


def enable_failure_simulation() -> None:
    """Enable failure simulation for this process and any remote jobs/pods.

    Sets GBTEST_SIMULATE_FAILURE_SCENARIO in the environment. The env var is also
    forwarded to remote pods via get_exported_gbtest_env_vars().
    """
    os.environ[ENV_VAR_GBTEST_SIMULATE_FAILURE_SCENARIO] = "true"


def disable_failure_simulation() -> None:
    """Disable failure simulation by removing GBTEST_SIMULATE_FAILURE_SCENARIO from the environment."""
    os.environ.pop(ENV_VAR_GBTEST_SIMULATE_FAILURE_SCENARIO, None)


# The set of all GBTEST_ env var names defined in this module.
_GBTEST_EXPORTED_ENV_VARS = {
    ENV_VAR_GBTEST_MOCK_HF_CALLS,
    ENV_VAR_GBTEST_SIMULATE_FAILURE_SCENARIO,
}


def get_exported_gbtest_env_vars() -> dict[str, str]:
    """Return the GBTEST_ environment variables defined in this module that are currently set.

    Only returns vars explicitly declared here (not arbitrary GBTEST_* vars from the
    environment), so callers never accidentally forward test secrets or API keys.

    Returns:
        dict[str, str]: mapping of env var name → value for each known GBTEST_
        variable that is currently set in the environment.
    """
    return {k: v for k, v in os.environ.items() if k in _GBTEST_EXPORTED_ENV_VARS}
