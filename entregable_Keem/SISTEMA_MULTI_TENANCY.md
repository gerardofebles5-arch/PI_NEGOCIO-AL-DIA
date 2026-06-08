# Implementación del Sistema Multi-tenancy para Vender a Otros Contadores

## Fecha
Junio 7, 2026

## Objetivo
Implementar un sistema multi-tenancy que permita vender el sistema de escaneo contable a otros contadores, con aislamiento completo de datos, roles y permisos, y panel de control para administración.

---

## 1. Arquitectura Multi-tenancy

```
┌─────────────────────────────────────────────────────────────────┐
│                    PINAD Platform (SaaS)                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Super Admin (PINAD)                                    │  │
│  │  - Panel de control global                              │  │
│  │  - Gestión de tenants (contadores)                      │  │
│  │  - Monitoreo de uso y facturación                       │  │
│  │  - Soporte técnico                                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Tenant 1 (Contador A)                                  │  │
│  │  - Admin del tenant                                     │  │
│  │  - Gestión de clientes                                  │  │
│  │  - Configuración de plan                                │  │
│  │  - Dashboard de uso                                     │  │
│  │  ┌────────────────────────────────────────────────┐    │  │
│  │  │  Clientes del Tenant 1                         │    │  │
│  │  │  - Cliente 1, Cliente 2, Cliente 3             │    │  │
│  │  │  - Acceso a su dashboard                        │    │  │
│  │  │  - Escaneo de documentos                         │    │  │
│  │  │  - Visualización de transacciones               │    │  │
│  │  └────────────────────────────────────────────────┘    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Tenant 2 (Contador B)                                  │  │
│  │  - Admin del tenant                                     │  │
│  │  - Gestión de clientes                                  │  │
│  │  - Configuración de plan                                │  │
│  │  - Dashboard de uso                                     │  │
│  │  ┌────────────────────────────────────────────────┐    │  │
│  │  │  Clientes del Tenant 2                         │    │  │
│  │  │  - Cliente 4, Cliente 5, Cliente 6             │    │  │
│  │  │  - Acceso a su dashboard                        │    │  │
│  │  │  - Escaneo de documentos                         │    │  │
│  │  │  - Visualización de transacciones               │    │  │
│  │  └────────────────────────────────────────────────┘    │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Data Isolation
                              │
┌─────────────────────────────────────────────────────────────────┐
│                    Base de Datos (Multi-tenant)                  │
│  - Firestore: tenant_id en todos los documentos                 │
│  - Cloud SQL: tenant_id en todas las tablas                     │
│  - Cloud Storage: /tenants/{tenant_id}/...                       │
│  - Aislamiento completo por tenant                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Roles y Permisos

### 2.1 Jerarquía de Roles

```
Super Admin (PINAD)
├── Tenant Admin (Contador)
│   ├── Client (Cliente del contador)
│   └── Viewer (Solo lectura)
└── Support (Soporte técnico)
```

### 2.2 Permisos por Rol

| Permiso | Super Admin | Tenant Admin | Client | Viewer | Support |
|---------|-------------|--------------|--------|--------|---------|
| Gestión de tenants | ✅ | ❌ | ❌ | ❌ | ❌ |
| Gestión de usuarios del tenant | ❌ | ✅ | ❌ | ❌ | ❌ |
| Escaneo de documentos | ❌ | ✅ | ✅ | ❌ | ❌ |
| Visualización de documentos | ✅ | ✅ | ✅ | ✅ | ✅ |
| Edición de transacciones | ❌ | ✅ | ❌ | ❌ | ❌ |
| Generación de reportes | ✅ | ✅ | ✅ | ✅ | ✅ |
| Exportación de datos | ✅ | ✅ | ✅ | ❌ | ✅ |
| Configuración del tenant | ❌ | ✅ | ❌ | ❌ | ❌ |
| Monitoreo de uso | ✅ | ✅ | ❌ | ❌ | ✅ |
| Soporte técnico | ✅ | ❌ | ❌ | ❌ | ✅ |

---

## 3. Implementación de Multi-tenancy

### 3.1 Middleware de Autenticación y Autorización

```typescript
// functions/src/middleware/auth.ts
import * as functions from 'firebase-functions';
import * as admin from 'firebase-admin';

