# [](https://github.com/ZeroSumQuant/luca-dev-assistant/compare/v0.5.2...v) (2025-05-19)


### Bug Fixes

* add package installation to CI and Docker test ([06b6401](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/06b64015cc77387fc627023c4c548721d28cc2dc))
* add PYTHONPATH to Docker test environment ([5191d6a](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/5191d6ac07ccf534917e1c4b20d96b11edec8155))
* add system dependencies for psutil compilation ([f901a72](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/f901a721800bfd505fd39e756118ea58fa80e444))
* apply targeted fix for AutoGen mocking interference in CI tests ([fd25a48](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/fd25a48405f662c4c54a714f1b11b5936f0d5972)), closes [#76](https://github.com/ZeroSumQuant/luca-dev-assistant/issues/76)
* de-duplicate skipif decorator in sandbox timeout test ([2596885](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/259688569402d76ce4693eea5473210c07b277b1))
* improve module installation and test configuration ([995703b](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/995703b019a3cf0f45b31b6671f2f982d0e3f88d))
* install package and dev requirements in CI ([0a4195e](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/0a4195e26ddca83698fbc1b34b47b255cbc92eb6))
* mark registry tests as real_exec and skip them in Docker ([4ccd130](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/4ccd1300365551573d7f62f8a9c57f5face53f77))
* properly isolate test steps to prevent env var bleed ([01dad8f](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/01dad8f9feb35ba4b3b3cdb78ced06ad97ae4902))
* remove pythonpath configuration causing site-packages isolation ([39e0337](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/39e0337794fa3da2e18053a2a6c6be3791e4cdc0))
* run registry tests first and set env var to "0" not empty ([0c5dc01](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/0c5dc014c847bc0db8d9863022bbef5c95edb674))
* **tests:** rename tests/luca_core to tests/luca_core_pkgtests to avoid import collision ([6af27e9](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/6af27e9f9661cf620ac701fb9e3f2b33a9e17ffd)), closes [#76](https://github.com/ZeroSumQuant/luca-dev-assistant/issues/76)
* update failing tests and fix mypy errors\n\n- Fix async execution in test_process_coroutine_execution\n- Fix module execution test to handle mocking properly\n- Fix registry parameter extraction test (expected default value)\n- Fix registry execute tests to use globals() for function lookup\n- Fix whitespace issue in test_main.py\n- Fix mypy type errors in test_base_store.py by adding TypeVar\n- Update method signatures to match base class properly ([3b4f37c](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/3b4f37c150e75ad078559051ac89e3cb4c0d3c8b))
* update tests to match actual ContextStore behavior ([2e0bf97](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/2e0bf97e42c8da4ecb369444dcba44c689b6749e))
* use separate pytest configs for better test isolation ([be38405](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/be38405a6ec3de3ec8926a47df1d6cc0eab7626c))
* use separate pytest runs for mocked vs real tests + fix mypy errors ([d8c82a1](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/d8c82a1c9528da6fed8020977ec709b4702f5d27))


### Features

* add 300-s timeout guard to SandboxRunner ([8b4a031](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/8b4a031f9a829895faeef9e08e8ef10b1fc24f39))
* add automation safeguards and improve test coverage to 95% ([e806696](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/e8066965d739591e3e7055dab181269fdb0a5bfc))
* add Makefile with capped test-docker target ([e9a54c8](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/e9a54c863112b44f85272d98635580683aa9654e))
* **core:** enhance LucaManager integration with improved error handling and debug support ([7801ab4](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/7801ab40c334bf2abca4a449e795437e6e5fd01e))
* **core:** integrate luca_core with main application ([1d6cd3b](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/1d6cd3b549823ef87a17cdfedcf3bce0e0199794))
* **core:** integrate luca_core with main application ([7a06dde](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/7a06dde35008ccd5dae4fadcf45f88763b4618ff))



# [](https://github.com/ZeroSumQuant/luca-dev-assistant/compare/v0.5.2...v) (2025-05-17)


### Bug Fixes

* add system dependencies for psutil compilation ([f901a72](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/f901a721800bfd505fd39e756118ea58fa80e444))
* de-duplicate skipif decorator in sandbox timeout test ([2596885](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/259688569402d76ce4693eea5473210c07b277b1))


### Features

* add 300-s timeout guard to SandboxRunner ([8b4a031](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/8b4a031f9a829895faeef9e08e8ef10b1fc24f39))
* add Makefile with capped test-docker target ([e9a54c8](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/e9a54c863112b44f85272d98635580683aa9654e))
* **core:** enhance LucaManager integration with improved error handling and debug support ([7801ab4](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/7801ab40c334bf2abca4a449e795437e6e5fd01e))
* **core:** integrate luca_core with main application ([1d6cd3b](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/1d6cd3b549823ef87a17cdfedcf3bce0e0199794))
* **core:** integrate luca_core with main application ([7a06dde](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/7a06dde35008ccd5dae4fadcf45f88763b4618ff))



# [](https://github.com/ZeroSumQuant/luca-dev-assistant/compare/v0.5.2...v) (2025-05-16)


### Features

* **core:** enhance LucaManager integration with improved error handling and debug support ([7801ab4](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/7801ab40c334bf2abca4a449e795437e6e5fd01e))
* **core:** integrate luca_core with main application ([1d6cd3b](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/1d6cd3b549823ef87a17cdfedcf3bce0e0199794))
* **core:** integrate luca_core with main application ([7a06dde](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/7a06dde35008ccd5dae4fadcf45f88763b4618ff))



# [](https://github.com/ZeroSumQuant/luca-dev-assistant/compare/v0.5.2...v) (2025-05-16)

### Features

* **core:** enhance LucaManager integration with improved error handling and debug support ([7801ab4](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/7801ab40c334bf2abca4a449e795437e6e5fd01e))
* **core:** integrate luca_core with main application ([1d6cd3b](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/1d6cd3b549823ef87a17cdfedcf3bce0e0199794))
* **core:** integrate luca_core with main application ([7a06dde](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/7a06dde35008ccd5dae4fadcf45f88763b4618ff))

# [](https://github.com/ZeroSumQuant/luca-dev-assistant/compare/v0.5.2...v) (2025-05-16)

### Features

* **core:** enhance LucaManager integration with improved error handling and debug support ([7801ab4](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/7801ab40c334bf2abca4a449e795437e6e5fd01e))
* **core:** integrate luca_core with main application ([1d6cd3b](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/1d6cd3b549823ef87a17cdfedcf3bce0e0199794))
* **core:** integrate luca_core with main application ([7a06dde](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/7a06dde35008ccd5dae4fadcf45f88763b4618ff))

# [](https://github.com/ZeroSumQuant/luca-dev-assistant/compare/v0.5.2...v) (2025-05-16)

### Features

* **core:** enhance LucaManager integration with improved error handling and debug support ([7801ab4](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/7801ab40c334bf2abca4a449e795437e6e5fd01e))
* **core:** integrate luca_core with main application ([1d6cd3b](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/1d6cd3b549823ef87a17cdfedcf3bce0e0199794))
* **core:** integrate luca_core with main application ([7a06dde](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/7a06dde35008ccd5dae4fadcf45f88763b4618ff))

# [](https://github.com/ZeroSumQuant/luca-dev-assistant/compare/v0.5.2...v) (2025-05-16)

### Features

* **core:** enhance LucaManager integration with improved error handling and debug support ([7801ab4](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/7801ab40c334bf2abca4a449e795437e6e5fd01e))
* **core:** integrate luca_core with main application ([1d6cd3b](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/1d6cd3b549823ef87a17cdfedcf3bce0e0199794))
* **core:** integrate luca_core with main application ([7a06dde](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/7a06dde35008ccd5dae4fadcf45f88763b4618ff))

# (2025-05-16)
EOF < /dev/null
### Bug Fixes

* **ci:** enhance changelog workflow to handle parallel updates ([#11](https://github.com/ZeroSumQuant/luca-dev-assistant/issues/11)) ([bf53706](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/bf537066a9e45a6978f01229a431749e915fa447))
* **ci:** enhance changelog workflow with progressive retry strategy ([#37](https://github.com/ZeroSumQuant/luca-dev-assistant/issues/37)) ([d176077](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/d17607778bda8656272161331cbe2e2b8e5b8775))

### Features

* **core:** enhance LucaManager integration with improved error handling and debug support ([7801ab4](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/7801ab40c334bf2abca4a449e795437e6e5fd01e))
* **core:** integrate luca_core with main application ([1d6cd3b](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/1d6cd3b549823ef87a17cdfedcf3bce0e0199794))
* **core:** integrate luca_core with main application ([7a06dde](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/7a06dde35008ccd5dae4fadcf45f88763b4618ff))
* **luca:** scaffold core (placeholder entry-point + smoke test) ([#3](https://github.com/ZeroSumQuant/luca-dev-assistant/issues/3)) ([cf49f45](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/cf49f45e3402f363e572595c3a550c9389003796))
* seed changelog test entry ([1766b66](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/1766b66685b463d158e248a74dd228f091a5c93d))

# (2025-05-12)

### Bug Fixes

* **ci:** enhance changelog workflow to handle parallel updates ([#11](https://github.com/ZeroSumQuant/luca-dev-assistant/issues/11)) ([bf53706](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/bf537066a9e45a6978f01229a431749e915fa447))
* **ci:** enhance changelog workflow with progressive retry strategy ([#37](https://github.com/ZeroSumQuant/luca-dev-assistant/issues/37)) ([d176077](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/d17607778bda8656272161331cbe2e2b8e5b8775))

### Features

* **luca:** scaffold core (placeholder entry-point + smoke test) ([#3](https://github.com/ZeroSumQuant/luca-dev-assistant/issues/3)) ([cf49f45](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/cf49f45e3402f363e572595c3a550c9389003796))
* seed changelog test entry ([1766b66](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/1766b66685b463d158e248a74dd228f091a5c93d))

# (2025-05-12)

### Bug Fixes

* **ci:** enhance changelog workflow to handle parallel updates ([#11](https://github.com/ZeroSumQuant/luca-dev-assistant/issues/11)) ([bf53706](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/bf537066a9e45a6978f01229a431749e915fa447))

### Features

* **luca:** scaffold core (placeholder entry-point + smoke test) ([#3](https://github.com/ZeroSumQuant/luca-dev-assistant/issues/3)) ([cf49f45](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/cf49f45e3402f363e572595c3a550c9389003796))
* seed changelog test entry ([1766b66](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/1766b66685b463d158e248a74dd228f091a5c93d))

# (2025-05-12)

### Bug Fixes

* **ci:** enhance changelog workflow to handle parallel updates ([#11](https://github.com/ZeroSumQuant/luca-dev-assistant/issues/11)) ([bf53706](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/bf537066a9e45a6978f01229a431749e915fa447))

### Features

* **luca:** scaffold core (placeholder entry-point + smoke test) ([#3](https://github.com/ZeroSumQuant/luca-dev-assistant/issues/3)) ([cf49f45](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/cf49f45e3402f363e572595c3a550c9389003796))
* seed changelog test entry ([1766b66](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/1766b66685b463d158e248a74dd228f091a5c93d))

# (2025-05-12)

### Bug Fixes

* **ci:** enhance changelog workflow to handle parallel updates ([#11](https://github.com/ZeroSumQuant/luca-dev-assistant/issues/11)) ([bf53706](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/bf537066a9e45a6978f01229a431749e915fa447))

### Features

* **luca:** scaffold core (placeholder entry-point + smoke test) ([#3](https://github.com/ZeroSumQuant/luca-dev-assistant/issues/3)) ([cf49f45](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/cf49f45e3402f363e572595c3a550c9389003796))
* seed changelog test entry ([1766b66](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/1766b66685b463d158e248a74dd228f091a5c93d))

# (2025-05-12)

### Bug Fixes

* **ci:** enhance changelog workflow to handle parallel updates ([#11](https://github.com/ZeroSumQuant/luca-dev-assistant/issues/11)) ([bf53706](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/bf537066a9e45a6978f01229a431749e915fa447))

### Features

* **luca:** scaffold core (placeholder entry-point + smoke test) ([#3](https://github.com/ZeroSumQuant/luca-dev-assistant/issues/3)) ([cf49f45](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/cf49f45e3402f363e572595c3a550c9389003796))
* seed changelog test entry ([1766b66](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/1766b66685b463d158e248a74dd228f091a5c93d))

# (2025-05-12)

### Bug Fixes

* **ci:** enhance changelog workflow to handle parallel updates ([#11](https://github.com/ZeroSumQuant/luca-dev-assistant/issues/11)) ([bf53706](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/bf537066a9e45a6978f01229a431749e915fa447))

### Features

* **luca:** scaffold core (placeholder entry-point + smoke test) ([#3](https://github.com/ZeroSumQuant/luca-dev-assistant/issues/3)) ([cf49f45](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/cf49f45e3402f363e572595c3a550c9389003796))
* seed changelog test entry ([1766b66](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/1766b66685b463d158e248a74dd228f091a5c93d))

# (2025-05-12)

### Bug Fixes

* **ci:** enhance changelog workflow to handle parallel updates ([#11](https://github.com/ZeroSumQuant/luca-dev-assistant/issues/11)) ([bf53706](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/bf537066a9e45a6978f01229a431749e915fa447))

### Features

* **luca:** scaffold core (placeholder entry-point + smoke test) ([#3](https://github.com/ZeroSumQuant/luca-dev-assistant/issues/3)) ([cf49f45](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/cf49f45e3402f363e572595c3a550c9389003796))
* seed changelog test entry ([1766b66](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/1766b66685b463d158e248a74dd228f091a5c93d))

# (2025-05-12)

### Bug Fixes

* **ci:** enhance changelog workflow to handle parallel updates ([#11](https://github.com/ZeroSumQuant/luca-dev-assistant/issues/11)) ([bf53706](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/bf537066a9e45a6978f01229a431749e915fa447))

### Features

* **luca:** scaffold core (placeholder entry-point + smoke test) ([#3](https://github.com/ZeroSumQuant/luca-dev-assistant/issues/3)) ([cf49f45](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/cf49f45e3402f363e572595c3a550c9389003796))
* seed changelog test entry ([1766b66](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/1766b66685b463d158e248a74dd228f091a5c93d))

# (2025-05-11)

### Bug Fixes

* **ci:** enhance changelog workflow to handle parallel updates ([#11](https://github.com/ZeroSumQuant/luca-dev-assistant/issues/11)) ([bf53706](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/bf537066a9e45a6978f01229a431749e915fa447))

### Features

* **luca:** scaffold core (placeholder entry-point + smoke test) ([#3](https://github.com/ZeroSumQuant/luca-dev-assistant/issues/3)) ([cf49f45](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/cf49f45e3402f363e572595c3a550c9389003796))
* seed changelog test entry ([1766b66](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/1766b66685b463d158e248a74dd228f091a5c93d))

# (2025-05-11)

### Bug Fixes

* **ci:** enhance changelog workflow to handle parallel updates ([#11](https://github.com/ZeroSumQuant/luca-dev-assistant/issues/11)) ([bf53706](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/bf537066a9e45a6978f01229a431749e915fa447))

### Features

* **luca:** scaffold core (placeholder entry-point + smoke test) ([#3](https://github.com/ZeroSumQuant/luca-dev-assistant/issues/3)) ([cf49f45](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/cf49f45e3402f363e572595c3a550c9389003796))
* seed changelog test entry ([1766b66](https://github.com/ZeroSumQuant/luca-dev-assistant/commit/1766b66685b463d158e248a74dd228f091a5c93d))

# (2025-05-11)

# (2025-05-09)

# (2025-05-06)

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
* Initial creation of changelog file in `docs/handoff/`.
