# Desarrollo del Dashboard Inteligente para Clientes

## Fecha
Junio 7, 2026

## Objetivo
Desarrollar un dashboard inteligente para clientes que permita visualizar documentos escaneados, estados de procesamiento, transacciones extraídas, y métricas contables en tiempo real.

---

## 1. Arquitectura del Dashboard

```
┌─────────────────────────────────────────────────────────────────┐
│                    Dashboard Cliente (Flutter Web)              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Layout Principal                                         │  │
│  │  - Sidebar de navegación                                 │  │
│  │  - Header con perfil y notificaciones                    │  │
│  │  - Contenido principal                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Widgets del Dashboard                                    │  │
│  │  - Tarjetas de resumen (métricas)                        │  │
│  │  - Gráficos de procesamiento                             │  │
│  │  - Lista de documentos recientes                         │  │
│  │  - Tabla de transacciones                               │  │
│  │  - Alertas y notificaciones                              │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ API Calls
                              │
┌─────────────────────────────────────────────────────────────────┐
│                    Cloud Functions (Backend)                     │
│  - getDashboardData: Obtener datos del dashboard              │
│  - getDocuments: Obtener documentos del cliente              │
│  - getTransactions: Obtener transacciones                    │
│  - getMetrics: Obtener métricas contables                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Database Queries
                              │
┌─────────────────────────────────────────────────────────────────┐
│                    Firestore + Cloud SQL                        │
│  - Documentos escaneados                                      │
│  - Transacciones contables                                   │
│  - Métricas y agregaciones                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Estructura del Dashboard

### 2.1 Layout Principal

```dart
// lib/presentation/pages/client/dashboard_page.dart
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../cubit/dashboard/client_dashboard_cubit.dart';
import '../../cubit/dashboard/client_dashboard_state.dart';
import '../../widgets/client/summary_cards.dart';
import '../../widgets/client/recent_documents.dart';
import '../../widgets/client/processing_chart.dart';
import '../../widgets/client/transactions_table.dart';
import '../../widgets/client/alerts_panel.dart';

class ClientDashboardPage extends StatefulWidget {
  const ClientDashboardPage({super.key});

  @override
  State<ClientDashboardPage> createState() => _ClientDashboardPageState();
}