export interface AuthContext {
  userId: string;
  tenantId: string;
  role: string;
  email: string;
}

export async function authenticateAndAuthorize(
  context: functions.https.CallableContext,
  requiredRole?: string
): Promise<AuthContext> {
  // Verificar autenticación
  if (!context.auth) {
    throw new functions.https.HttpsError(
      'unauthenticated',
      'User must be authenticated'
    );
  }

  const userId = context.auth.uid;
  const email = context.auth.token.email || '';

  // Obtener datos del usuario
  const userDoc = await admin.firestore().collection('users').doc(userId).get();
  
  if (!userDoc.exists) {
    throw new functions.https.HttpsError(
      'not-found',
      'User not found'
    );
  }

  const userData = userDoc.data() as any;
  const tenantId = userData.tenantId;
  const role = userData.role;

  // Verificar si el usuario está activo
  if (!userData.isActive) {
    throw new functions.https.HttpsError(
      'permission-denied',
      'User account is inactive'
    );
  }

  // Verificar si el tenant está activo
  const tenantDoc = await admin.firestore().collection('tenants').doc(tenantId).get();
  
  if (!tenantDoc.exists || !tenantDoc.data()?.isActive) {
    throw new functions.https.HttpsError(
      'permission-denied',
      'Tenant is inactive'
    );
  }

  // Verificar rol requerido
  if (requiredRole) {
    const roleHierarchy = {
      'viewer': 1,
      'client': 2,
      'admin': 3,
      'super_admin': 4,
      'support': 3,
    };

    const userRoleLevel = roleHierarchy[role] || 0;
    const requiredRoleLevel = roleHierarchy[requiredRole] || 0;

    if (userRoleLevel < requiredRoleLevel) {
      throw new functions.https.HttpsError(
        'permission-denied',
        'Insufficient permissions'
      );
    }
  }

  return {
    userId,
    tenantId,
    role,
    email,
  };
}

export async function checkTenantAccess(
  authContext: AuthContext,
  targetTenantId: string
): Promise<boolean> {
  // Super Admin puede acceder a cualquier tenant
  if (authContext.role === 'super_admin' || authContext.role === 'support') {
    return true;
  }

  // Tenant Admin solo puede acceder a su propio tenant
  if (authContext.role === 'admin' && authContext.tenantId === targetTenantId) {
    return true;
  }

  // Client y Viewer solo pueden acceder a su propio tenant
  if ((authContext.role === 'client' || authContext.role === 'viewer') && 
      authContext.tenantId === targetTenantId) {
    return true;
  }

  return false;
}
```

### 3.2 Servicio de Gestión de Tenants

```typescript
// functions/src/services/tenantService.ts
import * as admin from 'firebase-admin';
import { getPool } from '../config/database';

export class TenantService {
  async createTenant(data: CreateTenantData): Promise<string> {
    const db = admin.firestore();
    const pool = await getPool();

    // Crear tenant en Firestore
    const tenantRef = await db.collection('tenants').add({
      name: data.name,
      rif: data.rif,
      email: data.email,
      phone: data.phone,
      address: data.address,
      plan: data.plan || 'basic',
      maxUsers: this.getMaxUsersByPlan(data.plan),
      maxDocuments: this.getMaxDocumentsByPlan(data.plan),
      maxStorageGb: this.getMaxStorageByPlan(data.plan),
      currentUsers: 0,
      currentDocuments: 0,
      currentStorageGb: 0,
      isActive: true,
      createdAt: admin.firestore.FieldValue.serverTimestamp(),
      updatedAt: admin.firestore.FieldValue.serverTimestamp(),
    });

    const tenantId = tenantRef.id;

    // Crear tenant en Cloud SQL
    await pool.query(
      `INSERT INTO tenants (tenant_id, name, rif, email, phone, address, plan, max_users, max_documents, max_storage_gb, is_active)
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, true)`,
      [
        tenantId,
        data.name,
        data.rif,
        data.email,
        data.phone,
        data.address,
        data.plan || 'basic',
        this.getMaxUsersByPlan(data.plan),
        this.getMaxDocumentsByPlan(data.plan),
        this.getMaxStorageByPlan(data.plan),
      ]
    );

    // Crear usuario admin del tenant
    await this.createTenantAdmin(tenantId, data.adminEmail, data.adminPassword);

    // Crear carpeta en Cloud Storage
    const storage = admin.storage();
    const bucket = storage.bucket('pinad-documents');
    await bucket.file(`tenants/${tenantId}/.keep`).save('');

    return tenantId;
  }

