/**
 * JS Tree Select
 * A custom select utility / component using JsTree
 */

import { Popover } from "./popover.js";

export class JSTreeSelect {
    constructor( { element, triggerElement, treeJsonSrcUrl } = {} ) {
        this.element = element;
        this.srcUrl = treeJsonSrcUrl;

        this._discriminator = crypto.randomUUID();

        this._popover = new Popover({
            triggerElement: triggerElement ? triggerElement : null,
            wrapperElement: this.element
        });

        this._render();
    }

    /**
     * Render the JsTreeSelect
     */
    _render() {
        // this.element.empty();

        let contentElement = this.element.querySelector(".popover_content");
        
        let treeElement = document.createElement("div");
        contentElement.prepend(treeElement);

        this._loadTreeJson()
            .then(treeValidObj => {
                $(treeElement).jstree({
                    'plugins': [ 'checkbox', ], 
                    'core': {
                        'data': treeValidObj
                    }
                })
            });
    }

    /**
     * Get the JsTree tree object from the defined srcUrl
     * The srcUrl endpoint should be able to provide Json in a structure
     * that is acceptable to JsTree.
     * @returns An object
     */
    async _loadTreeJson() {
        return fetch(this.srcUrl, {
            method: 'GET'
        }).then(response => response.json())
    }
}