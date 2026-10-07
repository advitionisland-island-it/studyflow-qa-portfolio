# Evidence

Generated test reports and screenshots should be attached to CI artifacts rather than committed when they are large or ephemeral.

The reproducible evidence in this repository is:
- source code
- acceptance criteria
- test cases
- automated tests
- defect report
- regression report
- CI workflow

## Provenance

`LOCAL_VERIFICATION.json` was supplied in the ZIP. It describes a reconstructed build and records an earlier 14-test run; it is not evidence of this checkout or a current GitHub Actions run.

Fresh publication checks are recorded separately in `PUBLICATION_VERIFICATION.json`. Remote CI results must be checked against the run commit SHA; a local pass does not imply remote GREEN.