  async createTenantAdmin(
    tenantId: string,
    email: string,
    password: string
  ): Promise<string> {
    const db = admin.firestore();

    // Crear usuario en Firebase Auth
    const userRecord = await admin.auth().createUser({
      email,
      password,
      emailVerified: true,
    });

    // Crear usuario en Firestore
    await db.collection('users').doc(userRecord.uid).set({
      userId: userRecord.uid,
      tenantId,
      email,
      role: 'admin',
      isActive: true,
      createdAt: admin.firestore.FieldValue.serverTimestamp(),
      updatedAt: admin.firestore.FieldValue.serverTimestamp(),
    });

    // Crear usuario en Cloud SQL
    const pool = await getPool();
    await pool.query(
      `INSERT INTO users (user_id, tenant_id, firebase_uid, email, role, is_active)
       VALUES ($1, $2, $3, $4, 'admin', true)`,
      [userRecord.uid, tenantId, userRecord.uid, email]
    );

    return userRecord.uid;
  }

  async getTenant(tenantId: string): Promise<Tenant> {
    const db = admin.firestore();
    const tenantDoc = await db.collection('tenants').doc(tenantId).get();

    if (!tenantDoc.exists) {
      throw new Error('Tenant not found');
    }

    return {
      id: tenantDoc.id,
      ...tenantDoc.data(),
    } as Tenant;
  }

  async updateTenant(tenantId: string, data: UpdateTenantData): Promise<void> {
    const db = admin.firestore();
    const pool = await getPool();

    // Actualizar en Firestore
    await db.collection('tenants').doc(tenantId).update({
      ...data,
      updatedAt: admin.firestore.FieldValue.serverTimestamp(),
    });

    // Actualizar en Cloud SQL
    const updates: string[] = [];
    const values: any[] = [];
    let paramIndex = 1;

    if (data.name) {
      updates.push(`name = $${paramIndex++}`);
      values.push(data.name);
    }
    if (data.plan) {
      updates.push(`plan = $${paramIndex++}`);
      values.push(data.plan);
    }
    if (data.maxUsers) {
      updates.push(`max_users = $${paramIndex++}`);
      values.push(data.maxUsers);
    }
    if (data.maxDocuments) {
      updates.push(`max_documents = $${paramIndex++}`);
      values.push(data.maxDocuments);
    }
    if (data.maxStorageGb) {
      updates.push(`max_storage_gb = $${paramIndex++}`);
      values.push(data.maxStorageGb);
    }

    if (updates.length > 0) {
      updates.push(`updated_at = CURRENT_TIMESTAMP`);
      values.push(tenantId);

      await pool.query(
        `UPDATE tenants SET ${updates.join(', ')} WHERE tenant_id = $${paramIndex}`,
        values
      );
    }
  }

  async deleteTenant(tenantId: string): Promise<void> {
    const db = admin.firestore();
    const pool = await getPool();

    // Marcar como inactivo en Firestore
    await db.collection('tenants').doc(tenantId).update({
      isActive: false,
      updatedAt: admin.firestore.FieldValue.serverTimestamp(),
    });

    // Marcar como inactivo en Cloud SQL
    await pool.query(
      `UPDATE tenants SET is_active = false, updated_at = CURRENT_TIMESTAMP WHERE tenant_id = $1`,
      [tenantId]
    );

    // Desactivar usuarios del tenant
    await db.collection('users')
      .where('tenantId', '==', tenantId)
      .get()
      .then((snapshot) => {
        snapshot.docs.forEach((doc) => {
          doc.ref.update({ isActive: false });
        });
      });

    await pool.query(
      `UPDATE users SET is_active = false WHERE tenant_id = $1`,
      [tenantId]
    );
  }

