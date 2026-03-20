(function initMedRoundTableApiConfig(window) {
    const REMOTE_API_BASE = 'https://medroundtable-api.onrender.com';
    const LOCAL_HOSTS = new Set(['localhost', '127.0.0.1']);
    const STATIC_HOST_SUFFIXES = ['.github.io'];
    const STATIC_HOSTS = new Set(['mokangmedical.github.io']);
    const MODE_STORAGE_KEY = 'mrt_backend_mode';

    function consumeModeOverride() {
        try {
            const url = new URL(window.location.href);
            const override = url.searchParams.get('mrt_backend_mode');
            if (!override) {
                return;
            }
            if (override === 'auto') {
                window.localStorage.removeItem(MODE_STORAGE_KEY);
            } else if (override === 'static' || override === 'server') {
                window.localStorage.setItem(MODE_STORAGE_KEY, override);
            }
            url.searchParams.delete('mrt_backend_mode');
            window.history.replaceState({}, '', url.toString());
        } catch (error) {
            console.warn('Failed to consume backend mode override:', error);
        }
    }

    function getStoredModeOverride() {
        try {
            return window.localStorage.getItem(MODE_STORAGE_KEY);
        } catch (error) {
            console.warn('Failed to read backend mode override:', error);
            return null;
        }
    }

    function shouldDefaultToStaticMode() {
        const host = window.location.hostname;
        if (STATIC_HOSTS.has(host)) {
            return true;
        }
        return STATIC_HOST_SUFFIXES.some((suffix) => host.endsWith(suffix));
    }

    function isStaticMode() {
        const override = getStoredModeOverride();
        if (override === 'static') {
            return true;
        }
        if (override === 'server') {
            return false;
        }
        if (LOCAL_HOSTS.has(window.location.hostname)) {
            return false;
        }
        return shouldDefaultToStaticMode();
    }

    function getApiBase() {
        return LOCAL_HOSTS.has(window.location.hostname)
            ? 'http://localhost:8000'
            : REMOTE_API_BASE;
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

    function buildStaticModeError() {
        return new Error('当前站点运行在 GitHub Pages 静态工作台模式，未连接共享后端');
    }

    async function fetchJson(path, options) {
        if (isStaticMode()) {
            throw buildStaticModeError();
        }
        const response = await fetch(apiUrl(path), options);
        const payload = await parseResponseBody(response);
        if (!response.ok) {
            throw new Error(extractErrorMessage(payload, response));
        }
        return payload;
    }

    async function healthcheck() {
        if (isStaticMode()) {
            throw buildStaticModeError();
        }
        const response = await fetch(apiUrl('/health'));
        if (!response.ok) {
            throw new Error(`后端不可用 (${response.status})`);
        }
        return response.json();
    }

    consumeModeOverride();

    window.MRTApiConfig = {
        get API_BASE() {
            return getApiBase();
        },
        get MODE() {
            return isStaticMode() ? 'static' : 'server';
        },
        get isStaticMode() {
            return isStaticMode();
        },
        get STATIC_MODE_MESSAGE() {
            return '当前站点运行在 GitHub Pages 静态工作台模式，所有材料先保存在当前浏览器。';
        },
        apiUrl,
        fetchJson,
        parseResponseBody,
        healthcheck,
    };
})(window);
