 export class Dialog {
    constructor ({ dialogElementId, triggerElementId, htmlFabricator, onRenderedCallback, onUpdatedCallback, onSubmit, onPreRefresh, dialogOptions, triggerByEvent=false, customTriggerName=undefined } = {}) {
        this.dialogElementId = dialogElementId;
        this.triggerElementId = triggerElementId;
        this.customTriggerName = customTriggerName;
        this.triggerByEvent = triggerByEvent,
        this.htmlFabricator = htmlFabricator;
        this.onRenderedCallback = onRenderedCallback;
        this.onUpdatedCallback = onUpdatedCallback;
        this.onSubmit = onSubmit;
        this.onPreRefresh = onPreRefresh;
        this.dialogOptions = dialogOptions;
        this._isRendering = false;

        this.discriminator = null;
    }

    _$getDialogEl() {
        return $("#" + this.dialogElementId + "." + this.discriminator);
    }

    async render(context) {
        if (this.discriminator)
            this.destroy();
        if (this._isRendering === false) {
            this._isRendering = true;
            if (this.isOpen() === false) {
                let html = await this.htmlFabricator(context);

                let span = document.createElement("span");
                span.innerHTML = html;
                let dialogEl = span.querySelector("#" + this.dialogElementId);
                $(dialogEl).toggle("highlight");

                this.discriminator = dialogEl.getAttribute("class");

                $('body')
                    .append(html)
                    .ready( () => {
                        this._$getDialogEl().dialog( this.dialogOptions );
                        this.onRenderedCallback(this, context);
                        this._$getDialogEl().dialog("widget").find('.ui-dialog-titlebar-close')
                            .html("<span id='railing'></span><span class='dialogCloseButton'><i class='fas fa-times float-end'></i></span>")
                            .click( () => {
                                this.destroy();
                            });
                        
                        this._isRendering = false;
                    });
            }
            else {
                this._isRendering = false;
            }
        }
        else {
            console.warn("Dialog is already rendering...")
        }
    }

    changeTitle(newTitle) {
        this._$getDialogEl().dialog('option', 'title', newTitle);
    }

    async refresh(context, html) {
        if (this.isOpen() === true) {
            if (this.onPreRefresh !== undefined) {
                await this.onPreRefresh(this);
            }

            if (html === undefined) {
                html = await this.htmlFabricator(context);
            }
            else { console.log(html); }

            let holderEl = document.createElement("span");
            holderEl.innerHTML = html;

            let activeDialog = document.querySelector("#" + this.dialogElementId);
            let tmpDialog = holderEl.querySelector("#" + this.dialogElementId);
            activeDialog.innerHTML = tmpDialog.innerHTML;
            this.changeTitle(tmpDialog.getAttribute("title"));

            this.onRenderedCallback(this, context);

            return;
        }

        console.warn("Tried refreshing a non-open dialog.")
    }

    close() {
        if (this.isOpen() === true) {
            if (typeof this.destructure !== "undefined")
                this.destructure();
            this.destroy();
        }
    }

    prepareDOM() {
        const selector = `#${this.dialogElementId}.${this.discriminator}`

        if (this.dialogElementId == "editEventSerieDialog") {
            selector += ",#newTimePlanDialog";
        }

        let elements = document.querySelectorAll(selector);

        elements.forEach(element => {
            element.remove();
        })
    }

    getInstance() {
        return this._$getDialogEl().dialog( "instance" );
    }

    destroy() {
        this._$getDialogEl().dialog( "destroy" );
        $(`[id=${this.dialogElementId}][class='${this.discriminator}']`).each(function (index, $dialogElement) {
            $dialogElement.remove();
        });
        this.discriminator=null;
    }

    isOpen() {
        let $dialogElement = this._$getDialogEl();

        if ($dialogElement[0] === undefined || this.getInstance() === false || $($dialogElement).dialog("isOpen") === false) {
            return false;
        }

        return true;
    }
}


export class DialogManager {
    constructor ({ managerName, dialogs }) {
        this.managerName = managerName;

        this._listenForUpdatedEvent();
        this._listenForSubmitEvent();
        this._listenForCloseAllEvent();
        this._listenForReloadEvent();
        this._listenForCloseDialogEvent();

        this._dialogRepository = new Map(dialogs);
        this.context = {};
    }
    
