let DataStore = (function () {
    const readFromSessionStorage = (key) => {
        return JSON.parse(sessionStorage.getItem(key));
    }

    const saveToSessionStorage = (key, data) => {
        sessionStorage.setItem(key, JSON.stringify(data));
    }

    const getDisplayLayouts = async () => {
        let displayLayouts = readFromSessionStorage('displayLayouts');
        if (displayLayouts && displayLayouts.timestamp > Date.now() - 1000 * 60 * 60 * 24) {
            return displayLayouts;
        }
    
        fetch("/screenshow/layout/list/json", {
            method: "GET",
            headers: {
                "Content-Type": "application/json"
            }
        }).then(function (response) {
            return response.json();
        }).then(function (data) {
            saveToSessionStorage('displayLayouts', {
                data,
                timestamp: Date.now()
            });
            return data;
        });
    }


    return {
        getDisplayLayouts: getDisplayLayouts,
    }
})();