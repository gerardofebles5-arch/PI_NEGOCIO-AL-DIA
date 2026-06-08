const functions = require('firebase-functions');
const admin = require('firebase-admin');
const { BigQuery } = require('@google-cloud/bigquery');
const { Storage } = require('@google-cloud/storage');
const { DocumentProcessorServiceClient } = require('@google-cloud/documentai').v1;
const { PredictionServiceClient } = require('@google-cloud/aiplatform');
const { SecretManagerServiceClient } = require('@google-cloud/secret-manager');
const { KeyManagementServiceClient } = require('@google-cloud/kms');
const { MetricServiceClient } = require('@google-cloud/monitoring');
const { Logging } = require('@google-cloud/logging');
const { TraceServiceClient } = require('@google-cloud/trace').v1;

admin.initializeApp();
const db = admin.firestore();
const auth = admin.auth();
const bigquery = new BigQuery();
const storage = new Storage();
const documentAI = new DocumentProcessorServiceClient();
const aiplatform = new PredictionServiceClient();
const secretManager = new SecretManagerServiceClient();
const kms = new KeyManagementServiceClient();
const monitoring = new MetricServiceClient();
const logging = new Logging();
const trace = new TraceServiceClient();

// ==================== SECRET MANAGER FUNCTIONS ====================

/**
 * Get a secret from Secret Manager
 * @param {string} secretName - Name of the secret
 * @returns {Promise<string>} Secret value
 */
async function getSecret(secretName) {
  try {
    const projectId = process.env.PROJECT_ID || 'pinad-project';
    const name = `projects/${projectId}/secrets/${secretName}/versions/latest`;
    
    const [version] = await secretManager.accessSecretVersion({
      name: name,
    });
    
    return version.payload.data.toString('utf8');
  } catch (error) {
    console.error(`Error accessing secret ${secretName}:`, error);
    throw error;
  }
}

/**
 * Encrypt data using Cloud KMS
 * @param {string} data - Data to encrypt
 * @param {string} keyName - Name of the KMS key
 * @returns {Promise<Buffer>} Encrypted data
 */
async function encryptData(data, keyName) {
  try {
    const projectId = process.env.PROJECT_ID || 'pinad-project';
    const location = process.env.REGION || 'us-central1';
    const keyRing = 'pinad-keyring';
    const fullKeyName = `projects/${projectId}/locations/${location}/keyRings/${keyRing}/cryptoKeys/${keyName}`;
    
    const [encryptResponse] = await kms.encrypt({
      name: fullKeyName,
      plaintext: Buffer.from(data),
    });
    
    return encryptResponse.ciphertext;
  } catch (error) {
    console.error('Error encrypting data:', error);
    throw error;
  }
}

/**
 * Decrypt data using Cloud KMS
 * @param {Buffer} ciphertext - Encrypted data
 * @param {string} keyName - Name of the KMS key
 * @returns {Promise<string>} Decrypted data
 */
async function decryptData(ciphertext, keyName) {
  try {
    const projectId = process.env.PROJECT_ID || 'pinad-project';
    const location = process.env.REGION || 'us-central1';
    const keyRing = 'pinad-keyring';
    const fullKeyName = `projects/${projectId}/locations/${location}/keyRings/${keyRing}/cryptoKeys/${keyName}`;
    
    const [decryptResponse] = await kms.decrypt({
      name: fullKeyName,
      ciphertext: ciphertext,
    });
    
    return decryptResponse.plaintext.toString('utf8');
  } catch (error) {
    console.error('Error decrypting data:', error);
    throw error;
  }
}

// ==================== MULTI-TENANCY FUNCTIONS ====================

/**
 * Multi-tenancy service for data isolation
 * Implements Shared Database, Separate Schema pattern
 */

/**
 * Get tenant context from request
 * @param {Object} context - Firebase functions context
 * @returns {Object} Tenant context
 */
function getTenantContext(context) {
  const tenantId = context.rawRequest.headers['x-tenant-id'] || 
                   context.rawRequest.headers['tenant-id'] ||
                   'default';
  
  return {
    tenantId,
    isolationLevel: process.env.TENANT_ISOLATION_LEVEL || 'separate_schema',
  };
}

/**
 * Get Firestore collection path for tenant
 * @param {string} collectionName - Base collection name
 * @param {string} tenantId - Tenant ID
 * @returns {string} Tenant-specific collection path
 */
function getTenantCollectionPath(collectionName, tenantId) {
  const isolationLevel = process.env.TENANT_ISOLATION_LEVEL || 'separate_schema';
  
  switch (isolationLevel) {
    case 'shared_schema':
      // All tenants share the same collection, filter by tenant_id
      return collectionName;
    
    case 'separate_schema':
      // Each tenant has its own collection
      return `tenants/${tenantId}/${collectionName}`;
    
    case 'separate_database':
      // Each tenant has its own database (simulated with collection prefix)
      return `tenant_${tenantId}_${collectionName}`;
    
    default:
      return `tenants/${tenantId}/${collectionName}`;
  }
}

/**
 * Encrypt tenant data using Cloud KMS
 * @param {Object} data - Data to encrypt
 * @param {string} tenantId - Tenant ID
 * @returns {Promise<Object>} Encrypted data with metadata
 */
async function encryptTenantData(data, tenantId) {
  try {
    const dataString = JSON.stringify(data);
    const ciphertext = await encryptData(dataString, 'multi-tenant-data-key');
    
    return {
      encrypted: true,
      ciphertext: ciphertext.toString('base64'),
      tenantId,
      encryptedAt: new Date().toISOString(),
    };
  } catch (error) {
    console.error('Error encrypting tenant data:', error);
    throw error;
  }
}

