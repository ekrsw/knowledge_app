# Logging Guidelines and Standards

## 📋 Overview

This document establishes comprehensive logging guidelines for the knowledge_app project to ensure consistent, secure, and operationally useful logging across all modules.

## 🎯 Logging Objectives

- **Consistency**: Uniform logging patterns and formats across all modules
- **Security**: No sensitive information exposure in logs
- **Operational**: Actionable logs for monitoring, debugging, and alerting
- **Performance**: Efficient logging with minimal performance impact
- **Correlation**: Proper request/operation tracing capabilities

## 📊 Current State Analysis

### Identified Issues
1. **Mixed Format Patterns**: Some logs use f-strings, others use structured logging with `extra` parameters
2. **Inconsistent Error Context**: Variable amounts of context in error messages
3. **Log Level Inconsistencies**: Similar operations using different log levels
4. **Security Gaps**: Some logs may expose sensitive information through stack traces

### Strengths
- Comprehensive coverage across CRUD operations
- Security-conscious user ID hashing
- Performance monitoring with query timing
- Environment-aware formatting (JSON for production)
- Request ID correlation system

## 🔧 Logging Standards

### 1. Log Level Guidelines

#### DEBUG (Development/Troubleshooting)
- **Usage**: Detailed operation flow, query starts, internal state
- **Examples**: "Getting user by username", "Query started: get_users_paginated"
- **When**: Development debugging, detailed troubleshooting
- **Format**: Always use structured logging with `extra` parameters

#### INFO (Normal Operations)
- **Usage**: Operation lifecycle, successful completions, performance metrics
- **Examples**: "User creation completed successfully", "Query performance: 150ms"
- **When**: Normal operation tracking, audit trails
- **Format**: Structured logging with operation context

#### WARNING (Attention Required)
- **Usage**: Performance degradation, recoverable errors, configuration issues
- **Examples**: "Slow query detected: 750ms", "High memory usage detected"
- **When**: Performance thresholds exceeded, potential issues
- **Format**: Structured logging with metrics and context

#### ERROR (Failures)
- **Usage**: Operation failures, validation errors, database constraints
- **Examples**: "User not found for update", "Duplicate username detected"
- **When**: Business logic failures, user input errors
- **Format**: Structured logging with error context (no sensitive data)

#### CRITICAL (System Failures)
- **Usage**: System-wide failures, configuration errors, resource exhaustion
- **Examples**: "Database connection pool exhausted", "Configuration validation failed"
- **When**: System-threatening conditions requiring immediate attention
- **Format**: Structured logging with system context and metrics

### 2. Message Format Standards

#### Structured Logging Format
**All log messages MUST use structured logging with `extra` parameters:**

```python
# ✅ CORRECT - Structured with extra parameters
self.logger.info(
    "User operation completed",
    extra={
        "operation": "create_user",
        "status": "success",
        "user_id_hash": self._hash_user_id(user.id),
        "execution_time_ms": 125
    }
)

# ❌ INCORRECT - Direct f-string without structure
self.logger.info(f"User {user.id} created successfully")
```

#### Error Message Format
**Error messages MUST include operation context without sensitive data:**

```python
# ✅ CORRECT - Context with security
self.logger.error(
    "Database constraint violation",
    extra={
        "operation": "create_user",
        "error_type": "unique_violation",
        "constraint": "username",
        "error_code": "23505"
    }
)

# ❌ INCORRECT - Sensitive data exposure
self.logger.error(f"Duplicate username: {username}")
```

### 3. Security Standards

#### Sensitive Data Protection
**NEVER log sensitive information:**
- Raw user IDs (use `_hash_user_id()`)
- Passwords (plain text or hashed)
- Email addresses in full
- Personal information (names, addresses)
- Internal system paths or configurations

#### Required Security Measures
```python
# ✅ Safe user identification
user_id_hash = self._hash_user_id(user.id)

# ✅ Safe operation logging
self.logger.info(
    "Password update completed",
    extra={
        "operation": "update_password",
        "user_id_hash": user_id_hash,
        "timestamp": datetime.utcnow().isoformat()
    }
)
```

### 4. Performance Monitoring

#### Query Performance Logging
**All database operations MUST include performance metrics:**

```python
# Required pattern for database operations
async with self._monitor_query_performance(
    "operation_name",
    operation="detailed_operation",
    **additional_context
):
    # Database operation here
    pass
```