  async getTenantUsage(tenantId: string): Promise<TenantUsage> {
    const db = admin.firestore();
    const pool = await getPool();

    // Obtener documentos
    const documentsSnapshot = await db
      .collection('documents')
      .where('tenantId', '==', tenantId)
      .get();

    const totalDocuments = documentsSnapshot.size;
    let totalStorage = 0;

    for (const doc of documentsSnapshot.docs) {
      totalStorage += doc.data()?.fileSize || 0;
    }

    // Obtener usuarios
    const usersSnapshot = await db
      .collection('users')
      .where('tenantId', '==', tenantId)
      .where('isActive', '==', true)
      .get();

    const totalUsers = usersSnapshot.size;

    // Obtener transacciones del mes
    const transactionsResult = await pool.query(
      `SELECT COUNT(*) as count FROM transactions WHERE tenant_id = $1 
       AND EXTRACT(MONTH FROM created_at) = EXTRACT(MONTH FROM CURRENT_DATE)
       AND EXTRACT(YEAR FROM created_at) = EXTRACT(YEAR FROM CURRENT_DATE)`,
      [tenantId]
    );

    const monthlyTransactions = parseInt(transactionsResult.rows[0].count);

    return {
      totalDocuments,
      totalStorage: totalStorage / (1024 * 1024 * 1024), // Convertir a GB
      totalUsers,
      monthlyTransactions,
    };
  }

  private getMaxUsersByPlan(plan: string): number {
    switch (plan) {
      case 'basic':
        return 5;
      case 'pro':
        return 25;
      case 'enterprise':
        return 100;
      default:
        return 5;
    }
  }

  private getMaxDocumentsByPlan(plan: string): number {
    switch (plan) {
      case 'basic':
        return 1000;
      case 'pro':
        return 10000;
      case 'enterprise':
        return 100000;
      default:
        return 1000;
    }
  }

  private getMaxStorageByPlan(plan: string): number {
    switch (plan) {
      case 'basic':
        return 10;
      case 'pro':
        return 100;
      case 'enterprise':
        return 1000;
      default:
        return 10;
    }
  }
}
```

### 3.3 Cloud Functions para Gestión de Tenants

```typescript
// functions/src/index.ts
import * as functions from 'firebase-functions';
import { TenantService } from './services/tenantService';
import { authenticateAndAuthorize } from './middleware/auth';

const tenantService = new TenantService();

// Crear tenant (Solo Super Admin)
export const createTenant = functions.https.onCall(async (data, context) => {
  const authContext = await authenticateAndAuthorize(context, 'super_admin');

  try {
    const tenantId = await tenantService.createTenant(data);
    return { tenantId, status: 'created' };
  } catch (error) {
    throw new functions.https.HttpsError(
      'internal',
      error.message
    );
  }
});

// Obtener tenant (Super Admin o Tenant Admin)
export const getTenant = functions.https.onCall(async (data, context) => {
  const authContext = await authenticateAndAuthorize(context);

  const { tenantId } = data;

  // Verificar acceso al tenant
  if (authContext.role !== 'super_admin' && authContext.tenantId !== tenantId) {
    throw new functions.https.HttpsError(
      'permission-denied',
      'Access denied to this tenant'
    );
  }

  try {
    const tenant = await tenantService.getTenant(tenantId);
    return tenant;
  } catch (error) {
    throw new functions.https.HttpsError(
      'internal',
      error.message
    );
  }
});

// Actualizar tenant (Super Admin o Tenant Admin)
export const updateTenant = functions.https.onCall(async (data, context) => {
  const authContext = await authenticateAndAuthorize(context, 'admin');

  const { tenantId, ...updateData } = data;

  // Verificar acceso al tenant
  if (authContext.role !== 'super_admin' && authContext.tenantId !== tenantId) {
    throw new functions.https.HttpsError(
      'permission-denied',
      'Access denied to this tenant'
    );
  }

  try {
    await tenantService.updateTenant(tenantId, updateData);
    return { status: 'updated' };
  } catch (error) {
    throw new functions.https.HttpsError(
      'internal',
      error.message
    );
  }
});