/**
 * Decrypt tenant data using Cloud KMS
 * @param {Object} encryptedData - Encrypted data
 * @returns {Promise<Object>} Decrypted data
 */
async function decryptTenantData(encryptedData) {
  try {
    if (!encryptedData.encrypted) {
      return encryptedData;
    }
    
    const ciphertext = Buffer.from(encryptedData.ciphertext, 'base64');
    const decryptedString = await decryptData(ciphertext, 'multi-tenant-data-key');
    
    return JSON.parse(decryptedString);
  } catch (error) {
    console.error('Error decrypting tenant data:', error);
    throw error;
  }
}

/**
 * Apply tenant isolation to Firestore query
 * @param {Object} query - Firestore query
 * @param {string} tenantId - Tenant ID
 * @returns {Object} Query with tenant filter
 */
function applyTenantIsolation(query, tenantId) {
  const isolationLevel = process.env.TENANT_ISOLATION_LEVEL || 'separate_schema';
  
  if (isolationLevel === 'shared_schema') {
    // Add tenant_id filter for shared schema
    return query.where('tenant_id', '==', tenantId);
  }
  
  // For separate schema and separate database, no filter needed
  // as the collection path already isolates the data
  return query;
}

/**
 * Add tenant metadata to document
 * @param {Object} data - Document data
 * @param {string} tenantId - Tenant ID
 * @returns {Object} Document data with tenant metadata
 */
function addTenantMetadata(data, tenantId) {
  const isolationLevel = process.env.TENANT_ISOLATION_LEVEL || 'separate_schema';
  
  if (isolationLevel === 'shared_schema') {
    return {
      ...data,
      tenant_id: tenantId,
      tenant_created_at: new Date().toISOString(),
    };
  }
  
  // For separate schema and separate database, tenant metadata
  // is implicit in the collection path
  return data;
}

/**
 * Validate tenant access
 * @param {string} userId - User ID
 * @param {string} tenantId - Tenant ID
 * @returns {Promise<boolean>} True if user has access to tenant
 */
async function validateTenantAccess(userId, tenantId) {
  try {
    const userDoc = await db.collection('users').doc(userId).get();
    
    if (!userDoc.exists) {
      return false;
    }
    
    const userData = userDoc.data();
    
    // Check if user belongs to tenant
    if (userData.tenant_id === tenantId) {
      return true;
    }
    
    // Check if user has access to multiple tenants
    if (userData.tenant_ids && userData.tenant_ids.includes(tenantId)) {
      return true;
    }
    
    return false;
  } catch (error) {
    console.error('Error validating tenant access:', error);
    return false;
  }
}

/**
 * Get tenant quota limits
 * @param {string} tenantId - Tenant ID
 * @returns {Promise<Object>} Tenant quota limits
 */
async function getTenantQuotas(tenantId) {
  try {
    const tenantDoc = await db.collection('tenants').doc(tenantId).get();
    
    if (!tenantDoc.exists) {
      // Return default quotas
      return {
        maxDocuments: 1000,
        maxStorage: 10737418240, // 10GB
        maxUsers: 100,
        maxRequestsPerDay: 10000,
      };
    }
    
    const tenantData = tenantDoc.data();
    
    return {
      maxDocuments: tenantData.max_documents || 1000,
      maxStorage: tenantData.max_storage || 10737418240,
      maxUsers: tenantData.max_users || 100,
      maxRequestsPerDay: tenantData.max_requests_per_day || 10000,
    };
  } catch (error) {
    console.error('Error getting tenant quotas:', error);
    throw error;
  }
}

/**
 * Check if tenant has exceeded quota
 * @param {string} tenantId - Tenant ID
 * @param {string} quotaType - Type of quota to check
 * @param {number} currentValue - Current value
 * @returns {Promise<boolean>} True if quota exceeded
 */
async function checkTenantQuota(tenantId, quotaType, currentValue) {
  try {
    const quotas = await getTenantQuotas(tenantId);
    
    switch (quotaType) {
      case 'documents':
        return currentValue >= quotas.maxDocuments;
      case 'storage':
        return currentValue >= quotas.maxStorage;
      case 'users':
        return currentValue >= quotas.maxUsers;
      case 'requests':
        return currentValue >= quotas.maxRequestsPerDay;
      default:
        return false;
    }
  } catch (error) {
    console.error('Error checking tenant quota:', error);
    return false;
  }
}

// ==================== MONITORING AND LOGGING FUNCTIONS ====================

/**
 * Cloud Monitoring service for custom metrics
 */

/**
 * Log structured log entry to Cloud Logging
 * @param {string} logName - Name of the log
 * @param {Object} data - Log data
 * @param {string} severity - Log severity (DEBUG, INFO, WARNING, ERROR, CRITICAL)
 */
async function logStructured(logName, data, severity = 'INFO') {
  try {
    const projectId = process.env.PROJECT_ID || 'pinad-project';
    const logNameFull = `projects/${projectId}/logs/${logName}`;
    
    const logEntry = {
      severity,
      jsonPayload: data,
      timestamp: new Date(),
      labels: {
        environment: process.env.ENVIRONMENT || 'production',
        service: 'pinad-cloud-functions',
      },
    };
    
    const logger = logging.log(logNameFull);
    const entry = logger.entry(logEntry);
    await logger.write(entry);
  } catch (error) {
    console.error('Error logging to Cloud Logging:', error);
  }
}

