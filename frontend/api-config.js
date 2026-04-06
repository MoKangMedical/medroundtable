(function initMedRoundTableApiConfig(window) {
    const LOCAL_HOSTS = new Set(['localhost', '127.0.0.1']);
    const SAME_ORIGIN_HOSTS = new Set([
        'medroundtable-v2.vercel.app',
        'medroundtable.cn',
        'www.medroundtable.cn',
    ]);
    const PUBLIC_API_ORIGIN = 'https://medroundtable-v2.vercel.app';

    function getApiBase() {
        const hostname = window.location.hostname;
        if (LOCAL_HOSTS.has(hostname)) {
            return 'http://localhost:8000';
        }

        if (SAME_ORIGIN_HOSTS.has(hostname)) {
            return window.location.origin;
        }

        return PUBLIC_API_ORIGIN;
    }

    function apiUrl(path) {
        if (!path) {
            return getApiBase();
        }
        if (/^https?:\/\//.test(path)) {
            return path;
        }
        return `${getApiBase()}${path.startsWith('/') ? path : `/${path}`}`;
    }

    async function parseResponseBody(response) {
        const contentType = response.headers.get('content-type') || '';
        if (contentType.includes('application/json')) {
            return response.json();
        }

        const text = await response.text();
        if (!text) {
            return null;
        }

        try {
            return JSON.parse(text);
        } catch (err) {
            return { detail: text };
        }
    }

    function extractErrorMessage(payload, response) {
        if (payload && typeof payload === 'object') {
            if (typeof payload.detail === 'string') {
                return payload.detail;
            }
            if (Array.isArray(payload.detail)) {
                return payload.detail.map((item) => item.msg || String(item)).join('；');
            }
            if (typeof payload.message === 'string') {
                return payload.message;
            }
        }

        return `请求失败 (${response.status})`;
    }

    async function fetchJson(path, options) {
        const response = await fetch(apiUrl(path), options);
        const payload = await parseResponseBody(response);
        if (!response.ok) {
            throw new Error(extractErrorMessage(payload, response));
        }
        return payload;
    }

    async function healthcheck() {
        const response = await fetch(apiUrl('/api/health'));
        if (!response.ok) {
            throw new Error(`后端不可用 (${response.status})`);
        }
        return response.json();
    }

    window.MRTApiConfig = {
        get API_BASE() {
            return getApiBase();
        },
        apiUrl,
        fetchJson,
        parseResponseBody,
        healthcheck,
    };
})(window);
