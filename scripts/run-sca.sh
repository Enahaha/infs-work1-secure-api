#!/usr/bin/env bash
set -euo pipefail

# Keep credentials out of Maven command-line arguments and build logs.
if [[ -n "${NVD_API_KEY:-}" ]]; then
  echo "SCA: using the optional NVD API key from the environment."
  exec mvn -B -ntp -Psca,nvd-key dependency-check:check
else
  echo "SCA: no API key configured; downloading NVD data anonymously (may be slower)."
  # An explicitly empty environment variable must not become an invalid API key.
  unset NVD_API_KEY
  exec mvn -B -ntp -Psca dependency-check:check
fi