// Eliminar tenant (Solo Super Admin)
export const deleteTenant = functions.https.onCall(async (data, context) => {
  const authContext = await authenticateAndAuthorize(context, 'super_admin');

  const { tenantId } = data;

  try {
    await tenantService.deleteTenant(tenantId);
    return { status: 'deleted' };
  } catch (error) {
    throw new functions.https.HttpsError(
      'internal',
      error.message
    );
  }
});

// Obtener uso del tenant (Super Admin o Tenant Admin)
export const getTenantUsage = functions.https.onCall(async (data, context) => {
  const authContext = await authenticateAndAuthorize(context, 'admin');

  const { tenantId } = data;

  // Verificar acceso al tenant
  if (authContext.role !== 'super_admin' && authContext.tenantId !== tenantId) {
    throw new functions.https.HttpsError(
      'permission-denied',
      'Access denied to this tenant'
    );
  }

  try {
    const usage = await tenantService.getTenantUsage(tenantId);
    return usage;
  } catch (error) {
    throw new functions.https.HttpsError(
      'internal',
      error.message
    );
  }
});

// Listar tenants (Solo Super Admin)
export const listTenants = functions.https.onCall(async (data, context) => {
  const authContext = await authenticateAndAuthorize(context, 'super_admin');

  const { limit = 50, offset = 0 } = data;

  try {
    const db = admin.firestore();
    const snapshot = await db
      .collection('tenants')
      .where('isActive', '==', true)
      .orderBy('createdAt', 'desc')
      .limit(limit)
      .offset(offset)
      .get();

    const tenants = snapshot.docs.map(doc => ({
      id: doc.id,
      ...doc.data(),
    }));

    return { tenants };
  } catch (error) {
    throw new functions.https.HttpsError(
      'internal',
      error.message
    );
  }
});
```

---

## 4. Panel de Control para Contadores (Tenant Admin)

### 4.1 Dashboard del Tenant Admin

```dart
// lib/presentation/pages/tenant_admin/tenant_admin_dashboard_page.dart
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../cubit/tenant_admin/tenant_admin_cubit.dart';
import '../../widgets/tenant_admin/tenant_stats_card.dart';
import '../../widgets/tenant_admin/clients_list.dart';
import '../../widgets/tenant_admin/usage_chart.dart';

class TenantAdminDashboardPage extends StatefulWidget {
  const TenantAdminDashboardPage({super.key});

  @override
  State<TenantAdminDashboardPage> createState() => _TenantAdminDashboardPageState();
}

class _TenantAdminDashboardPageState extends State<TenantAdminDashboardPage> {
  @override
  void initState() {
    super.initState();
    context.read<TenantAdminCubit>().loadDashboardData();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Panel de Control'),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () {
              Navigator.pushNamed(context, '/tenant-settings');
            },
          ),
        ],
      ),
      body: BlocBuilder<TenantAdminCubit, TenantAdminState>(
        builder: (context, state) {
          if (state is TenantAdminLoading) {
            return const Center(child: CircularProgressIndicator());
          } else if (state is TenantAdminLoaded) {
            return SingleChildScrollView(
              padding: const EdgeInsets.all(24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _TenantStatsCard(tenant: state.tenant, usage: state.usage),
                  const SizedBox(height: 24),
                  _UsageChart(usage: state.usage),
                  const SizedBox(height: 24),
                  _ClientsList(clients: state.clients),
                  const SizedBox(height: 24),
                  _UpgradePlanCard(plan: state.tenant.plan),
                ],
              ),
            );
          } else if (state is TenantAdminError) {
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
                      context.read<TenantAdminCubit>().loadDashboardData();
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
    );
  }
}
```

### 4.2 Tarjeta de Estadísticas del Tenant

```dart
// lib/presentation/widgets/tenant_admin/tenant_stats_card.dart
import 'package:flutter/material.dart';
import '../../../core/theme/app_theme.dart';

class _TenantStatsCard extends StatelessWidget {
  final Tenant tenant;
  final TenantUsage usage;

