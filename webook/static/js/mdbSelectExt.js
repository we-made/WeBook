class ExtendedSelect {
    /* 
        jqElement: JQuery element of the select
        getUrl: API url to query.
        initialSearchValue: initial value to search (default empty, will get all items). Only interesting on the first load.
        extraParams: object with extra parameters to add to the request body. Default empty.
        dataParser: parser function to parse items received from querying the api to html options. Default looks for object.key and object.value.
        searchThreshold: how many characters must be "present" before we start querying the API. Default 3.
    */
    constructor ( { 
        jqElement, 
        getUrl, 
        initialSearchValue="", 
        extraParams=undefined, 
        extraHeaders=undefined,
        dataParser=undefined,
        searchThreshold=3 } = {} ) {

        this.jqElement = jqElement;
        this.getUrl = getUrl;
        this.extraParams = extraParams;
        this.searchThreshold = searchThreshold;
        this.extraHeaders = extraHeaders;
        this.dataParser = (dataParser === undefined ? this.defaultItemParser : dataParser)

        this.jqElement[0].addEventListener('open.mdb.select', (e) => {
            this.bindToSearch();
        });

        this.search(initialSearchValue);    // initialize the select, as to populate data
    }

    /* default for parsing from a fetched item into a html option element */
    defaultItemParser(item) {
        return {
            value: item.id,
            text: item.text,
            secondary_text: "",
        };
    }

    isValid() {
        return this.jqElement[0].dataset.mdbFilter === "true";
    }

    /* 
        Bind an event listener to the selects search input.
    */
    async bindToSearch () {
        let ext = this;
        var observer = new MutationObserver(function (mutations, me) {
            var filterField = document.getElementsByClassName('select-filter-input')[0];
            var delayTimer;
            if (filterField) {
                filterField.addEventListener("input", function () {
                    let searchValue = $(filterField).val();
                    if (ext.searchThreshold <= searchValue.length || searchValue === "") {
                        clearTimeout(delayTimer);
                        delayTimer=setTimeout(function () {
                            ext.search({ term: searchValue });
                        }, 300)   
                    }
                });

                me.disconnect();
                return;
            }
        })

        observer.observe(document, {
            childList: true,
            subtree: true
        })
    }

    /* 
        Query
    */
    async search( { term } = {} ) {

        let data = {}
        if (term === undefined) {
            term = "";
        }
        if (this.extraParams !== undefined) {
            data = this.extraParams;
        }
        data.term = term;

        let headers = {}
        if (this.extraHeaders !== undefined) {
            headers = this.extraHeaders;
        }
        headers["Content-Type"] = "application/json";

        const response = await fetch(this.getUrl, {
            method: 'POST',
            headers,
            credentials: "same-origin",
            body: JSON.stringify(data)
        });

        let respJson = await response.json();
        let parsedEntities = JSON.parse(respJson);

        let options = this.jqElement[0].querySelectorAll("option");
        for (let i = 0; i < options.length; i++) {
            options[i].remove();
        }

        for (let i = 0; i < parsedEntities.length; i++) {
            let item = this.dataParser(parsedEntities[i]);

            let parentEl = this.jqElement;
            
            let isOptgroup = item.options !== undefined && Array.isArray(item.options);
            
            if (isOptgroup) {
                parentEl = document.createElement('optgroup');
                parentEl.setAttribute('label', item.label);
                this.jqElement.append(parentEl);
            }


            let secondary = (item.secondary_text !== undefined && item.secondary_text !== "" ? "data-mdb-secondary-text='" + item.secondary_text + "'" : "")
            parentEl.append("<option value='" + item.value + "'" + secondary + ">" + item.text + "</option>");
        }
        
        return respJson;
    }
}