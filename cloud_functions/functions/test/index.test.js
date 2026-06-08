const assert = require('assert');
const functions = require('firebase-functions');
const admin = require('firebase-admin');
const { getTestFunctions } = require('firebase-functions-test');

const test = getTestFunctions();

describe('Cloud Functions Integration Tests', () => {
  let wrappedFunctions;

  beforeAll(() => {
    // Initialize Firebase Admin SDK for testing
    admin.initializeApp({
      credential: admin.credential.applicationDefault(),
      projectId: 'pinad-project',
    });

    // Get wrapped functions for testing
    wrappedFunctions = {
      createUser: test.wrap(require('../index').createUser),
      getUserProfile: test.wrap(require('../index').getUserProfile),
      getDocuments: test.wrap(require('../index').getDocuments),
      uploadDocument: test.wrap(require('../index').uploadDocument),
      deleteDocument: test.wrap(require('../index').deleteDocument),
      getGeneralLedger: test.wrap(require('../index').getGeneralLedger),
      getBalanceSheet: test.wrap(require('../index').getBalanceSheet),
      getIncomeStatement: test.wrap(require('../index').getIncomeStatement),
      getIVAReport: test.wrap(require('../index').getIVAReport),
      getISLRReport: test.wrap(require('../index').getISLRReport),
      getDashboardMetrics: test.wrap(require('../index').getDashboardMetrics),
      updateFCMToken: test.wrap(require('../index').updateFCMToken),
    };
  });

  afterAll(() => {
    test.cleanup();
  });

  describe('Authentication Functions', () => {
    test('createUser should create a new user', async () => {
      const data = {
        email: 'test@example.com',
        password: 'password123',
        name: 'Test User',
      };

      const context = {
        auth: {
          uid: 'test-uid',
        },
      };

      const result = await wrappedFunctions.createUser(data, context);
      
      assert.strictEqual(result.success, true);
      assert.ok(result.uid);
    });

    test('getUserProfile should return user profile', async () => {
      const context = {
        auth: {
          uid: 'test-uid',
        },
      };

      const result = await wrappedFunctions.getUserProfile({}, context);
      
      assert.ok(result);
      assert.strictEqual(result.uid, 'test-uid');
    });

    test('getUserProfile should throw error if not authenticated', async () => {
      const context = {};

      await assert.rejects(
        async () => await wrappedFunctions.getUserProfile({}, context),
        /User must be authenticated/
      );
    });
  });

  describe('Document Functions', () => {
    test('getDocuments should return user documents', async () => {
      const context = {
        auth: {
          uid: 'test-uid',
        },
      };

      const result = await wrappedFunctions.getDocuments({}, context);
      
      assert.ok(result.documents);
      assert.ok(Array.isArray(result.documents));
    });

    test('uploadDocument should upload a document', async () => {
      const data = {
        fileName: 'document.pdf',
        documentType: 'Factura',
      };

      const context = {
        auth: {
          uid: 'test-uid',
        },
      };

      const result = await wrappedFunctions.uploadDocument(data, context);
      
      assert.ok(result.id);
      assert.strictEqual(result.name, 'document.pdf');
      assert.strictEqual(result.type, 'Factura');
      assert.strictEqual(result.status, 'processing');
    });

    test('deleteDocument should delete a document', async () => {
      const data = {
        documentId: 'doc123',
      };

      const context = {
        auth: {
          uid: 'test-uid',
        },
      };

      const result = await wrappedFunctions.deleteDocument(data, context);
      
      assert.strictEqual(result.success, true);
    });
  });

  describe('Accounting Functions', () => {
    test('getGeneralLedger should return ledger entries', async () => {
      const data = {
        startDate: '2024-01-01',
        endDate: '2024-12-31',
      };

      const context = {
        auth: {
          uid: 'test-uid',
        },
      };

      const result = await wrappedFunctions.getGeneralLedger(data, context);
      
      assert.ok(result.entries);
      assert.ok(Array.isArray(result.entries));
    });

    test('getBalanceSheet should return balance sheet data', async () => {
      const data = {
        asOfDate: '2024-12-31',
      };

      const context = {
        auth: {
          uid: 'test-uid',
        },
      };

      const result = await wrappedFunctions.getBalanceSheet(data, context);
      
      assert.ok(result.totalAssets);
      assert.ok(result.totalLiabilities);
      assert.ok(result.totalEquity);
    });

    test('getIncomeStatement should return income statement data', async () => {
      const data = {
        startDate: '2024-01-01',
        endDate: '2024-12-31',
      };

      const context = {
        auth: {
          uid: 'test-uid',
        },
      };

      const result = await wrappedFunctions.getIncomeStatement(data, context);
      
      assert.ok(result.totalRevenue);
      assert.ok(result.totalExpenses);
      assert.ok(result.netIncome);
    });
  });

  describe('Reports Functions', () => {
    test('getIVAReport should return IVA report', async () => {
      const data = {
        period: '2024-01',
      };

      const context = {
        auth: {
          uid: 'test-uid',
        },
      };

      const result = await wrappedFunctions.getIVAReport(data, context);
      
      assert.strictEqual(result.period, '2024-01');
      assert.ok(result.totalSales);
      assert.ok(result.totalPurchases);
      assert.ok(result.debitIVA);
      assert.ok(result.creditIVA);
      assert.ok(result.ivaToPay);
    });

    test('getISLRReport should return ISLR report', async () => {
      const data = {
        period: '2024',
      };

      const context = {
        auth: {
          uid: 'test-uid',
        },
      };

      const result = await wrappedFunctions.getISLRReport(data, context);
      
      assert.strictEqual(result.period, '2024');
      assert.ok(result.grossIncome);
      assert.ok(result.deductions);
      assert.ok(result.taxableIncome);
      assert.ok(result.taxRate);
      assert.ok(result.taxToPay);
    });
  });

  describe('Dashboard Functions', () => {
    test('getDashboardMetrics should return dashboard metrics', async () => {
      const context = {
        auth: {
          uid: 'test-uid',
        },
      };

      const result = await wrappedFunctions.getDashboardMetrics({}, context);
      
      assert.ok(result.revenue);
      assert.ok(result.expenses);
      assert.ok(result.documentsCount);
      assert.ok(result.clientsCount);
    });
  });

  describe('Notification Functions', () => {
    test('updateFCMToken should update FCM token', async () => {
      const data = {
        fcmToken: 'test-fcm-token',
      };

      const context = {
        auth: {
          uid: 'test-uid',
        },
      };

      const result = await wrappedFunctions.updateFCMToken(data, context);
      
      assert.strictEqual(result.success, true);
    });
  });
});