  const _TenantStatsCard({
    required this.tenant,
    required this.usage,
  });

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
                  tenant.name,
                  style: Theme.of(context).textTheme.headlineSmall,
                ),
                _PlanBadge(plan: tenant.plan),
              ],
            ),
            const SizedBox(height: 24),
            GridView.count(
              crossAxisCount: 4,
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              mainAxisSpacing: 16,
              crossAxisSpacing: 16,
              childAspectRatio: 2.5,
              children: [
                _StatItem(
                  label: 'Usuarios',
                  value: '${usage.totalUsers}/${tenant.maxUsers}',
                  icon: Icons.people,
                  color: AppColors.goldDark,
                ),
                _StatItem(
                  label: 'Documentos',
                  value: '${usage.totalDocuments}/${tenant.maxDocuments}',
                  icon: Icons.description,
                  color: AppColors.brownMedium,
                ),
                _StatItem(
                  label: 'Almacenamiento',
                  value: '${usage.totalStorage.toStringAsFixed(1)}/${tenant.maxStorageGb} GB',
                  icon: Icons.storage,
                  color: AppColors.orangeLight,
                ),
                _StatItem(
                  label: 'Transacciones/Mes',
                  value: usage.monthlyTransactions.toString(),
                  icon: Icons.receipt_long,
                  color: AppColors.goldBright,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _PlanBadge extends StatelessWidget {
  final String plan;

  const _PlanBadge({required this.plan});

  @override
  Widget build(BuildContext context) {
    final color = _getPlanColor(plan);
    final label = _getPlanLabel(plan);

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

  Color _getPlanColor(String plan) {
    switch (plan) {
      case 'basic':
        return AppColors.goldDark;
      case 'pro':
        return AppColors.brownMedium;
      case 'enterprise':
        return AppColors.goldBright;
      default:
        return AppColors.brownGray;
    }
  }

  String _getPlanLabel(String plan) {
    switch (plan) {
      case 'basic':
        return 'Básico';
      case 'pro':
        return 'Profesional';
      case 'enterprise':
        return 'Empresarial';
      default:
        return 'Desconocido';
    }
  }
}

class _StatItem extends StatelessWidget {
  final String label;
  final String value;
  final IconData icon;
  final Color color;

  const _StatItem({
    required this.label,
    required this.value,
    required this.icon,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(height: 8),
          Text(
            label,
            style: Theme.of(context).textTheme.bodySmall,
          ),
          const SizedBox(height: 4),
          Text(
            value,
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: AppColors.grayDark,
                ),
          ),
        ],
      ),
    );
  }
}
```

### 4.3 Lista de Clientes

```dart
// lib/presentation/widgets/tenant_admin/clients_list.dart
import 'package:flutter/material.dart';
import '../../../core/theme/app_theme.dart';

class _ClientsList extends StatelessWidget {
  final List<Client> clients;

  const _ClientsList({required this.clients});

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
                  'Clientes',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                ElevatedButton.icon(
                  onPressed: () {
                    // Mostrar diálogo para agregar cliente
                  },
                  icon: const Icon(Icons.add),
                  label: const Text('Agregar Cliente'),
                ),
              ],
            ),
            const SizedBox(height: 16),
            ListView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: clients.length,
              itemBuilder: (context, index) {
                final client = clients[index];
                return _ClientItem(client: client);
              },
            ),
          ],
        ),
      ),
    );
  }
}

class _ClientItem extends StatelessWidget {
  final Client client;

  const _ClientItem({required this.client});

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
          CircleAvatar(
            backgroundColor: AppColors.goldDark,
            child: Text(
              client.name[0].toUpperCase(),
              style: const TextStyle(color: Colors.white),
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  client.name,
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                const SizedBox(height: 4),
                Text(
                  client.email,
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: AppColors.brownGray,
                      ),
                ),
              ],
            ),
          ),
          _StatusChip(isActive: client.isActive),
          const SizedBox(width: 8),
          IconButton(
            icon: const Icon(Icons.more_vert),
            onPressed: () {
              // Mostrar opciones
            },
          ),
        ],
      ),
    );
  }
}

class _StatusChip extends StatelessWidget {
  final bool isActive;

  const _StatusChip({required this.isActive});

  @override
  Widget build(BuildContext context) {
    final color = isActive ? AppColors.brownMedium : AppColors.brownGray;
    final label = isActive ? 'Activo' : 'Inactivo';

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
}
```

### 4.4 Tarjeta de Actualización de Plan

```dart
// lib/presentation/widgets/tenant_admin/upgrade_plan_card.dart
import 'package:flutter/material.dart';
import '../../../core/theme/app_theme.dart';

class _UpgradePlanCard extends StatelessWidget {
  final String plan;

