(function () {
    const STORAGE_KEY = 'mrt_secondme_identity';
    const PARAM_KEYS = ['sm_id', 'sm_name', 'sm_email', 'sm_avatar'];

    function clone(value) {
        return value ? JSON.parse(JSON.stringify(value)) : null;
    }

    function sanitize(value) {
        return typeof value === 'string' ? value.trim() : '';
    }

    function persistIdentity(identity) {
        if (!identity || !sanitize(identity.name)) {
            return null;
        }
        const payload = {
            id: sanitize(identity.id),
            name: sanitize(identity.name),
            email: sanitize(identity.email),
            avatar: sanitize(identity.avatar),
            provider: 'secondme'
        };
        localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
        return payload;
    }

    function loadIdentity() {
        try {
            const raw = localStorage.getItem(STORAGE_KEY);
            return raw ? JSON.parse(raw) : null;
        } catch (err) {
            console.error('SecondMe identity parse failed:', err);
            return null;
        }
    }

    function clearIdentity() {
        localStorage.removeItem(STORAGE_KEY);
    }

    function consumeIdentityFromLocation(currentWindow = window) {
        try {
            const url = new URL(currentWindow.location.href);
            const identity = {
                id: sanitize(url.searchParams.get('sm_id')),
                name: sanitize(url.searchParams.get('sm_name')),
                email: sanitize(url.searchParams.get('sm_email')),
                avatar: sanitize(url.searchParams.get('sm_avatar'))
            };

            if (!identity.name) {
                return loadIdentity();
            }

            const stored = persistIdentity(identity);
            PARAM_KEYS.forEach((key) => url.searchParams.delete(key));
            currentWindow.history.replaceState({}, '', url.toString());
            return stored;
        } catch (err) {
            console.error('SecondMe identity consume failed:', err);
            return loadIdentity();
        }
    }

    window.MedRoundTableSecondMeIdentity = {
        storageKey: STORAGE_KEY,
        loadIdentity,
        persistIdentity,
        clearIdentity,
        consumeIdentityFromLocation,
        clone
    };
})();
