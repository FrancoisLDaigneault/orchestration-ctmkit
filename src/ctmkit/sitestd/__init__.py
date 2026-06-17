"""BNC site-standard compliance engine.

Implements the real ``BNC-STANDARD`` ruleset (naming, mandatory variables, host exclusions,
etc.) and the rule-less ``BNC-CTRLM-ADMIN`` standard used by the 0225 admin application. The
engine audits any Control-M JSON tree and reports findings with suggested fixes.
"""