  const _UpgradePlanCard({required this.plan});

  @override
  Widget build(BuildContext context) {
    if (plan == 'enterprise') {
      return const SizedBox.shrink();
    }

    return Card(
      color: AppColors.goldDark.withOpacity(0.1),
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.star, color: AppColors.goldDark),
                const SizedBox(width: 8),
                Text(
                  'Actualiza tu Plan',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        color: AppColors.goldDark,
                      ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Text(
              'Desbloquea más usuarios, documentos y almacenamiento actualizando a un plan superior.',
              style: Theme.of(context).textTheme.bodyMedium,
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: _PlanOption(
                    plan: 'pro',
                    price: '\$99/mes',
                    features: [
                      '25 usuarios',
                      '10,000 documentos',
                      '100 GB almacenamiento',
                      'Soporte prioritario',
                    ],
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: _PlanOption(
                    plan: 'enterprise',
                    price: '\$299/mes',
                    features: [
                      '100 usuarios',
                      '100,000 documentos',
                      '1 TB almacenamiento',
                      'Soporte dedicado',
                      'API access',
                    ],
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _PlanOption extends StatelessWidget {
  final String plan;
  final String price;
  final List<String> features;

  const _PlanOption({
    required this.plan,
    required this.price,
    required this.features,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              plan.toUpperCase(),
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: AppColors.goldDark,
                  ),
            ),
            const SizedBox(height: 8),
            Text(
              price,
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    color: AppColors.grayDark,
                  ),
            ),
            const SizedBox(height: 16),
            ...features.map((feature) => Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Row(
                children: [
                  Icon(Icons.check, color: AppColors.brownMedium, size: 16),
                  const SizedBox(width: 8),
                  Text(
                    feature,
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                ],
              ),
            )),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () {
                // Iniciar proceso de actualización
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: AppColors.goldDark,
                minimumSize: const Size(double.infinity, 40),
              ),
              child: const Text('Actualizar'),
            ),
          ],
        ),
      ),
    );
  }
}
```

---

## 5. Panel de Control Super Admin (PINAD)

### 5.1 Dashboard del Super Admin

```dart
// lib/presentation/pages/super_admin/super_admin_dashboard_page.dart
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../cubit/super_admin/super_admin_cubit.dart';
import '../../widgets/super_admin/tenants_list.dart';
import '../../widgets/super_admin/revenue_chart.dart';

class SuperAdminDashboardPage extends StatefulWidget {
  const SuperAdminDashboardPage({super.key});

  @override
  State<SuperAdminDashboardPage> createState() => _SuperAdminDashboardPageState();
}

class _SuperAdminDashboardPageState extends State<SuperAdminDashboardPage> {
  @override
  void initState() {
    super.initState();
    context.read<SuperAdminCubit>().loadDashboardData();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Panel de Control - PINAD'),
        actions: [
          IconButton(
            icon: const Icon(Icons.add),
            onPressed: () {
              _showCreateTenantDialog(context);
            },
          ),
        ],
      ),
      body: BlocBuilder<SuperAdminCubit, SuperAdminState>(
        builder: (context, state) {
          if (state is SuperAdminLoading) {
            return const Center(child: CircularProgressIndicator());
          } else if (state is SuperAdminLoaded) {
            return SingleChildScrollView(
              padding: const EdgeInsets.all(24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _RevenueStats(revenue: state.revenue),
                  const SizedBox(height: 24),
                  _RevenueChart(revenue: state.revenue),
                  const SizedBox(height: 24),
                  _TenantsList(tenants: state.tenants),
                ],
              ),
            );
          } else if (state is SuperAdminError) {
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
                      context.read<SuperAdminCubit>().loadDashboardData();
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
    );
  }

  void _showCreateTenantDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => _CreateTenantDialog(),
    );
  }
}
```

---

## 6. Facturación y Pagos

### 6.1 Integración con Stripe

```typescript
// functions/src/services/billingService.ts
import Stripe from 'stripe';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY || '');

