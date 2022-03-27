/**
 * arrangementInspector.js
 * 
 * This should, when time allows, be split into a more re-usable component. The business logic
 * is too integrated with dialog management and dialog concerns. I think the best solution is to
 * split this up into a dialog manager, and then a consumer of said manager. Allows us to use the dialog approach
 * in more than just the main calendar -- which may be neat.
 */

class Dialog {
    constructor ({ dialogElementId, triggerElementId, htmlFabricator, onRenderedCallback, onUpdatedCallback, onPreRefresh, dialogOptions } = {}) {
        this.dialogElementId = dialogElementId;
        this.triggerElementId = triggerElementId;
        this.htmlFabricator = htmlFabricator;
        this.onRenderedCallback = onRenderedCallback;
        this.onUpdatedCallback = onUpdatedCallback;
        this.onPreRefresh = onPreRefresh;
        this.dialogOptions = dialogOptions;
    }

    _$getDialogEl() {
        return $("#" + this.dialogElementId);
    }

    async render(arrangement) {
        this.prepareDOM();

        if (this.isOpen() === false) {
            $('body')
                .append(await this.htmlFabricator(arrangement))
                .ready( () => {
                    this.onRenderedCallback(this);
                    this._$getDialogEl().dialog( this.dialogOptions );       
                });
        }
    }

