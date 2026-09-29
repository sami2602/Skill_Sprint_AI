# SkillSprint AI — Authentication & RBAC Specification

## Overview
SkillSprint AI implements role-based access control (RBAC) backed by PBKDF2-HMAC-SHA256 password hashing and HMAC-SHA256 signed JSON Web Tokens (JWT).

---

## Password Security
- **Algorithm**: PBKDF2-HMAC-SHA256
- **Salt**: 16-byte cryptographically secure random salt (`secrets.token_bytes(16)`)
- **Iterations**: 100,000 iterations (NIST standard)
- **Format**: `$pbkdf2-sha256$100000$<salt_hex>$<hash_hex>`

---

## Role-Based Access Control Matrix

| Permission Key | Admin | Reviewer | Training Manager | Manager | Employee |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `read_all` | Yes | Yes | Yes | Dept | Own |
| `write_all` | Yes | No | No | No | No |
| `upload_document` | Yes | Yes | No | No | No |
| `manage_roles` | Yes | No | No | No | No |
| `approve_override` | Yes | Yes | No | No | No |
| `review_queue_action`| Yes | Yes | No | No | No |
| `selective_regenerate`| Yes | Yes | No | No | No |
| `generate_plan` | Yes | Yes | Yes | No | No |
| `view_audit` | Yes | Yes | Yes | No | No |
| `view_employee_dashboard` | Yes | Yes | Yes | Yes | No |
| `view_own_dashboard` | Yes | Yes | Yes | Yes | Yes |
