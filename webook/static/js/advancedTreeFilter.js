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
        } = {} ) 
        { 
            super({
                triggerElement: triggerElement,
                wrapperElement: wrapperElement,
            });

            this.title = title;
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

            let treeHolder = document.createElement("div");
            popoverContentEl.appendChild(treeHolder);
            this._jsTreeElement = treeHolder;

            let submitBtnElement = document.createElement("button");
            submitBtnElement.classList.add("btn", "wb-btn-secondary", "mt-2");
            submitBtnElement.innerText = "Filtrer med gjeldende valg";
            submitBtnElement.onclick = (event) => {
                this._selectedMap.clear();
                const selectedNodes = $(this._jsTreeElement).jstree("get_selected", true);
                const undeterminedNodes = $(this._jsTreeElement).jstree("get_undetermined", true);

                this._onSubmit(selectedNodes, undeterminedNodes);
            }
            popoverContentEl.appendChild(submitBtnElement)

            this._loadTreeJson()
                .then(treeValidObj => {
                    this._jsTree = $(treeHolder).jstree({
                        'checkbox': getCascadeSettingsFromCascadeBehaviour(this.cascadeBehaviour),
                        'plugins': [ 'checkbox', ], 
                        'core': {
                            "themes" : { "icons": false },
                            'data': treeValidObj,
                            'multiple': true,
                        }
                    });
                });
        }
}