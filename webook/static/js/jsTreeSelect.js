/**
 * JS Tree Select
 * A custom select utility / component using JsTree
 */

import { Popover } from "./popover.js";

export class JSTreeSelect {
    constructor( { 
        element, 
        treeJsonSrcUrl,
        initialSelected=null,
        allowMultipleSelect=false,
        noneSelectedLabelText="None selected",
        valueSelectedLabelText=undefined,
        selectFirstTimeButtonText="Select",
        changeSelectedValueButtonText="Change",
        popoverSaveChoicesButtonText="Save choices",
        invalidFeedbackText="Please select an item"} = {} ) {

        this.element = element;
        this.srcUrl = treeJsonSrcUrl;
        this.allowMultipleSelect = allowMultipleSelect;

        this.selected = initialSelected;

        this.invalidFeedbackText = invalidFeedbackText;

        this.noneSelectedLabelText = noneSelectedLabelText;
        this.valueSelectedLabelText = valueSelectedLabelText === undefined ? this._standardValueSelectedLabelText : valueSelectedLabelText;
        this.popoverSaveChoicesButtonText = popoverSaveChoicesButtonText;
        this.selectFirstTimeButtonText = selectFirstTimeButtonText;
        this.changeSelectedValueButtonText = changeSelectedValueButtonText;

        this._popover = null;
        this._jsTree = null;

        this._render();
    }

    _standardValueSelectedLabelText(selected) {
        return selected.text;
    }

    _setSelectedValue(id, text) {
        this.selected = { id: id, text: text };
        this._labelElement.innerHTML = this._generateLabelElement().innerHTML;
        this._hideInvalidFeedback();
    }

    getSelectedValue() {
        if (!this._hasSelectedValue())
            throw Error("No value selected");
        
        return this.selected.id;
    }

    isValid()  {
        return this._hasSelectedValue();
    }

    showInvalidFeedback() {
        let invalidText = document.createElement("span");
        invalidText.classList.add("text-danger");
        invalidText.innerText = this.invalidFeedbackText;
        this._activeInvalidTextElement = invalidText;
        this.element.append(invalidText);
    }

    _hideInvalidFeedback() {
        if (this._activeInvalidTextElement !== undefined){
            this._activeInvalidTextElement.remove();
            this._activeInvalidTextElement = undefined;
        }
    }
 
    /**
     * Check if a value has been selected, and if so return true, otherwise false.
     * @returns a boolean value indicating if a value has been selected or not
     */
    _hasSelectedValue() { 
        return this.selected !== undefined && this.selected !== null;
    }

    /**
     * Generate the label element, which contains text indicating the status of the component and value selection.
     * @returns a html element, the label
     */
    _generateLabelElement() {
        let labelElement = document.createElement('span');
        
        if (this._hasSelectedValue())
            labelElement.innerHTML = typeof this.valueSelectedLabelText === "function" ? this.valueSelectedLabelText( this.selected ) : this.valueSelectedLabelText;
        else
            labelElement.innerHTML = typeof this.noneSelectedLabelText === "function" ? this.noneSelectedLabelText() : this.noneSelectedLabelText;

        return labelElement;
    }

    /**
     * Generate a HTML element containing the trigger for the popover containing the JS Tree, and a button for triggering the
     * said popover to show. As a side effect this function will also  set the variable _popover on the instance to the popover instance
     * that it creates in tandem with its generated elements.
     */
    _generateJsTreeTriggerElement() {
        let wrapper = document.createElement("div");

        let buttonElement = document.createElement("button");
        buttonElement.setAttribute("type", "button");
        buttonElement.innerText = this._hasSelectedValue ? this.selectFirstTimeButtonText : this.changeSelectedValueButtonText;
        buttonElement.classList.add("btn", "wb-btn-secondary");
        wrapper.appendChild(buttonElement);

        let popoverWrapper = document.createElement("div");
        popoverWrapper.classList.add("popover_wrapper");
        wrapper.appendChild(popoverWrapper);

        let popoverContent = document.createElement("span");
        popoverContent.classList.add("popover_content");
        popoverWrapper.appendChild(popoverContent);

        let treeElement = document.createElement("div");
        popoverContent.appendChild(treeElement);

        let submitButtonInsidePopoverElement = document.createElement("button");
        submitButtonInsidePopoverElement.setAttribute("type", "button");
        submitButtonInsidePopoverElement.innerText = this.popoverSaveChoicesButtonText;
        submitButtonInsidePopoverElement.classList.add("btn", "wb-btn-secondary", "float-end", "mt-2");
        submitButtonInsidePopoverElement.onclick = () => { 
            const id = $(this._jsTreeElement).jstree("get_selected")[0];
            const text = $(this._jsTreeElement).jstree("get_selected", true)[0].text;
            
            console.log(id, text)

            this._setSelectedValue(id, text);

            this._popover.show(); //hide --toggle
        };
        popoverContent.appendChild(submitButtonInsidePopoverElement);
        
        this._jsTreeElement = treeElement;

        this._loadTreeJson()
            .then(treeValidObj => {
                this._jsTree = $(treeElement).jstree({
                    'checkbox': {
                        "three_state": false,
                    },
                    'plugins': [ 'checkbox', ], 
                    'core': {
                        'data': treeValidObj,
                        'multiple': false,
                    }
                });
            });

        this._popover = new Popover({
            triggerElement: buttonElement,
            wrapperElement: popoverWrapper,
        });

        return wrapper;
    }

    /**
     * Compose the various parts of the component, and render it into the given "base" element of the component.
     */
    _render() {
        let wrapper = document.createElement("div");
        wrapper.classList.add("border", "border-1", "p-2", "ps-3", "pe-3", "rounded-2", "d-flex");
        wrapper.style = "align-items:center; justify-content: space-between;";
        this._labelElement = this._generateLabelElement();
        wrapper.append( this._labelElement, this._generateJsTreeTriggerElement() );
        this.element.appendChild(wrapper);
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