    async loadDialogHtml( 
            { url, managerName, dialogId, dialogTitle=undefined, customParameters=undefined } = {}) {
        const params = new URLSearchParams({
            managerName: managerName,
            dialogId: dialogId,
            dialogTitle: dialogTitle,
            ...customParameters
        });

        let mutated_url = `${url}?${params.toString()}`;
        return await fetch(mutated_url).then(response => response.text());
    }

    $getDialogElement(dialogId) {
        return this._dialogRepository.get(dialogId)._$getDialogEl();
    }

    setContext(ctxObj) {
        this.context = ctxObj;
    }

    reloadDialog(dialogId, customHtml=undefined) {
        this._dialogRepository.get(dialogId).refresh(this.context, customHtml);
    }

    openDialog(dialogId) {
        if (this._dialogRepository.has(dialogId)) {
            this._dialogRepository.get(dialogId).render(this.context);
            this._setTriggers();
        }
        else {
            console.error(`Dialog with key ${dialogId} does not exist. Repository: `, this._dialogRepository);
        }
    }

    closeDialog(dialogId) {
        this._dialogRepository.get(dialogId).close();
    }

    closeAllDialogs() {
        this._dialogRepository.forEach( (dialog) => {
            dialog.close();
        });
    }

    _listenForCloseDialogEvent() {
        document.addEventListener(`${this.managerName}.closeDialog`, (e) => {
            this.closeDialog(e.detail.dialog);
        });
    }

    _listenForCloseAllEvent() {
        document.addEventListener(`${this.managerName}.close`, (e) => {
            this.closeAllDialogs();
        })
    }

    /**
     * Listens for custom reload events being fired, allowing us to reload a dialog from 
     * anywhere. The dialog name must be specified in detail.
     * When called with valid dialog name it will reload the dialog with the given dialog name.
     */
    _listenForReloadEvent() {
        document.addEventListener(`${this.managerName}.reload`, (e) => {
            this.reloadDialog(e.detail.dialog);
        })
    }

    _listenForUpdatedEvent() {
        document.addEventListener(`${this.managerName}.hasBeenUpdated`, (e) => {
            this._dialogRepository.get(e.detail.dialog).onUpdatedCallback(this.context);
        });
    }

    _listenForSubmitEvent() {
        document.addEventListener(`${this.managerName}.submit`, async (e) => {
            let dialog = this._dialogRepository.get(e.detail.dialog);
            let submitResult = await dialog.onSubmit(this.context, e.detail);  // Trigger the dialogs onSubmit handling
            if (submitResult !== false) {
                dialog.onUpdatedCallback(this.context);  // Trigger the dialogs on update handling
            }
        })
    }

    _setTriggers() {
        this._dialogRepository.forEach( (value, key, map) => {
            if (value.triggerElementId !== undefined) {
                $("#" + value.triggerElementId).on('click', () => {
                    this.context.lastTriggererDetails = undefined;
                    this.context.lastTriggererElement = document.querySelector(`#${value.triggerElementId}`);
                    value.render(this.context);
                });
            }
        })
    }

    _makeAware() {
        this._setTriggers();

        this._dialogRepository.forEach(( value, key, map) => {
            if (value.triggerByEvent === true) {
                let triggerName = value.dialogElementId;
                if (value.customTriggerName !== undefined) {
                    triggerName = value.customTriggerName;
                }

                document.addEventListener(`${this.managerName}.${triggerName}.trigger`, (event) => {
                    this.context.lastTriggererDetails = event.detail;
                    value.render(this.context);

                    let parent = event.detail.$parent;
                    let current = $(value._$getDialogEl());
                    if (parent) {
                        $(parent).on("dialogdrag", function (event, ui) {
                            $(value._$getDialogEl()).dialog("option", "position", { my: "left+20 top", at: "right top", of: parent.parentNode });
                        });
                        current.on("dialogdrag", function (event, ui) {
                            console.log("current drag")
                            $(parent).dialog("option","position", { my: "right top", at: "left top", of: current[0].parentNode } )
                        });

                        value.dialogOptions = { 
                            dialogClass: "slave-dialog" + value.dialogOptions.dialogClass !== undefined ? (" " + value.dialogOptions.dialogClass) : "",
                            classes: {
                                "ui-dialog": "slave-dialog"
                            },
                            position: { my: "left top", at: "right top", of: parent.parentNode },
                            height: parent.parentNode.offsetHeight,
                            width: 600,
                            show: { effect: "slide", direction: "left", duration: 400 }
                        }
                        console.log("options", value.dialogOptions)
                    }
                });
            }
        });
    }
}