    async refresh(arrangement) {
        if (this.isOpen() === true) {
            if (this.onPreRefresh !== undefined) {
                await this.onPreRefresh(this);
            }

            var html = await this.htmlFabricator(arrangement);
            var holderEl = document.createElement("span");
            holderEl.innerHTML = html;
            var realHtml = holderEl.querySelector("#" + this.dialogElementId).innerHTML;
            document.querySelector("#" + this.dialogElementId).innerHTML = realHtml;

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


export class ArrangementInspector {
    constructor () {
        this._listenForRepopRequest();
        this._listenForUpdatedRequest();

        this._dialogRepository = new Map([
            [ 
                "mainDialog", 
                new Dialog({
                    dialogElementId: "mainDialog",
                    triggerElementId: "_mainDialog",
                    htmlFabricator: this._fabricateMainDialog,
                    onPreRefresh: (dialog) => {
                        var active = $('#tabs').tabs ( "option", "active" );
                        dialog._active_tab = active;
                    },
                    onRenderedCallback: (dialog) => {
                        $('#tabs').tabs(); 

                        if (dialog._active_tab !== undefined) {
                            $('#tabs').tabs("option", "active", dialog._active_tab);
                            dialog._active_tab = undefined;
                        }

                        this._makeAware(); 
                    },
                    onUpdatedCallback: () => { return false; },
                    dialogOptions: { width: 600 }
                }) 
            ],
            [
                "addPlannerDialog",
                new Dialog({
                    dialogElementId: "addPlannerDialog",
                    triggerElementId: "mainDialog__addPlannerBtn",
                    htmlFabricator: this._fabricateAddPlannerDialog,
                    onRenderedCallback: () => { console.info("Rendered"); },
                    onUpdatedCallback: ( ) => { this.reloadDialog("mainDialog"); this.closeDialog("addPlannerDialog"); },
                    dialogOptions: { width: 700 }
                })
            ],
            [
                "newTimePlanDialog",
                new Dialog({
                    dialogElementId: "newTimePlanDialog",
                    triggerElementId: "mainPlannerDialog__newTimePlan",
                    htmlFabricator: this._fabricateNewTimePlanDialog,
                    onRenderedCallback: () => { console.info("Rendered"); },
                    onUpdatedCallback: () => { this.reloadDialog("mainDialog"); this.closeDialog("newTimePlanDialog"); },
                    dialogOptions: { width: 700 }
                })
            ],
            [
                "newSimpleActivityDialog",
                new Dialog({
                    dialogElementId: "newSimpleActivityDialog",
                    triggerElementId: "mainPlannerDialog__newSimpleActivity",
                    htmlFabricator: this._fabricateNewSimpleActivityDialog,
                    onRenderedCallback: () => { console.info("Rendered") },
                    onUpdatedCallback: () => { this.reloadDialog("mainDialog"); this.closeDialog("newSimpleActivityDialog"); },
                    dialogOptions: { width: 500 }
                })
            ],
            [
                "calendarFormDialog",
                new Dialog({
                    dialogElementId: "calendarFormDialog",
                    triggerElementId: "mainPlannerDialog__showInCalendarForm",
                    htmlFabricator: this._fabricateCalendarFormDialog,
                    onRenderedCallback: () => { console.info("Rendered") },
                    onUpdatedCallback: () => { return false; },
                    dialogOptions: { width: 1200, height: 700 }
                })
            ],
            [
                "promotePlannerDialog",
                new Dialog({
                    dialogElementId: "promotePlannerDialog",
                    triggerElementId: "mainPlannerDialog__promotePlannerBtn",
                    htmlFabricator: this._fabricatePromotePlannerDialog,
                    onRenderedCallback: () => { console.info("Rendered") },
                    onUpdatedCallback: () => { this.reloadDialog("mainDialog"); this.closeDialog("promotePlannerDialog"); },
                    dialogOptions: { width: 500 },
                })
            ],
            [
                "newNoteDialog",
                new Dialog({
                    dialogElementId: "newNoteDialog",
                    triggerElementId: "mainPlannerDialog__newNoteBtn",
                    htmlFabricator: this._fabricateNewNoteDialog,
                    onRenderedCallback: () => { console.info("Rendered") },
                    onUpdatedCallback: () => { this.reloadDialog("mainDialog"); this.closeDialog("newNoteDialog");  },
                    dialogOptions: { width: 500 },
                })
            ],
            [
                "addPlannerDialog",
                new Dialog({
                    dialogElementId: "addPlannerDialog",
                    triggerElementId: "mainPlannerDialog__addPlannerBtn",
                    htmlFabricator: this._fabricateAddPlannerDialog,
                    onRenderedCallback: () => { console.info("Rendered") },
                    onUpdatedCallback: () => { this.reloadDialog("mainDialog"); this.closeDialog("addPlannerDialog");  },
                    dialogOptions: { width: 500 },  
                })
            ],
        ]);

        this.dialogElIdToDialogTriggerKey = new Map();
        this._dialogRepository.forEach((value, key) => {
            this.dialogElIdToDialogTriggerKey.set(value.dialogElementId, key);
        });
    }

    reloadDialog(dialogId) {
        this._dialogRepository.get(dialogId).refresh(this.arrangement);
    }

    closeDialog(dialogId) {
        this._dialogRepository.get(dialogId).close();
    }

    _listenForRepopRequest() {
        document.addEventListener("arrangementPlannerDialogs.repop", () => {
            this.repop();
        })
    }
    _listenForUpdatedRequest() {
        document.addEventListener("arrangementPlannerDialogs.hasBeenUpdated", (e) => {
            console.log(">> UPDATED HANDLER!!")
            this._dialogRepository.get(e.detail.dialog).onUpdatedCallback();
        });
    }

    repop() {
        this._dialogRepository.forEach( (value, key, map) => {
            var dialogEl = $("#" + value.dialogElementId);
            if (dialogEl !== undefined) {
                console.log("DESTROY " + value.dialogElementId)
                dialogEl.dialog("destroy");
            }

            this.inspectArrangement(this.arrangement);
        });
    }

    inspectArrangement( arrangement ) {
        this.arrangement = arrangement;
        this._dialogRepository.get("mainDialog").render(arrangement);

        this.$nameField = undefined;
        this.$targetAudienceField = undefined;
        this.$arrangementTypeField = undefined;
        this.$startsWhenField = undefined;
        this.$endsWhenField = undefined;
        this.$plannersField = undefined;
        this.$multimediaSwitch = undefined;

        this.$saveArrangementBtn = undefined;
        this.$editArrangementBtn = undefined;
        this.$openInDetailedViewBtn = undefined;
        this.$archiveArrangementBtn = undefined;
        this.$addPlannerBtn = undefined;
    }

    _setTriggers() {
        this._dialogRepository.forEach( (value, key, map) => {
            console.log(" >> Binding to " + value.triggerElementId)
            console.log(value);
            $("#" + value.triggerElementId).on('click', () => {
                value.render(this.arrangement);
            });
        })
    }

    _makeAware() {
        this.$nameField = $('#mainPlannerDialog__nameField');
        this.$addPlannerBtn = $('#mainDialog__addPlannerBtn');
        this.$newTimePlanBtn = $('#mainPlannerDialog__newTimePlan');
        this.$newSimpleActivityBtn = $('#mainPlannerDialog__newSimpleActivity');
        this.$showInCalendarFormBtn = $('#mainPlannerDialog__showInCalendarForm');
        this.$promoteNewPlannerBtn = $('#mainPlannerDialog__promotePlannerBtn');

        this._setTriggers();
    }

    async _fabricateAddPlannerDialog(arrangement) {
        return await fetch("/arrangement/planner/dialogs/add_planner?slug=" + arrangement.slug)
            .then(response => response.text());
    }

    async _fabricateNewNoteDialog(arrangement) {
        return await fetch("/arrangement/planner/dialogs/new_note?slug=" + arrangement.slug)
            .then(response => response.text());
    }

    async _fabricatePromotePlannerDialog(arrangement) {
        return await fetch("/arrangement/planner/dialogs/promote_main_planner?slug=" + arrangement.slug)
            .then(response => response.text());
    }

    async _fabricateNewTimePlanDialog(arrangement) {
        return await fetch("/arrangement/planner/dialogs/create_serie?slug=" + arrangement.slug)
            .then(response => response.text());
    }

    async _fabricateNewSimpleActivityDialog(arrangement) {
        return await fetch('/arrangement/planner/dialogs/create_simple_event?slug=' + arrangement.slug)
            .then(response => response.text());
    }

    async _fabricateCalendarFormDialog(arrangement) {
        return await fetch('/arrangement/planner/dialogs/arrangement_calendar_planner/' + arrangement.slug)
                .then(response => response.text())
    }

    async _fabricateMainDialog(arrangement) {
        return await fetch('/arrangement/planner/dialogs/arrangement_information/' + arrangement.slug)
                .then(response => response.text());
    }
}