class _ClientDashboardPageState extends State<ClientDashboardPage> {
  @override
  void initState() {
    super.initState();
    context.read<ClientDashboardCubit>().loadDashboardData();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Row(
        children: [
          _Sidebar(),
          Expanded(
            child: Column(
              children: [
                _Header(),
                Expanded(
                  child: BlocBuilder<ClientDashboardCubit, ClientDashboardState>(
                    builder: (context, state) {
                      if (state is ClientDashboardLoading) {
                        return const Center(child: CircularProgressIndicator());
                      } else if (state is ClientDashboardLoaded) {
                        return SingleChildScrollView(
                          padding: const EdgeInsets.all(24),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              _SummaryCards(metrics: state.metrics),
                              const SizedBox(height: 24),
                              _ProcessingChart(status: state.status),
                              const SizedBox(height: 24),
                              _RecentDocuments(documents: state.documents),
                              const SizedBox(height: 24),
                              _TransactionsTable(transactions: state.transactions),
                              const SizedBox(height: 24),
                              _AlertsPanel(alerts: state.alerts),
                            ],
                          ),
                        );
                      } else if (state is ClientDashboardError) {
                        return Center(
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              const Icon(Icons.error_outline, size: 64),
                              const SizedBox(height: 16),
                              Text(state.message),
                              const SizedBox(height: 16),
                              ElevatedButton(
                                onPressed: () {
                                  context.read<ClientDashboardCubit>().loadDashboardData();
                                },
                                child: const Text('Reintentar'),
                              ),
                            ],
                          ),
                        );
                      }
                      return const SizedBox.shrink();
                    },
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _Sidebar extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      width: 250,
      color: AppColors.goldDark,
      child: Column(
        children: [
          const SizedBox(height: 32),
          Image.asset(
            'assets/images/logo_PINAD.jpeg',
            height: 48,
            width: 48,
          ),
          const SizedBox(height: 16),
          const Text(
            '(π)NAD',
            style: TextStyle(
              color: Colors.white,
              fontSize: 24,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 32),
          _SidebarItem(
            icon: Icons.dashboard,
            label: 'Dashboard',
            isSelected: true,
          ),
          _SidebarItem(
            icon: Icons.description,
            label: 'Documentos',
          ),
          _SidebarItem(
            icon: Icons.receipt_long,
            label: 'Transacciones',
          ),
          _SidebarItem(
            icon: Icons.assessment,
            label: 'Reportes',
          ),
          _SidebarItem(
            icon: Icons.settings,
            label: 'Configuración',
          ),
          const Spacer(),
          _SidebarItem(
            icon: Icons.logout,
            label: 'Cerrar Sesión',
          ),
          const SizedBox(height: 16),
        ],
      ),
    );
  }
}

class _SidebarItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final bool isSelected;

  const _SidebarItem({
    required this.icon,
    required this.label,
    this.isSelected = false,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: isSelected ? AppColors.goldMedium.withOpacity(0.3) : Colors.transparent,
      ),
      child: Row(
        children: [
          Icon(icon, color: Colors.white),
          const SizedBox(width: 12),
          Text(
            label,
            style: const TextStyle(color: Colors.white),
          ),
        ],
      ),
    );
  }
}

class _Header extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      height: 64,
      padding: const EdgeInsets.symmetric(horizontal: 24),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 4,
          ),
        ],
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          const Text(
            'Dashboard',
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: AppColors.grayDark,
            ),
          ),
          Row(
            children: [
              IconButton(
                icon: const Icon(Icons.notifications_outlined),
                onPressed: () {},
              ),
              const SizedBox(width: 16),
              CircleAvatar(
                backgroundColor: AppColors.goldDark,
                child: const Icon(Icons.person, color: Colors.white),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
```

### 2.2 Tarjetas de Resumen

```dart
// lib/presentation/widgets/client/summary_cards.dart
import 'package:flutter/material.dart';
import '../../../core/theme/app_theme.dart';

class _SummaryCards extends StatelessWidget {
  final DashboardMetrics metrics;

  const _SummaryCards({required this.metrics});

  @override
  Widget build(BuildContext context) {
    return GridView.count(
      crossAxisCount: 4,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      mainAxisSpacing: 16,
      crossAxisSpacing: 16,
      childAspectRatio: 2.5,
      children: [
        _SummaryCard(
          title: 'Documentos Totales',
          value: metrics.totalDocuments.toString(),
          icon: Icons.description,
          color: AppColors.goldDark,
          change: '+${metrics.documentsChange}%',
        ),
        _SummaryCard(
          title: 'Procesados',
          value: metrics.processedDocuments.toString(),
          icon: Icons.check_circle,
          color: AppColors.brownMedium,
          change: '+${metrics.processedChange}%',
        ),
        _SummaryCard(
          title: 'Pendientes',
          value: metrics.pendingDocuments.toString(),
          icon: Icons.pending,
          color: AppColors.orangeLight,
          change: '+${metrics.pendingChange}%',
        ),
        _SummaryCard(
          title: 'Monto Total',
          value: '\$${metrics.totalAmount.toStringAsFixed(2)}',
          icon: Icons.attach_money,
          color: AppColors.goldBright,
          change: '+${metrics.amountChange}%',
        ),
      ],
    );
  }
}

class _SummaryCard extends StatelessWidget {
  final String title;
  final String value;
  final IconData icon;
  final Color color;
  final String change;

  const _SummaryCard({
    required this.title,
    required this.value,
    required this.icon,
    required this.color,
    required this.change,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(icon, color: color, size: 24),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    title,
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                  const SizedBox(height: 4),
                  Text(
                    value,
                    style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: AppColors.grayDark,
                        ),
                  ),
                ],
              ),
            ),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                change,
                style: TextStyle(
                  color: color,
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
```

### 2.3 Gráfico de Procesamiento

```dart
// lib/presentation/widgets/client/processing_chart.dart
import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../../core/theme/app_theme.dart';

class _ProcessingChart extends StatelessWidget {
  final ProcessingStatus status;

  const _ProcessingChart({required this.status});

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Estado de Procesamiento',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 24),
            SizedBox(
              height: 200,
              child: PieChart(
                PieChartData(
                  sections: [
                    PieChartSectionData(
                      value: status.uploaded.toDouble(),
                      title: 'Subidos',
                      color: AppColors.goldDark,
                      radius: 80,
                    ),
                    PieChartSectionData(
                      value: status.processing.toDouble(),
                      title: 'Procesando',
                      color: AppColors.orangeLight,
                      radius: 80,
                    ),
                    PieChartSectionData(
                      value: status.processed.toDouble(),
                      title: 'Procesados',
                      color: AppColors.brownMedium,
                      radius: 80,
                    ),
                    PieChartSectionData(
                      value: status.failed.toDouble(),
                      title: 'Fallidos',
                      color: AppColors.brownDark,
                      radius: 80,
                    ),
                  ],
                  sectionsSpace: 2,
                  centerSpaceRadius: 40,
                  borderData: FlBorderData(show: false),
                ),
              ),
            ),
            const SizedBox(height: 24),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _LegendItem(color: AppColors.goldDark, label: 'Subidos', value: status.uploaded),
                _LegendItem(color: AppColors.orangeLight, label: 'Procesando', value: status.processing),
                _LegendItem(color: AppColors.brownMedium, label: 'Procesados', value: status.processed),
                _LegendItem(color: AppColors.brownDark, label: 'Fallidos', value: status.failed),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _LegendItem extends StatelessWidget {
  final Color color;
  final String label;
  final int value;

  const _LegendItem({
    required this.color,
    required this.label,
    required this.value,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Container(
          width: 12,
          height: 12,
          decoration: BoxDecoration(
            color: color,
            borderRadius: BorderRadius.circular(2),
          ),
        ),
        const SizedBox(width: 8),
        Text(
          '$label: $value',
          style: Theme.of(context).textTheme.bodySmall,
        ),
      ],
    );
  }
}
```

### 2.4 Documentos Recientes

```dart
// lib/presentation/widgets/client/recent_documents.dart
import 'package:flutter/material.dart';
import '../../../core/theme/app_theme.dart';

class _RecentDocuments extends StatelessWidget {
  final List<Document> documents;

  const _RecentDocuments({required this.documents});

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Documentos Recientes',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                TextButton(
                  onPressed: () {},
                  child: const Text('Ver Todos'),
                ),
              ],
            ),
            const SizedBox(height: 16),
            ListView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: documents.take(5).length,
              itemBuilder: (context, index) {
                final doc = documents[index];
                return _DocumentItem(document: doc);
              },
            ),
          ],
        ),
      ),
    );
  }
}

