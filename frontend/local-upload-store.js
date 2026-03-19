(function initMedRoundTableLocalUploadStore(window) {
    const DB_NAME = 'medroundtable-local-uploads';
    const DB_VERSION = 1;
    const STORE_NAME = 'records';

    let dbPromise = null;

    function createId() {
        if (window.crypto && typeof window.crypto.randomUUID === 'function') {
            return window.crypto.randomUUID();
        }
        return `local_${Date.now()}_${Math.random().toString(16).slice(2)}`;
    }

    function formatBytes(bytes) {
        if (!bytes) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.min(sizes.length - 1, Math.floor(Math.log(bytes) / Math.log(k)));
        return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
    }

    function openDatabase() {
        if (dbPromise) {
            return dbPromise;
        }

        dbPromise = new Promise((resolve, reject) => {
            if (!window.indexedDB) {
                reject(new Error('当前浏览器不支持 IndexedDB，本地暂存不可用'));
                return;
            }

            const request = window.indexedDB.open(DB_NAME, DB_VERSION);

            request.onupgradeneeded = () => {
                const db = request.result;
                if (!db.objectStoreNames.contains(STORE_NAME)) {
                    const store = db.createObjectStore(STORE_NAME, { keyPath: 'id' });
                    store.createIndex('kind', 'kind', { unique: false });
                    store.createIndex('createdAt', 'createdAt', { unique: false });
                }
            };

            request.onsuccess = () => {
                const db = request.result;
                db.onversionchange = () => db.close();
                resolve(db);
            };

            request.onerror = () => {
                reject(request.error || new Error('打开本地暂存数据库失败'));
            };
        });

        return dbPromise;
    }

    async function withStore(mode, handler) {
        const db = await openDatabase();
        return new Promise((resolve, reject) => {
            const transaction = db.transaction(STORE_NAME, mode);
            const store = transaction.objectStore(STORE_NAME);
            const result = handler(store, transaction);

            transaction.oncomplete = () => resolve(result);
            transaction.onerror = () => reject(transaction.error || new Error('本地暂存操作失败'));
            transaction.onabort = () => reject(transaction.error || new Error('本地暂存操作中止'));
        });
    }

    async function saveRecord(payload) {
        const {
            kind,
            title,
            description = '',
            roundtableId = '',
            protocolId = '',
            file,
            meta = {},
        } = payload || {};

        if (!kind) {
            throw new Error('缺少暂存类型');
        }
        if (!file) {
            throw new Error('缺少文件');
        }

        const record = {
            id: createId(),
            kind,
            title: title || file.name,
            description,
            roundtableId,
            protocolId,
            fileName: file.name,
            fileSize: file.size,
            fileType: file.type || 'application/octet-stream',
            source: 'browser-local',
            meta,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            fileBlob: file.slice(0, file.size, file.type || 'application/octet-stream'),
        };

        await withStore('readwrite', (store) => store.put(record));
        return record;
    }

    async function listRecords(kind) {
        const rows = await withStore('readonly', (store) => {
            return new Promise((resolve, reject) => {
                const request = store.getAll();
                request.onsuccess = () => resolve(request.result || []);
                request.onerror = () => reject(request.error || new Error('读取本地暂存记录失败'));
            });
        });

        return rows
            .filter((record) => !kind || record.kind === kind)
            .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
    }

    async function getRecord(id) {
        if (!id) return null;
        return withStore('readonly', (store) => {
            return new Promise((resolve, reject) => {
                const request = store.get(id);
                request.onsuccess = () => resolve(request.result || null);
                request.onerror = () => reject(request.error || new Error('读取本地暂存详情失败'));
            });
        });
    }

    async function deleteRecord(id) {
        if (!id) return;
        await withStore('readwrite', (store) => store.delete(id));
    }

    async function clearRecords(kind) {
        const rows = await listRecords(kind);
        await Promise.all(rows.map((record) => deleteRecord(record.id)));
    }

    async function downloadRecord(id) {
        const record = await getRecord(id);
        if (!record || !record.fileBlob) {
            throw new Error('未找到可下载的本地暂存文件');
        }

        const blob = record.fileBlob instanceof Blob
            ? record.fileBlob
            : new Blob([record.fileBlob], { type: record.fileType || 'application/octet-stream' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = record.fileName || record.title || 'medroundtable-file';
        document.body.appendChild(link);
        link.click();
        link.remove();
        setTimeout(() => URL.revokeObjectURL(url), 1000);
    }

    async function summarize(kind) {
        const rows = await listRecords(kind);
        return {
            count: rows.length,
            totalSize: rows.reduce((sum, record) => sum + Number(record.fileSize || 0), 0),
            rows,
        };
    }

    window.MRTLocalUploadStore = {
        saveRecord,
        listRecords,
        getRecord,
        deleteRecord,
        clearRecords,
        downloadRecord,
        summarize,
        formatBytes,
    };
})(window);