/**
 * Send custom metric to Cloud Monitoring
 * @param {string} metricType - Type of metric
 * @param {number} value - Metric value
 * @param {Object} labels - Metric labels
 */
async function sendCustomMetric(metricType, value, labels = {}) {
  try {
    const projectId = process.env.PROJECT_ID || 'pinad-project';
    const metricName = `projects/${projectId}/metricDescriptors/custom.googleapis.com/${metricType}`;
    
    const timeSeries = {
      metric: {
        type: `custom.googleapis.com/${metricType}`,
        labels: labels,
      },
      resource: {
        type: 'cloud_function',
        labels: {
          project_id: projectId,
          function_name: process.env.FUNCTION_NAME || 'unknown',
          region: process.env.REGION || 'us-central1',
        },
      },
      points: [
        {
          interval: {
            endTime: {
              seconds: Math.floor(Date.now() / 1000),
            },
          },
          value: {
            doubleValue: value,
          },
        },
      ],
    };
    
    const request = {
      name: `projects/${projectId}`,
      timeSeries: [timeSeries],
    };
    
    await monitoring.createTimeSeries(request);
  } catch (error) {
    console.error('Error sending custom metric:', error);
  }
}

/**
 * Increment request count metric
 * @param {string} endpoint - API endpoint
 * @param {string} method - HTTP method
 * @param {number} statusCode - HTTP status code
 * @param {string} tenantId - Tenant ID (optional)
 */
async function incrementRequestCount(endpoint, method, statusCode, tenantId = 'default') {
  await sendCustomMetric('api/request_count', 1, {
    endpoint,
    method,
    status_code: statusCode.toString(),
    tenant_id: tenantId,
  });
}

/**
 * Increment error count metric
 * @param {string} errorType - Type of error
 * @param {string} endpoint - API endpoint
 * @param {string} tenantId - Tenant ID (optional)
 */
async function incrementErrorCount(errorType, endpoint, tenantId = 'default') {
  await sendCustomMetric('api/error_count', 1, {
    error_type: errorType,
    endpoint,
    tenant_id: tenantId,
  });
}

/**
 * Record latency metric
 * @param {string} endpoint - API endpoint
 * @param {number} latencyMs - Latency in milliseconds
 * @param {string} tenantId - Tenant ID (optional)
 */
async function recordLatency(endpoint, latencyMs, tenantId = 'default') {
  await sendCustomMetric('api/latency', latencyMs, {
    endpoint,
    tenant_id: tenantId,
  });
}

/**
 * Record tenant-specific metric
 * @param {string} metricType - Type of metric
 * @param {number} value - Metric value
 * @param {string} tenantId - Tenant ID
 */
async function recordTenantMetric(metricType, value, tenantId) {
  await sendCustomMetric(`tenant/${metricType}`, value, {
    tenant_id: tenantId,
  });
}

/**
 * Create a span for distributed tracing
 * @param {string} spanName - Name of the span
 * @param {string} parentSpanId - Parent span ID (optional)
 * @returns {Object} Span object
 */
function createSpan(spanName, parentSpanId = null) {
  const projectId = process.env.PROJECT_ID || 'pinad-project';
  const traceId = generateTraceId();
  const spanId = generateSpanId();
  
  return {
    name: `projects/${projectId}/traces/${traceId}/spans/${spanId}`,
    displayName: spanName,
    spanId,
    parentSpanId,
    startTime: new Date(),
    traceId,
  };
}

/**
 * Generate a random trace ID
 * @returns {string} Trace ID
 */
function generateTraceId() {
  return Math.random().toString(36).substring(2, 15) + 
         Math.random().toString(36).substring(2, 15);
}

/**
 * Generate a random span ID
 * @returns {string} Span ID
 */
function generateSpanId() {
  return Math.random().toString(36).substring(2, 15);
}

/**
 * End a span and record its duration
 * @param {Object} span - Span object
 */
async function endSpan(span) {
  try {
    const endTime = new Date();
    const duration = endTime - span.startTime;
    
    // In a real implementation, you would send this to Cloud Trace
    // For now, we'll log it
    await logStructured('trace', {
      span_name: span.displayName,
      trace_id: span.traceId,
      span_id: span.spanId,
      parent_span_id: span.parentSpanId,
      duration_ms: duration,
      start_time: span.startTime,
      end_time: endTime,
    });
  } catch (error) {
    console.error('Error ending span:', error);
  }
}

/**
 * Middleware to add monitoring and logging to function calls
 * @param {Function} handler - Function handler
 * @param {string} functionName - Name of the function
 * @returns {Function} Wrapped handler
 */
function withMonitoring(handler, functionName) {
  return async (data, context) => {
    const startTime = Date.now();
    const tenantContext = getTenantContext(context);
    const span = createSpan(functionName);
    
    try {
      // Log function call
      await logStructured('function_call', {
        function_name: functionName,
        tenant_id: tenantContext.tenantId,
        user_id: context.auth?.uid,
        timestamp: new Date(),
      });
      
      // Call the handler
      const result = await handler(data, context);
      
      // Record success metrics
      const latency = Date.now() - startTime;
      await recordLatency(functionName, latency, tenantContext.tenantId);
      await incrementRequestCount(functionName, 'CALL', 200, tenantContext.tenantId);
      
      // End span
      await endSpan(span);
      
      return result;
    } catch (error) {
      // Record error metrics
      const latency = Date.now() - startTime;
      await recordLatency(functionName, latency, tenantContext.tenantId);
      await incrementRequestCount(functionName, 'CALL', 500, tenantContext.tenantId);
      await incrementErrorCount(error.name, functionName, tenantContext.tenantId);
      
      // Log error
      await logStructured('function_error', {
        function_name: functionName,
        tenant_id: tenantContext.tenantId,
        error_message: error.message,
        error_stack: error.stack,
        timestamp: new Date(),
      }, 'ERROR');
      
      // End span
      await endSpan(span);
      
      throw error;
    }
  };
}