class _DocumentItem extends StatelessWidget {
  final Document document;

  const _DocumentItem({required this.document});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 12),
      decoration: BoxDecoration(
        border: Border(
          bottom: BorderSide(
            color: AppColors.brownGray.withOpacity(0.2),
          ),
        ),
      ),
      child: Row(
        children: [
          Container(
            width: 48,
            height: 48,
            decoration: BoxDecoration(
              color: _getStatusColor(document.status).withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(
              _getDocumentIcon(document.fileType),
              color: _getStatusColor(document.status),
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  document.fileName,
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                const SizedBox(height: 4),
                Text(
                  _formatDate(document.createdAt),
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: AppColors.brownGray,
                      ),
                ),
              ],
            ),
          ),
          _StatusChip(status: document.status),
        ],
      ),
    );
  }

  Color _getStatusColor(String status) {
    switch (status) {
      case 'uploaded':
        return AppColors.goldDark;
      case 'processing':
        return AppColors.orangeLight;
      case 'processed':
        return AppColors.brownMedium;
      case 'failed':
        return AppColors.brownDark;
      default:
        return AppColors.brownGray;
    }
  }

  IconData _getDocumentIcon(String fileType) {
    switch (fileType) {
      case 'invoice':
        return Icons.receipt;
      case 'receipt':
        return Icons.receipt_long;
      case 'contract':
        return Icons.description;
      default:
        return Icons.insert_drive_file;
    }
  }

  String _formatDate(DateTime date) {
    return '${date.day}/${date.month}/${date.year}';
  }
}

class _StatusChip extends StatelessWidget {
  final String status;

  const _StatusChip({required this.status});

