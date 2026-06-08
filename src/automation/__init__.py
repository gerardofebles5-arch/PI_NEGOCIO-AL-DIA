"""
Módulo de Automatización
Integra sistema de alertas inteligentes con arquitectura Google-native
"""

from .alert_system import (
    AlertType,
    AlertPriority,
    AlertChannel,
    Alert,
    AlertSystem,
    alert_system
)

from .email_watcher import (
    EmailProvider,
    EmailFilter,
    EmailMessage,
    EmailAttachment,
    EmailWatcher,
    email_watcher
)

from .file_watcher import (
    FileEventType,
    FileFilter,
    FileEvent,
    WatchDirectory,
    FileWatcher as FileWatcherClass,
    file_watcher
)

__all__ = [
    'AlertType',
    'AlertPriority',
    'AlertChannel',
    'Alert',
    'AlertSystem',
    'alert_system',
    'EmailProvider',
    'EmailFilter',
    'EmailMessage',
    'EmailAttachment',
    'EmailWatcher',
    'email_watcher',
    'FileEventType',
    'FileFilter',
    'FileEvent',
    'WatchDirectory',
    'FileWatcherClass',
    'file_watcher'
]