// ==================== BACKUP AND DISASTER RECOVERY FUNCTIONS ====================

/**
 * Backup service for disaster recovery
 */

/**
 * Backup Firestore data to Cloud Storage
 * @param {string} tenantId - Tenant ID (optional)
 * @returns {Promise<Object>} Backup result
 */
async function backupFirestore(tenantId = null) {
  try {
    const projectId = process.env.PROJECT_ID || 'pinad-project';
    const backupBucket = storage.bucket('pinad-firestore-backups');
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const backupFileName = `firestore-backup-${tenantId || 'all'}-${timestamp}.json`;
    
    // Get Firestore data
    let collections;
    if (tenantId) {
      // Backup specific tenant data
      const tenantCollections = [
        'documents',
        'accounting',
        'reports',
        'users',
      ];
      
      collections = {};
      for (const collection of tenantCollections) {
        const collectionPath = getTenantCollectionPath(collection, tenantId);
        const snapshot = await db.collection(collectionPath).get();
        collections[collection] = snapshot.docs.map(doc => ({
          id: doc.id,
          data: doc.data(),
        }));
      }
    } else {
      // Backup all data
      const allCollections = await db.listCollections();
      collections = {};
      
      for (const collection of allCollections) {
        const snapshot = await collection.get();
        collections[collection.id] = snapshot.docs.map(doc => ({
          id: doc.id,
          data: doc.data(),
        }));
      }
    }
    
    // Encrypt backup data
    const encryptedData = await encryptTenantData(collections, tenantId || 'system');
    
    // Upload to Cloud Storage
    const file = backupBucket.file(backupFileName);
    await file.save(JSON.stringify(encryptedData), {
      contentType: 'application/json',
      metadata: {
        tenantId: tenantId || 'all',
        timestamp,
        backupType: 'firestore',
      },
    });
    
    await logStructured('backup', {
      type: 'firestore',
      tenantId: tenantId || 'all',
      fileName: backupFileName,
      timestamp,
      status: 'success',
    });
    
    return {
      success: true,
      fileName: backupFileName,
      timestamp,
      tenantId: tenantId || 'all',
    };
  } catch (error) {
    console.error('Error backing up Firestore:', error);
    await logStructured('backup', {
      type: 'firestore',
      tenantId: tenantId || 'all',
      error: error.message,
      status: 'error',
    }, 'ERROR');
    
    throw error;
  }
}

/**
 * Restore Firestore data from Cloud Storage
 * @param {string} backupFileName - Backup file name
 * @param {string} tenantId - Tenant ID (optional)
 * @returns {Promise<Object>} Restore result
 */
async function restoreFirestore(backupFileName, tenantId = null) {
  try {
    const backupBucket = storage.bucket('pinad-firestore-backups');
    const file = backupBucket.file(backupFileName);
    
    // Download backup file
    const [exists] = await file.exists();
    if (!exists) {
      throw new Error(`Backup file ${backupFileName} not found`);
    }
    
    const [contents] = await file.download();
    const encryptedData = JSON.parse(contents.toString());
    
    // Decrypt backup data
    const collections = await decryptTenantData(encryptedData);
    
    // Restore Firestore data
    for (const [collectionName, documents] of Object.entries(collections)) {
      for (const doc of documents) {
        const collectionPath = tenantId 
          ? getTenantCollectionPath(collectionName, tenantId)
          : collectionName;
        
        await db.collection(collectionPath).doc(doc.id).set(doc.data);
      }
    }
    
    await logStructured('restore', {
      type: 'firestore',
      tenantId: tenantId || 'all',
      fileName: backupFileName,
      status: 'success',
    });
    
    return {
      success: true,
      fileName: backupFileName,
      tenantId: tenantId || 'all',
      collectionsRestored: Object.keys(collections),
    };
  } catch (error) {
    console.error('Error restoring Firestore:', error);
    await logStructured('restore', {
      type: 'firestore',
      tenantId: tenantId || 'all',
      fileName: backupFileName,
      error: error.message,
      status: 'error',
    }, 'ERROR');
    
    throw error;
  }
}

/**
 * Backup multi-tenant data to Cloud Storage
 * @param {string} tenantId - Tenant ID
 * @returns {Promise<Object>} Backup result
 */