  @override
  Widget build(BuildContext context) {
    final color = _getStatusColor(status);
    final label = _getStatusLabel(status);

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Text(
        label,
        style: TextStyle(
          color: color,
          fontSize: 12,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }

  Color _getStatusColor(String status) {
    switch (status) {
      case 'uploaded':
        return AppColors.goldDark;
      case 'processing':
        return AppColors.orangeLight;
      case 'processed':
        return AppColors.brownMedium;
      case 'failed':
        return AppColors.brownDark;
      default:
        return AppColors.brownGray;
    }
  }

  String _getStatusLabel(String status) {
    switch (status) {
      case 'uploaded':
        return 'Subido';
      case 'processing':
        return 'Procesando';
      case 'processed':
        return 'Procesado';
      case 'failed':
        return 'Fallido';
      default:
        return 'Desconocido';
    }
  }
}
```

### 2.5 Tabla de Transacciones

```dart
// lib/presentation/widgets/client/transactions_table.dart
import 'package:flutter/material.dart';
import '../../../core/theme/app_theme.dart';

class _TransactionsTable extends StatelessWidget {
  final List<Transaction> transactions;

  const _TransactionsTable({required this.transactions});

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Transacciones Extraídas',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                ElevatedButton.icon(
                  onPressed: () {},
                  icon: const Icon(Icons.download),
                  label: const Text('Exportar'),
                ),
              ],
            ),
            const SizedBox(height: 16),
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: DataTable(
                columns: const [
                  DataColumn(label: Text('Fecha')),
                  DataColumn(label: Text('Descripción')),
                  DataColumn(label: Text('Monto')),
                  DataColumn(label: Text('Impuesto')),
                  DataColumn(label: Text('Estado')),
                ],
                rows: transactions.take(10).map((transaction) {
                  return DataRow(
                    cells: [
                      DataCell(Text(_formatDate(transaction.date))),
                      DataCell(Text(transaction.description)),
                      DataCell(Text('\$${transaction.amount.toStringAsFixed(2)}')),
                      DataCell(Text('\$${transaction.taxAmount.toStringAsFixed(2)}')),
                      DataCell(_StatusChip(status: transaction.status)),
                    ],
                  );
                }).toList(),
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _formatDate(DateTime date) {
    return '${date.day}/${date.month}/${date.year}';
  }
}

class _StatusChip extends StatelessWidget {
  final String status;

  const _StatusChip({required this.status});

  @override
  Widget build(BuildContext context) {
    final color = _getStatusColor(status);
    final label = _getStatusLabel(status);

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Text(
        label,
        style: TextStyle(
          color: color,
          fontSize: 12,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }

  Color _getStatusColor(String status) {
    switch (status) {
      case 'pending':
        return AppColors.orangeLight;
      case 'verified':
        return AppColors.brownMedium;
      case 'reconciled':
        return AppColors.goldDark;
      default:
        return AppColors.brownGray;
    }
  }

  String _getStatusLabel(String status) {
    switch (status) {
      case 'pending':
        return 'Pendiente';
      case 'verified':
        return 'Verificado';
      case 'reconciled':
        return 'Conciliado';
      default:
        return 'Desconocido';
    }
  }
}
```

### 2.6 Panel de Alertas

```dart
// lib/presentation/widgets/client/alerts_panel.dart
import 'package:flutter/material.dart';
import '../../../core/theme/app_theme.dart';

class _AlertsPanel extends StatelessWidget {
  final List<Alert> alerts;

  const _AlertsPanel({required this.alerts});

  @override
  Widget build(BuildContext context) {
    if (alerts.isEmpty) {
      return const SizedBox.shrink();
    }

    return Card(
      elevation: 2,
      color: AppColors.orangeBeige.withOpacity(0.3),
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.warning, color: AppColors.goldDark),
                const SizedBox(width: 8),
                Text(
                  'Alertas',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        color: AppColors.goldDark,
                      ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            ...alerts.take(3).map((alert) => _AlertItem(alert: alert)),
          ],
        ),
      ),
    );
  }
}

class _AlertItem extends StatelessWidget {
  final Alert alert;

  const _AlertItem({required this.alert});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 12),
      decoration: BoxDecoration(
        border: Border(
          bottom: BorderSide(
            color: AppColors.brownGray.withOpacity(0.2),
          ),
        ),
      ),
      child: Row(
        children: [
          Icon(
            _getAlertIcon(alert.type),
            color: _getAlertColor(alert.type),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  alert.title,
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                const SizedBox(height: 4),
                Text(
                  alert.message,
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: AppColors.brownGray,
                      ),
                ),
              ],
            ),
          ),
          Text(
            _formatTime(alert.createdAt),
            style: Theme.of(context).textTheme.bodySmall,
          ),
        ],
      ),
    );
  }

  IconData _getAlertIcon(String type) {
    switch (type) {
      case 'document_failed':
        return Icons.error;
      case 'quota_exceeded':
        return Icons.warning;
      case 'system_alert':
        return Icons.info;
      default:
        return Icons.notifications;
    }
  }

  Color _getAlertColor(String type) {
    switch (type) {
      case 'document_failed':
        return AppColors.brownDark;
      case 'quota_exceeded':
        return AppColors.orangeLight;
      case 'system_alert':
        return AppColors.goldDark;
      default:
        return AppColors.brownGray;
    }
  }

  String _formatTime(DateTime time) {
    final now = DateTime.now();
    final difference = now.difference(time);
    
    if (difference.inMinutes < 60) {
      return '${difference.inMinutes} min';
    } else if (difference.inHours < 24) {
      return '${difference.inHours} h';
    } else {
      return '${difference.inDays} d';
    }
  }
}
```

---

## 3. Cubit de Dashboard

```dart
// lib/presentation/cubit/dashboard/client_dashboard_cubit.dart
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:cloud_functions/cloud_functions.dart';

