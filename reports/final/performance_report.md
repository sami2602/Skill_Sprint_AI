# SkillSprint AI — Final System Performance & Benchmark Report

## Executive Summary
This report presents empirical performance measurements for **SkillSprint AI** across backend REST endpoints, database query speeds, deterministic Python validation benchmarks, and frontend production build metrics.

All measured metrics comply with and significantly outperform the target Non-Functional Requirements defined in **SkillSprint AI SRS Version 1.0**.

---

## 1. Non-Functional Performance Summary

| Metric / NFR Target | SRS Target Requirement | Actual Measured Result | Performance Evaluation |
| :--- | :--- | :--- | :--- |
| **AC-NFR-01: End-to-End Plan Generation Latency** | <= 30,000 ms (30.0s) | **177.74 ms** (0.178s) | **PASSED** (168x faster than requirement) |
| **AC-NFR-02: Database Query Response Latency** | <= 200.0 ms | **4.39 ms** | **PASSED** (45x faster than requirement) |
| **Python Ground-Truth Validation Latency** | <= 30,000 ms | **49.14 ms** average | **PASSED** (610x faster than requirement) |
| **Requirement Comparison Engine Speed** | <= 1,000 ms | **2.09 ms** | **PASSED** |
| **Auth Login Latency** | <= 1,000 ms | **90.35 ms** | **PASSED** |
| **System Analytics API Response** | <= 500 ms | **91.61 ms** | **PASSED** |
| **Audit Log Query Latency** | <= 200 ms | **10.41 ms** | **PASSED** |

---

## 2. Itemized Latency Benchmarks

### Database Query Micro-Benchmarks
*Measured via `scripts/benchmark_backend.py` over SQLite database with 154 active requirements and 22 policy documents:*

- **Role Matrix Retrieval (Count=10)**: `1.22 ms`
- **Policy Requirements Catalog Query (Count=154)**: `4.39 ms`
- **Document Catalog Query (Count=32)**: `2.75 ms`

### Independent Python Validation Engine Benchmarks
*Measured via `scripts/run_phase5_validation_benchmark.py` across all 10 standard job roles:*

| Job Role ID | Role Name | Validation Latency | Mandatory Coverage | Traceability Score | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `ROL-01` | Software Engineer | 43.49 ms | 100.0% | 100.0% | `VERIFIED` |
| `ROL-02` | Senior Software Engineer | 59.12 ms | 100.0% | 100.0% | `VERIFIED` |
| `ROL-03` | Customer Support Executive | 56.72 ms | 100.0% | 100.0% | `VERIFIED` |
| `ROL-04` | Customer Support Manager | 51.43 ms | 100.0% | 100.0% | `VERIFIED` |
| `ROL-05` | Financial Analyst | 42.14 ms | 100.0% | 100.0% | `VERIFIED` |
| `ROL-06` | HR Operations Specialist | 60.19 ms | 100.0% | 100.0% | `VERIFIED` |
| `ROL-07` | Information Security Officer | 50.50 ms | 100.0% | 100.0% | `VERIFIED` |
| `ROL-08` | Product Manager | 35.45 ms | 100.0% | 100.0% | `VERIFIED` |
| `ROL-09` | Sales Development Rep | 44.27 ms | 100.0% | 100.0% | `VERIFIED` |
| `ROL-10` | Compliance Auditor | 48.07 ms | 100.0% | 100.0% | `VERIFIED` |
- **Average Validation Latency Across All 10 Roles**: **49.14 ms**

---

## 3. Frontend Production Build Performance

*Measured via Vite / Rollup build pipeline (`cmd /c "cd frontend && npm run build"`):*

- **Build Time**: `12.13 seconds`
- **Modules Transformed**: `2,590 modules`
- **Output Bundle Sizes**:
  - `dist/index.html`: `1.13 kB` (gzip: 0.62 kB)
  - `dist/assets/index.css`: `32.30 kB` (gzip: 6.09 kB)
  - `dist/assets/index.js`: `818.23 kB` (gzip: 232.42 kB)
- **Unit Test Execution Speed**: `7 tests passed in 713 ms` (Vitest v3.2.7)

---

## 4. Bottleneck Analysis & Performance Conclusion
- **Memory Footprint**: SQLite database engine and FastAPI in-memory ORM caching maintain minimal memory footprint (< 120 MB RAM).
- **Concurrency**: Async FastAPI handlers using AnyIO handle concurrent endpoint calls without blocking event loops.
- **Conclusion**: The system exhibits exceptional performance with latency profiles orders of magnitude better than competition SLA targets.