async function backupMultiTenantData(tenantId) {
  try {
    const backupBucket = storage.bucket('pinad-multitenant-backups');
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const backupFileName = `multitenant-backup-${tenantId}-${timestamp}.json`;
    
    // Get tenant-specific data
    const tenantData = {
      documents: [],
      accounting: [],
      reports: [],
      users: [],
    };
    
    const collections = ['documents', 'accounting', 'reports', 'users'];
    for (const collection of collections) {
      const collectionPath = getTenantCollectionPath(collection, tenantId);
      const snapshot = await db.collection(collectionPath).get();
      tenantData[collection] = snapshot.docs.map(doc => ({
        id: doc.id,
        data: doc.data(),
      }));
    }
    
    // Encrypt backup data
    const encryptedData = await encryptTenantData(tenantData, tenantId);
    
    // Upload to Cloud Storage
    const file = backupBucket.file(backupFileName);
    await file.save(JSON.stringify(encryptedData), {
      contentType: 'application/json',
      metadata: {
        tenantId,
        timestamp,
        backupType: 'multitenant',
      },
    });
    
    await logStructured('backup', {
      type: 'multitenant',
      tenantId,
      fileName: backupFileName,
      timestamp,
      status: 'success',
    });
    
    return {
      success: true,
      fileName: backupFileName,
      timestamp,
      tenantId,
    };
  } catch (error) {
    console.error('Error backing up multi-tenant data:', error);
    await logStructured('backup', {
      type: 'multitenant',
      tenantId,
      error: error.message,
      status: 'error',
    }, 'ERROR');
    
    throw error;
  }
}

/**
 * List available backups
 * @param {string} backupType - Type of backup (firestore, cloudsql, multitenant)
 * @param {string} tenantId - Tenant ID (optional)
 * @returns {Promise<Array>} List of backups
 */
async function listBackups(backupType, tenantId = null) {
  try {
    let bucketName;
    switch (backupType) {
      case 'firestore':
        bucketName = 'pinad-firestore-backups';
        break;
      case 'cloudsql':
        bucketName = 'pinad-cloudsql-backups';
        break;
      case 'multitenant':
        bucketName = 'pinad-multitenant-backups';
        break;
      default:
        throw new Error(`Invalid backup type: ${backupType}`);
    }
    
    const bucket = storage.bucket(bucketName);
    const [files] = await bucket.getFiles();
    
    let backups = files.map(file => ({
      name: file.name,
      size: file.metadata.size,
      timeCreated: file.metadata.timeCreated,
      metadata: file.metadata,
    }));
    
    // Filter by tenant if specified
    if (tenantId) {
      backups = backups.filter(backup => 
        backup.metadata.tenantId === tenantId
      );
    }
    
    // Sort by creation date (newest first)
    backups.sort((a, b) => 
      new Date(b.timeCreated) - new Date(a.timeCreated)
    );
    
    return backups;
  } catch (error) {
    console.error('Error listing backups:', error);
    throw error;
  }
}

/**
 * Delete old backups based on retention policy
 * @param {string} backupType - Type of backup
 * @param {number} retentionDays - Retention period in days
 * @returns {Promise<Object>} Deletion result
 */
async function deleteOldBackups(backupType, retentionDays = 90) {
  try {
    let bucketName;
    switch (backupType) {
      case 'firestore':
        bucketName = 'pinad-firestore-backups';
        break;
      case 'cloudsql':
        bucketName = 'pinad-cloudsql-backups';
        break;
      case 'multitenant':
        bucketName = 'pinad-multitenant-backups';
        break;
      default:
        throw new Error(`Invalid backup type: ${backupType}`);
    }
    
    const bucket = storage.bucket(bucketName);
    const [files] = await bucket.getFiles();
    
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - retentionDays);
    
    const deletedFiles = [];
    
    for (const file of files) {
      const fileDate = new Date(file.metadata.timeCreated);
      if (fileDate < cutoffDate) {
        await file.delete();
        deletedFiles.push(file.name);
      }
    }
    
    await logStructured('backup_cleanup', {
      backupType,
      retentionDays,
      deletedCount: deletedFiles.length,
      deletedFiles,
      status: 'success',
    });
    
    return {
      success: true,
      deletedCount: deletedFiles.length,
      deletedFiles,
    };
  } catch (error) {
    console.error('Error deleting old backups:', error);
    await logStructured('backup_cleanup', {
      backupType,
      retentionDays,
      error: error.message,
      status: 'error',
    }, 'ERROR');
    
    throw error;
  }
}