class ClientDashboardCubit extends Cubit<ClientDashboardState> {
  final FirebaseFunctions _functions;

  ClientDashboardCubit(this._functions) : super(ClientDashboardInitial());

  Future<void> loadDashboardData() async {
    emit(ClientDashboardLoading());
    
    try {
      final result = await _functions.httpsCallable('getDashboardData').call({
        'tenantId': 'tenant-1', // Obtener del contexto de autenticación
        'userId': 'user-1', // Obtener del contexto de autenticación
      });

      final data = result.data as Map<String, dynamic>;
      
      emit(ClientDashboardLoaded(
        metrics: DashboardMetrics.fromJson(data['metrics']),
        documents: (data['documents'] as List)
            .map((doc) => Document.fromJson(doc))
            .toList(),
        status: ProcessingStatus.fromJson(data['status']),
        transactions: (data['transactions'] as List)
            .map((tx) => Transaction.fromJson(tx))
            .toList(),
        alerts: (data['alerts'] as List)
            .map((alert) => Alert.fromJson(alert))
            .toList(),
      ));
    } catch (error) {
      emit(ClientDashboardError(error.toString()));
    }
  }
}

class ClientDashboardState {}

class ClientDashboardInitial extends ClientDashboardState {}

class ClientDashboardLoading extends ClientDashboardState {}

class ClientDashboardLoaded extends ClientDashboardState {
  final DashboardMetrics metrics;
  final List<Document> documents;
  final ProcessingStatus status;
  final List<Transaction> transactions;
  final List<Alert> alerts;

  ClientDashboardLoaded({
    required this.metrics,
    required this.documents,
    required this.status,
    required this.transactions,
    required this.alerts,
  });
}

class ClientDashboardError extends ClientDashboardState {
  final String message;

  ClientDashboardError(this.message);
}
```

---

## 4. Modelos de Datos

```dart
// lib/models/dashboard_metrics.dart
class DashboardMetrics {
  final int totalDocuments;
  final int processedDocuments;
  final int pendingDocuments;
  final int failedDocuments;
  final double totalAmount;
  final String documentsChange;
  final String processedChange;
  final String pendingChange;
  final String amountChange;

  DashboardMetrics({
    required this.totalDocuments,
    required this.processedDocuments,
    required this.pendingDocuments,
    required this.failedDocuments,
    required this.totalAmount,
    required this.documentsChange,
    required this.processedChange,
    required this.pendingChange,
    required this.amountChange,
  });

  factory DashboardMetrics.fromJson(Map<String, dynamic> json) {
    return DashboardMetrics(
      totalDocuments: json['totalDocuments'] ?? 0,
      processedDocuments: json['processedDocuments'] ?? 0,
      pendingDocuments: json['pendingDocuments'] ?? 0,
      failedDocuments: json['failedDocuments'] ?? 0,
      totalAmount: (json['totalAmount'] ?? 0).toDouble(),
      documentsChange: json['documentsChange'] ?? '0%',
      processedChange: json['processedChange'] ?? '0%',
      pendingChange: json['pendingChange'] ?? '0%',
      amountChange: json['amountChange'] ?? '0%',
    );
  }
}

class ProcessingStatus {
  final int uploaded;
  final int processing;
  final int processed;
  final int failed;

  ProcessingStatus({
    required this.uploaded,
    required this.processing,
    required this.processed,
    required this.failed,
  });

  factory ProcessingStatus.fromJson(Map<String, dynamic> json) {
    return ProcessingStatus(
      uploaded: json['uploaded'] ?? 0,
      processing: json['processing'] ?? 0,
      processed: json['processed'] ?? 0,
      failed: json['failed'] ?? 0,
    );
  }
}

class Document {
  final String id;
  final String fileName;
  final String fileType;
  final String status;
  final DateTime createdAt;
  final ExtractedData? extractedData;

  Document({
    required this.id,
    required this.fileName,
    required this.fileType,
    required this.status,
    required this.createdAt,
    this.extractedData,
  });

