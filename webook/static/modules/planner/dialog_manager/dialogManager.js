 export class Dialog {
    constructor ({ dialogElementId, triggerElementId, htmlFabricator, onRenderedCallback, onUpdatedCallback, onSubmit, onPreRefresh, dialogOptions, triggerByEvent=false } = {}) {
        this.dialogElementId = dialogElementId;
        this.triggerElementId = triggerElementId;
        this.triggerByEvent = triggerByEvent,
        this.htmlFabricator = htmlFabricator;
        this.onRenderedCallback = onRenderedCallback;
        this.onUpdatedCallback = onUpdatedCallback;
        this.onSubmit = onSubmit;
        this.onPreRefresh = onPreRefresh;
        this.dialogOptions = dialogOptions;
    }

    _$getDialogEl() {
        return $("#" + this.dialogElementId);
    }

    async render(context) {
        this.prepareDOM();

        $('#' + this.dialogElementId).remove();

        this.dialogOptions.closeText = "hello";

        if (this.isOpen() === false) {
            $('body')
                .append(await this.htmlFabricator(context))
                .ready( () => {
                    this.onRenderedCallback(this);
                    this._$getDialogEl().dialog( this.dialogOptions );    
                    this._$getDialogEl().dialog("widget").find('.ui-dialog-titlebar-close')
                        .html("<i class='fas fa-times text-danger' style='font-size: 24px'></i>");
                });
        }
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

            var holderEl = document.createElement("span");
            holderEl.innerHTML = html;

            document.querySelector("#" + this.dialogElementId).innerHTML 
                = holderEl.querySelector("#" + this.dialogElementId).innerHTML;

            this.onRenderedCallback(this);

            return;
        }

        console.warn("Tried refreshing a non-open dialog.")
    }

    close() {
        if (this.isOpen() === true) {
            this._$getDialogEl().dialog("close");
        }
    }

    prepareDOM() {
        var $dialogElement = this._$getDialogEl();
        if ($dialogElement[0] !== undefined) {
            $dialogElement[0].remove();
        }
    }

    isOpen() {
        var $dialogElement = this._$getDialogEl();

        if ($dialogElement[0] === undefined || $($dialogElement).dialog("isOpen") === false) {
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

        this._dialogRepository = new Map(dialogs);
        this.context = {};
    }

    setContext(ctxObj) {
        this.context = ctxObj;
    }

    reloadDialog(dialogId, customHtml=undefined) {
        console.log("reloadDialog " + dialogId)
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
        this._dialogRepository.values.forEach( (dialog) => {
            dialog.close();
        })
    }

    _listenForUpdatedEvent() {
        document.addEventListener(`${this.managerName}.hasBeenUpdated`, (e) => {
            this._dialogRepository.get(e.detail.dialog)
                .onUpdatedCallback();
        });
    }

    _listenForSubmitEvent() {
        console.log(`${this.managerName}.submit`)
        document.addEventListener(`${this.managerName}.submit`, (e) => {
            this._dialogRepository.get(e.detail.dialog)
                .onSubmit(this.context, e.detail);
        })
    }

    _setTriggers() {
        this._dialogRepository.forEach( (value, key, map) => {
            if (value.triggerByEvent === true) {
                console.log(`${this.managerName}.${value.dialogElementId}.trigger`)
                document.addEventListener(`${this.managerName}.${value.dialogElementId}.trigger`, (detail) => {
                    console.log("trigger by triggered")
                    value.render(this.context);
                });
            }

            if (value.triggerElementId !== undefined) {
                $("#" + value.triggerElementId).on('click', () => {
                    value.render(this.context);
                });
            }
        })
    }

    _makeAware() {
        this._setTriggers();
    }
}