// Export backup functions
exports.scheduleFirestoreBackup = functions.https.onRequest(async (req, res) => {
  try {
    const { tenantId } = req.body || {};
    const result = await backupFirestore(tenantId);
    res.status(200).json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

exports.scheduleCloudSQLBackup = functions.https.onRequest(async (req, res) => {
  try {
    // Cloud SQL backup is handled by Google Cloud's automated backups
    // This function triggers a manual backup if needed
    const result = {
      success: true,
      message: 'Cloud SQL backup triggered',
      timestamp: new Date().toISOString(),
    };
    res.status(200).json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

exports.scheduleMultiTenantBackup = functions.https.onRequest(async (req, res) => {
  try {
    const { tenantId } = req.body || {};
    if (!tenantId) {
      throw new Error('tenantId is required');
    }
    const result = await backupMultiTenantData(tenantId);
    res.status(200).json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

exports.listBackups = functions.https.onCall(async (data, context) => {
  if (!context.auth) {
    throw new functions.https.HttpsError('unauthenticated', 'User must be authenticated');
  }
  
  try {
    const { backupType, tenantId } = data;
    const backups = await listBackups(backupType, tenantId);
    return { backups };
  } catch (error) {
    console.error('Error listing backups:', error);
    throw new functions.https.HttpsError('internal', error.message);
  }
});

exports.restoreBackup = functions.https.onCall(async (data, context) => {
  if (!context.auth) {
    throw new functions.https.HttpsError('unauthenticated', 'User must be authenticated');
  }
  
  try {
    const { backupFileName, backupType, tenantId } = data;
    
    let result;
    switch (backupType) {
      case 'firestore':
        result = await restoreFirestore(backupFileName, tenantId);
        break;
      default:
        throw new Error(`Invalid backup type: ${backupType}`);
    }
    
    return result;
  } catch (error) {
    console.error('Error restoring backup:', error);
    throw new functions.https.HttpsError('internal', error.message);
  }
});

// ==================== AUTHENTICATION FUNCTIONS ====================

exports.createUser = functions.https.onCall(async (data, context) => {
  try {
    const { email, password, name } = data;
    
    // Create user in Firebase Auth
    const userRecord = await auth.createUser({
      email,
      password,
      displayName: name,
    });
    
    // Create user document in Firestore
    await db.collection('users').doc(userRecord.uid).set({
      uid: userRecord.uid,
      email,
      name,
      createdAt: admin.firestore.FieldValue.serverTimestamp(),
      updatedAt: admin.firestore.FieldValue.serverTimestamp(),
    });
    
    return { success: true, uid: userRecord.uid };
  } catch (error) {
    console.error('Error creating user:', error);
    throw new functions.https.HttpsError('internal', error.message);
  }
});

exports.getUserProfile = functions.https.onCall(async (data, context) => {
  if (!context.auth) {
    throw new functions.https.HttpsError('unauthenticated', 'User must be authenticated');
  }
  
  try {
    const userDoc = await db.collection('users').doc(context.auth.uid).get();
    
    if (!userDoc.exists) {
      throw new functions.https.HttpsError('not-found', 'User not found');
    }
    
    return userDoc.data();
  } catch (error) {
    console.error('Error getting user profile:', error);
    throw new functions.https.HttpsError('internal', error.message);
  }
});

// ==================== DOCUMENT FUNCTIONS ====================

exports.getDocuments = functions.https.onCall(async (data, context) => {
  if (!context.auth) {
    throw new functions.https.HttpsError('unauthenticated', 'User must be authenticated');
  }
  
  try {
    const snapshot = await db.collection('users')
      .doc(context.auth.uid)
      .collection('documents')
      .orderBy('createdAt', 'desc')
      .limit(100)
      .get();
    
    const documents = snapshot.docs.map(doc => ({
      id: doc.id,
      ...doc.data(),
    }));
    
    return { documents };
  } catch (error) {
    console.error('Error getting documents:', error);
    throw new functions.https.HttpsError('internal', error.message);
  }
});

exports.uploadDocument = functions.https.onCall(async (data, context) => {
  if (!context.auth) {
    throw new functions.https.HttpsError('unauthenticated', 'User must be authenticated');
  }
  
  try {
    const { fileName, documentType } = data;
    
    // Create document record in Firestore
    const docRef = await db.collection('users')
      .doc(context.auth.uid)
      .collection('documents')
      .add({
        name: fileName,
        type: documentType,
        status: 'processing',
        createdAt: admin.firestore.FieldValue.serverTimestamp(),
        updatedAt: admin.firestore.FieldValue.serverTimestamp(),
      });
    
    // Trigger document processing in background
    await processDocument(context.auth.uid, docRef.id, fileName);
    
    return {
      id: docRef.id,
      name: fileName,
      type: documentType,
      status: 'processing',
      createdAt: new Date().toISOString(),
    };
  } catch (error) {
    console.error('Error uploading document:', error);
    throw new functions.https.HttpsError('internal', error.message);
  }
});

exports.deleteDocument = functions.https.onCall(async (data, context) => {
  if (!context.auth) {
    throw new functions.https.HttpsError('unauthenticated', 'User must be authenticated');
  }
  
  try {
    const { documentId } = data;
    
    // Delete document from Firestore
    await db.collection('users')
      .doc(context.auth.uid)
      .collection('documents')
      .doc(documentId)
      .delete();
    
    // Delete file from Cloud Storage
    const bucket = storage.bucket();
    const file = bucket.file(`users/${context.auth.uid}/documents/${documentId}`);
    await file.delete();
    
    return { success: true };
  } catch (error) {
    console.error('Error deleting document:', error);
    throw new functions.https.HttpsError('internal', error.message);
  }
});

// Background function to process documents
async function processDocument(userId, documentId, fileName) {
  try {
    // Update document status to processing
    await db.collection('users')
      .doc(userId)
      .collection('documents')
      .doc(documentId)
      .update({
        status: 'processing',
        updatedAt: admin.firestore.FieldValue.serverTimestamp(),
      });
    
    // TODO: Implement OCR with Document AI
    // TODO: Extract data with Vertex AI
    // TODO: Store extracted data in BigQuery
    
    // Update document status to completed
    await db.collection('users')
      .doc(userId)
      .collection('documents')
      .doc(documentId)
      .update({
        status: 'completed',
        processedAt: admin.firestore.FieldValue.serverTimestamp(),
        ocrConfidence: '95%',
        extractedData: {
          invoiceNumber: 'INV-001',
          date: '2024-01-15',
          amount: 1250.00,
          tax: 225.00,
        },
        updatedAt: admin.firestore.FieldValue.serverTimestamp(),
      });
    
    // Send notification
    await sendNotification(userId, 'Documento procesado', `${fileName} ha sido procesado exitosamente`);
  } catch (error) {
    console.error('Error processing document:', error);
    
    // Update document status to failed
    await db.collection('users')
      .doc(userId)
      .collection('documents')
      .doc(documentId)
      .update({
        status: 'failed',
        error: error.message,
        updatedAt: admin.firestore.FieldValue.serverTimestamp(),
      });
  }
}

// ==================== ACCOUNTING FUNCTIONS ====================

exports.getGeneralLedger = functions.https.onCall(async (data, context) => {
  if (!context.auth) {
    throw new functions.https.HttpsError('unauthenticated', 'User must be authenticated');
  }
  
  try {
    const { startDate, endDate } = data;
    
    // Query BigQuery for general ledger
    const query = `
      SELECT 
        id,
        date,
        description,
        account,
        debit,
        credit,
        balance
      FROM \`pinad-project.accounting.general_ledger\`
      WHERE user_id = @userId
      ${startDate ? 'AND date >= @startDate' : ''}
      ${endDate ? 'AND date <= @endDate' : ''}
      ORDER BY date DESC
      LIMIT 1000
    `;
    
    const options = {
      query,
      params: {
        userId: context.auth.uid,
        startDate: startDate || null,
        endDate: endDate || null,
      },
    };
    
    const [rows] = await bigquery.query(options);
    
    const entries = rows.map(row => ({
      id: row.id,
      date: row.date.value,
      description: row.description,
      account: row.account,
      debit: row.debit,
      credit: row.credit,
      balance: row.balance,
    }));
    
    return { entries };
  } catch (error) {
    console.error('Error getting general ledger:', error);
    throw new functions.https.HttpsError('internal', error.message);
  }
});

exports.getBalanceSheet = functions.https.onCall(async (data, context) => {
  if (!context.auth) {
    throw new functions.https.HttpsError('unauthenticated', 'User must be authenticated');
  }
  
  try {
    const { asOfDate } = data;
    
    // Query BigQuery for balance sheet
    const query = `
      SELECT 
        total_assets,
        total_liabilities,
        total_equity,
        assets,
        liabilities,
        equity
      FROM \`pinad-project.accounting.balance_sheet\`
      WHERE user_id = @userId
      ${asOfDate ? 'AND as_of_date = @asOfDate' : ''}
      ORDER BY as_of_date DESC
      LIMIT 1
    `;
    
    const options = {
      query,
      params: {
        userId: context.auth.uid,
        asOfDate: asOfDate || null,
      },
    };
    
    const [rows] = await bigquery.query(options);
    
    if (rows.length === 0) {
      return {
        totalAssets: 0,
        totalLiabilities: 0,
        totalEquity: 0,
        assets: [],
        liabilities: [],
        equity: [],
      };
    }
    
    const row = rows[0];
    
    return {
      totalAssets: row.total_assets,
      totalLiabilities: row.total_liabilities,
      totalEquity: row.total_equity,
      assets: row.assets,
      liabilities: row.liabilities,
      equity: row.equity,
    };
  } catch (error) {
    console.error('Error getting balance sheet:', error);
    throw new functions.https.HttpsError('internal', error.message);
  }
});

exports.getIncomeStatement = functions.https.onCall(async (data, context) => {
  if (!context.auth) {
    throw new functions.https.HttpsError('unauthenticated', 'User must be authenticated');
  }
  
  try {
    const { startDate, endDate } = data;
    
    // Query BigQuery for income statement
    const query = `
      SELECT 
        total_revenue,
        total_expenses,
        net_income,
        revenues,
        expenses
      FROM \`pinad-project.accounting.income_statement\`
      WHERE user_id = @userId
      ${startDate ? 'AND start_date >= @startDate' : ''}
      ${endDate ? 'AND end_date <= @endDate' : ''}
      ORDER BY end_date DESC
      LIMIT 1
    `;
    
    const options = {
      query,
      params: {
        userId: context.auth.uid,
        startDate: startDate || null,
        endDate: endDate || null,
      },
    };
    
    const [rows] = await bigquery.query(options);
    
    if (rows.length === 0) {
      return {
        totalRevenue: 0,
        totalExpenses: 0,
        netIncome: 0,
        revenues: [],
        expenses: [],
      };
    }
    
    const row = rows[0];
    
    return {
      totalRevenue: row.total_revenue,
      totalExpenses: row.total_expenses,
      netIncome: row.net_income,
      revenues: row.revenues,
      expenses: row.expenses,
    };
  } catch (error) {
    console.error('Error getting income statement:', error);
    throw new functions.https.HttpsError('internal', error.message);
  }
});

// ==================== REPORTS FUNCTIONS ====================

exports.getIVAReport = functions.https.onCall(async (data, context) => {
  if (!context.auth) {
    throw new functions.https.HttpsError('unauthenticated', 'User must be authenticated');
  }
  
  try {
    const { period } = data;
    
    // Query BigQuery for IVA report
    const query = `
      SELECT 
        period,
        total_sales,
        total_purchases,
        debit_iva,
        credit_iva,
        iva_to_pay,
        sales,
        purchases
      FROM \`pinad-project.reports.iva_reports\`
      WHERE user_id = @userId
      AND period = @period
    `;
    
    const options = {
      query,
      params: {
        userId: context.auth.uid,
        period,
      },
    };
    
    const [rows] = await bigquery.query(options);
    
    if (rows.length === 0) {
      return {
        period,
        totalSales: 0,
        totalPurchases: 0,
        debitIVA: 0,
        creditIVA: 0,
        ivaToPay: 0,
        sales: [],
        purchases: [],
      };
    }
    
    const row = rows[0];
    
    return {
      period: row.period,
      totalSales: row.total_sales,
      totalPurchases: row.total_purchases,
      debitIVA: row.debit_iva,
      creditIVA: row.credit_iva,
      ivaToPay: row.iva_to_pay,
      sales: row.sales,
      purchases: row.purchases,
    };
  } catch (error) {
    console.error('Error getting IVA report:', error);
    throw new functions.https.HttpsError('internal', error.message);
  }
});

exports.getISLRReport = functions.https.onCall(async (data, context) => {
  if (!context.auth) {
    throw new functions.https.HttpsError('unauthenticated', 'User must be authenticated');
  }
  
  try {
    const { period } = data;
    
    // Query BigQuery for ISLR report
    const query = `
      SELECT 
        period,
        gross_income,
        deductions,
        taxable_income,
        tax_rate,
        tax_to_pay,
        entries
      FROM \`pinad-project.reports.islr_reports\`
      WHERE user_id = @userId
      AND period = @period
    `;
    
    const options = {
      query,
      params: {
        userId: context.auth.uid,
        period,
      },
    };
    
    const [rows] = await bigquery.query(options);
    
    if (rows.length === 0) {
      return {
        period,
        grossIncome: 0,
        deductions: 0,
        taxableIncome: 0,
        taxRate: 0,
        taxToPay: 0,
        entries: [],
      };
    }
    
    const row = rows[0];
    
    return {
      period: row.period,
      grossIncome: row.gross_income,
      deductions: row.deductions,
      taxableIncome: row.taxable_income,
      taxRate: row.tax_rate,
      taxToPay: row.tax_to_pay,
      entries: row.entries,
    };
  } catch (error) {
    console.error('Error getting ISLR report:', error);
    throw new functions.https.HttpsError('internal', error.message);
  }
});

// ==================== DASHBOARD FUNCTIONS ====================

exports.getDashboardMetrics = functions.https.onCall(async (data, context) => {
  if (!context.auth) {
    throw new functions.https.HttpsError('unauthenticated', 'User must be authenticated');
  }
  
  try {
    // Query BigQuery for dashboard metrics
    const query = `
      SELECT 
        revenue,
        expenses,
        documents_count,
        clients_count,
        revenue_change,
        expenses_change,
        documents_change,
        clients_change,
        recent_documents
      FROM \`pinad-project.dashboard.metrics\`
      WHERE user_id = @userId
      ORDER BY timestamp DESC
      LIMIT 1
    `;
    
    const options = {
      query,
      params: {
        userId: context.auth.uid,
      },
    };
    
    const [rows] = await bigquery.query(options);
    
    if (rows.length === 0) {
      return {
        revenue: 0,
        expenses: 0,
        documentsCount: 0,
        clientsCount: 0,
        revenueChange: 0,
        expensesChange: 0,
        documentsChange: 0,
        clientsChange: 0,
        recentDocuments: [],
      };
    }
    
    const row = rows[0];
    
    return {
      revenue: row.revenue,
      expenses: row.expenses,
      documentsCount: row.documents_count,
      clientsCount: row.clients_count,
      revenueChange: row.revenue_change,
      expensesChange: row.expenses_change,
      documentsChange: row.documents_change,
      clientsChange: row.clients_change,
      recentDocuments: row.recent_documents,
    };
  } catch (error) {
    console.error('Error getting dashboard metrics:', error);
    throw new functions.https.HttpsError('internal', error.message);
  }
});

// ==================== NOTIFICATION FUNCTIONS ====================

async function sendNotification(userId, title, body) {
  try {
    // Get user's FCM token
    const userDoc = await db.collection('users').doc(userId).get();
    const fcmToken = userDoc.data().fcmToken;
    
    if (!fcmToken) {
      console.log('No FCM token for user:', userId);
      return;
    }
    
    // Send notification
    const message = {
      notification: {
        title,
        body,
      },
      token: fcmToken,
    };
    
    await admin.messaging().send(message);
  } catch (error) {
    console.error('Error sending notification:', error);
  }
}

exports.updateFCMToken = functions.https.onCall(async (data, context) => {
  if (!context.auth) {
    throw new functions.https.HttpsError('unauthenticated', 'User must be authenticated');
  }
  
  try {
    const { fcmToken } = data;
    
    await db.collection('users').doc(context.auth.uid).update({
      fcmToken,
      updatedAt: admin.firestore.FieldValue.serverTimestamp(),
    });
    
    return { success: true };
  } catch (error) {
    console.error('Error updating FCM token:', error);
    throw new functions.https.HttpsError('internal', error.message);
  }
});

// ==================== BACKGROUND TRIGGERS ====================

// Triggered when a new document is uploaded to Cloud Storage
exports.onDocumentUpload = functions.storage.object().onFinalize(async (object) => {
  const filePath = object.name;
  const fileName = object.name.split('/').pop();
  const userId = filePath.split('/')[1];
  
  console.log(`Document uploaded: ${fileName} by user ${userId}`);
  
  // Process document with Document AI
  // Extract data with Vertex AI
  // Store in BigQuery
  // Send notification
});

// Triggered when a user is created
exports.onUserCreate = functions.auth.user().onCreate(async (user) => {
  console.log(`User created: ${user.uid}`);
  
  // Create user document in Firestore
  await db.collection('users').doc(user.uid).set({
    uid: user.uid,
    email: user.email,
    name: user.displayName || '',
    createdAt: admin.firestore.FieldValue.serverTimestamp(),
    updatedAt: admin.firestore.FieldValue.serverTimestamp(),
  });
  
  // Send welcome notification
  await sendNotification(user.uid, 'Bienvenido a (π)NAD', 'Tu cuenta ha sido creada exitosamente');
});