export class BillingService {
  async createSubscription(
    tenantId: string,
    plan: string,
    paymentMethodId: string
  ): Promise<Stripe.Subscription> {
    // Crear cliente en Stripe
    const customer = await stripe.customers.create({
      metadata: { tenantId },
    });

    // Crear suscripción
    const subscription = await stripe.subscriptions.create({
      customer: customer.id,
      items: [{ price: this.getPlanPriceId(plan) }],
      default_payment_method: paymentMethodId,
    });

    return subscription;
  }

  async cancelSubscription(subscriptionId: string): Promise<Stripe.Subscription> {
    return await stripe.subscriptions.cancel(subscriptionId);
  }

  async upgradeSubscription(
    subscriptionId: string,
    newPlan: string
  ): Promise<Stripe.Subscription> {
    const subscription = await stripe.subscriptions.retrieve(subscriptionId);
    
    return await stripe.subscriptions.update(subscriptionId, {
      items: [{
        id: subscription.items.data[0].id,
        price: this.getPlanPriceId(newPlan),
      }],
    });
  }

  private getPlanPriceId(plan: string): string {
    switch (plan) {
      case 'basic':
        return process.env.STRIPE_PRICE_BASIC || '';
      case 'pro':
        return process.env.STRIPE_PRICE_PRO || '';
      case 'enterprise':
        return process.env.STRIPE_PRICE_ENTERPRISE || '';
      default:
        return '';
    }
  }
}
```

---

## 7. Monitoreo y Alertas

### 7.1 Cloud Function para Monitoreo de Cuotas

```typescript
// functions/src/index.ts
export const monitorQuotas = functions.pubsub
  .schedule('0 */6 * * *') // Cada 6 horas
  .onRun(async (context) => {
    const db = admin.firestore();
    const tenantsSnapshot = await db.collection('tenants').get();

    for (const tenantDoc of tenantsSnapshot.docs) {
      const tenant = tenantDoc.data() as any;
      const tenantId = tenantDoc.id;

      // Obtener uso actual
      const usage = await tenantService.getTenantUsage(tenantId);

      // Verificar si excede cuota
      if (usage.totalUsers >= tenant.maxUsers) {
        await sendQuotaAlert(tenantId, 'users', usage.totalUsers, tenant.maxUsers);
      }

      if (usage.totalDocuments >= tenant.maxDocuments) {
        await sendQuotaAlert(tenantId, 'documents', usage.totalDocuments, tenant.maxDocuments);
      }

      if (usage.totalStorage >= tenant.maxStorageGb) {
        await sendQuotaAlert(tenantId, 'storage', usage.totalStorage, tenant.maxStorageGb);
      }
    }

    return null;
  });

async function sendQuotaAlert(
  tenantId: string,
  resourceType: string,
  current: number,
  max: number
): Promise<void> {
  const db = admin.firestore();

  // Enviar notificación al admin del tenant
  const adminSnapshot = await db
    .collection('users')
    .where('tenantId', '==', tenantId)
    .where('role', '==', 'admin')
    .get();

  for (const adminDoc of adminSnapshot.docs) {
    await db.collection('notifications').add({
      tenantId,
      userId: adminDoc.id,
      type: 'quota_exceeded',
      title: 'Cuota Excedida',
      message: `Has excedido tu cuota de ${resourceType}: ${current}/${max}`,
      data: { resourceType, current, max },
      isRead: false,
      createdAt: admin.firestore.FieldValue.serverTimestamp(),
    });
  }
}
```

---

## Conclusión

El sistema multi-tenancy incluye:
- **Aislamiento completo de datos** por tenant en Firestore, Cloud SQL y Cloud Storage
- **Roles y permisos** jerárquicos (Super Admin, Tenant Admin, Client, Viewer, Support)
- **Panel de control para contadores** con estadísticas de uso y gestión de clientes
- **Panel de control Super Admin** para gestión de tenants y monitoreo global
- **Facturación integrada** con Stripe para planes básico, pro y enterprise
- **Monitoreo de cuotas** con alertas automáticas
- **Sistema de actualización de planes** con límites escalables

Este sistema permite vender la plataforma a otros contadores como un servicio SaaS, con aislamiento completo de datos y gestión centralizada.