#### Performance Thresholds
- **INFO**: Queries > 100ms
- **WARNING**: Queries > 500ms
- **ERROR**: Queries > 2000ms

### 5. Correlation Standards

#### Request ID Integration
**All logs MUST include correlation IDs:**

```python
# Automatic via _log_operation method
self._log_operation(
    "user_creation",
    "start",
    user_id=user.id,
    request_id=request_id  # From request context
)
```

#### Operation Tracking
**All operations MUST log start/success/error states:**

```python
# Start
self._log_operation("operation_name", "start", user_id=user_id)

# Success
self._log_operation("operation_name", "success", user_id=user_id)

# Error
self._log_operation("operation_name", "error", user_id=user_id, error_type="ValidationError")
```

## 🔄 Implementation Plan

### Phase 1: Standardization (Current)
1. **Document Current Issues**: Complete analysis of inconsistencies
2. **Create Guidelines**: Establish comprehensive standards
3. **Update Core Logging**: Improve `_log_operation` method

### Phase 2: Consistency Updates
1. **Standardize Error Logging**: Convert f-string errors to structured format
2. **Improve Debug Logging**: Add consistent context to all DEBUG messages
3. **Enhance Performance Logging**: Ensure all queries use monitoring context

### Phase 3: Operational Enhancements
1. **Add Monitoring Metrics**: Include operational metrics in logs
2. **Implement Alerting Tags**: Add tags for automated alerting
3. **Create Log Aggregation**: Prepare for centralized logging

## 📋 Specific Improvements Required

### 1. Convert F-String Errors to Structured Format

**Current Issues:**
```python
# ❌ These need to be converted
self.logger.error(f"Duplicate username detected during {operation}")
self.logger.error(f"Error getting users: {str(e)}")
self.logger.error(f"User not found for update")
```

**Target Format:**
```python
# ✅ Structured format
self.logger.error(
    "Duplicate username detected",
    extra={
        "operation": operation,
        "error_type": "duplicate_username",
        "constraint": "username"
    }
)
```

### 2. Standardize Debug Messages

**Current Issues:**
```python
# ❌ Inconsistent context
self.logger.debug("Getting user by username")
self.logger.debug(f"Found {len(users)} users")
```

**Target Format:**
```python
# ✅ Consistent structured format
self.logger.debug(
    "User lookup initiated",
    extra={
        "operation": "get_user_by_username",
        "lookup_type": "username"
    }
)
```

### 3. Enhance Performance Context

**Current Issues:**
```python
# ❌ Missing operation context
self.logger.info(f"Query performance: {query_name}", extra=log_data)
```

**Target Format:**
```python
# ✅ Complete performance context
self.logger.info(
    "Query performance monitored",
    extra={
        "query_name": query_name,
        "execution_time_ms": execution_time_ms,
        "operation": current_operation,
        "user_id_hash": user_id_hash,
        "performance_category": "normal"  # slow, normal, fast
    }
)
```

## 🧪 Testing Requirements

### Logging Tests
1. **Security Tests**: Verify no sensitive data in logs
2. **Format Tests**: Confirm structured logging compliance
3. **Performance Tests**: Validate performance monitoring accuracy
4. **Correlation Tests**: Ensure request ID propagation

### Test Coverage
- All logging methods must have corresponding tests
- Mock logging verification in all CRUD tests
- Security leak detection in log output
- Performance threshold validation

## 🔍 Monitoring and Alerting

### Log Aggregation Preparation
- All logs use JSON format in production
- Consistent field names for parsing
- Proper timestamp formatting
- Request correlation capabilities

### Alerting Triggers
- **ERROR** logs → Immediate notification
- **WARNING** logs → Batched alerts
- Performance threshold breaches → Capacity alerts
- Security events → Priority alerts

## 📊 Success Metrics

### Consistency Metrics
- 100% structured logging compliance
- 0% sensitive data exposure
- Consistent log levels across operations
- Complete operation lifecycle tracking

### Operational Metrics
- Query performance visibility
- Error rate monitoring
- Operation success/failure rates
- System health indicators

---

*This logging guidelines document ensures the knowledge_app maintains high-quality, secure, and operationally useful logging across all components. Regular updates will be made as the system evolves.*