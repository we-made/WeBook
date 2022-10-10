import { Popover } from "./popover.js";

export const NORMAL_CASCADE_BEHAVIOUR = Symbol("NormalCascadeBehaviour")
export const PARENT_INDEPENDENT_CASCADE_BEHAVIOUR = Symbol("ParentIndependentCascadeBehaviour")

function getCascadeSettingsFromCascadeBehaviour(cascadeBehaviour) {
    switch(cascadeBehaviour) {
        case NORMAL_CASCADE_BEHAVIOUR:
            return { };
        case PARENT_INDEPENDENT_CASCADE_BEHAVIOUR:
            return { 
                "three_state": false,
                "cascade": "up+undetermined",
            };
        default:
            throw Error("No such cascade behaviour known!");
    }
}

export class AdvancedTreeFilter extends Popover {
    constructor ( { 
        title,
        triggerElement, 
        wrapperElement, 
        data,
        selectionPresets,
        onSelectionUpdate,
        onSubmit,
        treeSrcUrl,
        cascadeBehaviour=NORMAL_CASCADE_BEHAVIOUR,
        isSearchable=false,
        } = {} ) 
        { 
            super({
                triggerElement: triggerElement,
                wrapperElement: wrapperElement,
            });

            this.title = title;
            this.isSearchable = isSearchable;
            this.cascadeBehaviour = cascadeBehaviour;

            this._instanceDiscriminator = crypto.randomUUID();

            this.treeSrcUrl = treeSrcUrl;

            this._selectionPresets = selectionPresets;
            this._data = data;
            this._onSubmit = onSubmit;
            
            this.isRendered = false;

            this.onSelectionUpdate = onSelectionUpdate;

            this._selectedMap = new Map();
            this._categorySearchMap = new Map();

            this._render();
        }

        async _loadTreeJson() {
            return fetch(this.treeSrcUrl, {
                method: 'GET'
            }).then(response => response.json())
        }

        getSelectedValues() {
            return Array.from(this._selectedMap.keys());
        }

        _search(term) {
            $(this._jsTreeElement).jstree("search", term, false, true);
        }

        _render() {
            this.wrapperElement.innerHTML = "";
            if (!this.wrapperElement.classList.contains("popover_wrapper")) {
                this.wrapperElement.classList.add("popover_wrapper");
            }

            let popoverContentEl = document.createElement("div");
            popoverContentEl.classList.add("popover_content", this._instanceDiscriminator);
            this.wrapperElement.appendChild(popoverContentEl);

            let titleEl = document.createElement("h4");
            titleEl.innerText = this.title;
            popoverContentEl.appendChild(titleEl);

            if (this.isSearchable) {
                let searchInput = document.createElement("input");
                searchInput.setAttribute("type", "search");
                searchInput.setAttribute("placeholder", "Søk...");
                searchInput.classList.add("form-control", "mb-1");
                
                searchInput.addEventListener("input", (event) => { 
                    this._search( event.target.value );
                })

                popoverContentEl.appendChild(searchInput);
            }

            let submitBtnElement = document.createElement("button");
            submitBtnElement.classList.add("btn", "wb-btn-secondary", "mt-1", "mb-1");
            submitBtnElement.innerHTML = "<i class='fas fa-filter'></i>&nbsp; Filtrer med gjeldende valg";
            submitBtnElement.onclick = (event) => {
                this._selectedMap.clear();
                const selectedNodes = $(this._jsTreeElement).jstree("get_selected", true);
                const undeterminedNodes = $(this._jsTreeElement).jstree("get_undetermined", true);

                this._onSubmit(selectedNodes, undeterminedNodes);
            }
            popoverContentEl.appendChild(submitBtnElement)

            let treeHolder = document.createElement("div");
            popoverContentEl.appendChild(treeHolder);
            this._jsTreeElement = treeHolder;

            this._loadTreeJson()
                .then(treeValidObj => {
                    this._jsTree = $(treeHolder).jstree({
                        'checkbox': getCascadeSettingsFromCascadeBehaviour(this.cascadeBehaviour),
                        'plugins': [ 'checkbox', 'search' ], 
                        'core': {
                            "themes" : { "icons": false },
                            'data': treeValidObj,
                            'multiple': true,
                        }
                    });
                });
        }
}