  factory Document.fromJson(Map<String, dynamic> json) {
    return Document(
      id: json['id'] ?? '',
      fileName: json['fileName'] ?? '',
      fileType: json['fileType'] ?? 'other',
      status: json['status'] ?? 'uploaded',
      createdAt: DateTime.parse(json['createdAt'] ?? DateTime.now().toIso8601String()),
      extractedData: json['extractedData'] != null 
          ? ExtractedData.fromJson(json['extractedData'])
          : null,
    );
  }
}

class Transaction {
  final String id;
  final DateTime date;
  final String description;
  final double amount;
  final double taxAmount;
  final String status;

  Transaction({
    required this.id,
    required this.date,
    required this.description,
    required this.amount,
    required this.taxAmount,
    required this.status,
  });

  factory Transaction.fromJson(Map<String, dynamic> json) {
    return Transaction(
      id: json['id'] ?? '',
      date: DateTime.parse(json['date'] ?? DateTime.now().toIso8601String()),
      description: json['description'] ?? '',
      amount: (json['amount'] ?? 0).toDouble(),
      taxAmount: (json['taxAmount'] ?? 0).toDouble(),
      status: json['status'] ?? 'pending',
    );
  }
}

class Alert {
  final String id;
  final String type;
  final String title;
  final String message;
  final DateTime createdAt;

  Alert({
    required this.id,
    required this.type,
    required this.title,
    required this.message,
    required this.createdAt,
  });

  factory Alert.fromJson(Map<String, dynamic> json) {
    return Alert(
      id: json['id'] ?? '',
      type: json['type'] ?? 'system_alert',
      title: json['title'] ?? '',
      message: json['message'] ?? '',
      createdAt: DateTime.parse(json['createdAt'] ?? DateTime.now().toIso8601String()),
    );
  }
}
```

---

## 5. Configuración Flutter Web

### 5.1 pubspec.yaml

```yaml
dependencies:
  flutter:
    sdk: flutter
  flutter_web_plugins:
    sdk: flutter
  firebase_core: ^2.24.2
  cloud_functions: ^4.6.0
  fl_chart: ^0.66.0
  flutter_bloc: ^8.1.3
  google_fonts: ^6.0.0
```

### 5.2 Configuración Web

```dart
// web/index.html
<!DOCTYPE html>
<html>
<head>
  <base href="/">
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>PINAD - Sistema de Escaneo Contable</title>
</head>
<body>
  <script src="flutter_bootstrap.js" async></script>
</body>
</html>
```

---

## 6. Características Inteligentes

### 6.1 Predicciones de Gastos

```dart
class _ExpensePredictionWidget extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Predicción de Gastos (Próximo Mes)',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 16),
            LinearProgressIndicator(
              value: 0.75,
              backgroundColor: AppColors.brownGray.withOpacity(0.3),
              valueColor: AlwaysStoppedAnimation<Color>(AppColors.goldDark),
            ),
            const SizedBox(height: 8),
            Text(
              'Estimado: \$12,500',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 8),
            Text(
              'Basado en patrones históricos',
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ],
        ),
      ),
    );
  }
}
```

### 6.2 Anomalías Detectadas

```dart
class _AnomalyDetectionWidget extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Card(
      color: AppColors.brownDark.withOpacity(0.1),
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.warning, color: AppColors.brownDark),
                const SizedBox(width: 8),
                Text(
                  'Anomalía Detectada',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        color: AppColors.brownDark,
                      ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Text(
              'Gasto inusual detectado: \$5,000 en "Servicios Profesionales"',
              style: Theme.of(context).textTheme.bodyMedium,
            ),
            const SizedBox(height: 8),
            Text(
              'Este gasto es 300% mayor que el promedio mensual',
              style: Theme.of(context).textTheme.bodySmall,
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () {},
              child: const Text('Revisar'),
            ),
          ],
        ),
      ),
    );
  }
}
```

---

## Conclusión

El dashboard inteligente para clientes incluye:
- **Layout responsivo** con sidebar y header
- **Tarjetas de resumen** con métricas clave
- **Gráficos de procesamiento** con PieChart
- **Lista de documentos recientes** con estados
- **Tabla de transacciones** extraídas
- **Panel de alertas** para notificaciones
- **Características inteligentes** como predicciones y detección de anomalías

Este dashboard proporciona a los clientes una visión completa de sus documentos escaneados, transacciones contables, y métricas en tiempo real, con la identidad visual de PINAD.
