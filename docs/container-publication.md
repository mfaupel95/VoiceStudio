# Container publication: independent manual authorization

`docker.yml` accepts **only** `workflow_dispatch`. Its boolean `publish` defaults
to false. Every CUDA/ROCm/arm64 publishing job requires
`github.event_name == 'workflow_dispatch' && inputs.publish == true`.
`packages: write` exists only on these guarded jobs. Registry cache exports,
GHCR login, compatibility retagging and optional Docker Hub pushes are inside
the same boundary. Push/merge/tag/release events do not publish containers.

The Electron release workflow no longer dispatches the Docker workflow and no
longer needs `actions: write`. Its existing desktop packaging/publication rules
are unchanged. No other release automation was disabled.

An authorized human must separately select **Docker (GHCR)** in Actions, choose
a reviewed branch and explicitly enable `publish`. Leaving it false runs no
jobs and publishes neither images nor caches. No publish dispatch was authorized
or performed for this change. Never interpret merging this PR as publication approval.

Without backfill, manual publication produces only immutable source-SHA tags.
For existing version tags, the existing validated `backfill_release`, `release_ref`
and `promote_stable` inputs retain exact version/beta/stable promotion behavior.
Historical automatic main/release metadata rules remain inert: rolling `latest`,
`main`, `rocm` and `cuda-arm64` aliases no longer update automatically; neither
does the Docker Hub description. Registry coordinates remain upstream's explicit
coordinates and must be reviewed before any later publication; this change does
not grant access or redirect publishing into another namespace.

## Verification

Install PyYAML 6.0.3 in a test environment, then run:

```sh
python -B tests/test_container_publish_policy.py
```

The parser validates actual YAML events, input defaults, all publisher job
conditions/permissions, and absence of chained Docker dispatches or alternate
registry writers across workflows. The condition is exact-match allowlisted;
negative push/PR/release/workflow_run/workflow_call and false/missing dispatch
inputs plus positive explicit true are checked without dispatching publication.
The old workflows fail these regressions (three failures); changed workflows pass.

## Integration gate

Do not merge PR #1 before this safety change is integrated into its head (or the
fork default). Merging the old PR #1 alone still triggers its old Docker publisher.
Existing CLA and UI crawler failures remain real gates, not permission to bypass.
The CLA bot requests the account owner's personal agreement and reports an
unlinked `Hermes <hermes@local>` commit identity. An agent must not sign or rewrite
attribution to impersonate the owner. Obtain human resolution before integration.
