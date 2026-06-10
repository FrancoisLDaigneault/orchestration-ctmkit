"""Event-driven workflows: Kafka / Amazon SQS event sources that trigger Control-M.

Models the Control-M Event Handler queue-configuration entries — a listener consumes from a
broker queue/topic and fires a Control-M action (``setevent`` / ``runorder`` / ``ondemand``).
Only Kafka and SQS are supported here.
"""
