class Dialog {
    constructor ({ dialogElementId, htmlFabricator, onRenderedCallback, dialogOptions } = {}) {
        this.dialogElementId = dialogElementId;
        this.htmlFabricator = htmlFabricator;
        this.onRenderedCallback = onRenderedCallback;
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
                    this.onRenderedCallback();
                    this._$getDialogEl().dialog( this.dialogOptions );       
                });
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
        this._dialogRepository = new Map([
            [ 
                "_mainDialog", 
                new Dialog({ 
                    dialogElementId: "mainDialog",
                    htmlFabricator: this._fabricateMainDialog,
                    onRenderedCallback: () => { $('#tabs').tabs(); this._makeAware(); },
                    dialogOptions: { width: 600 }
                }) 
            ],
            [
                "mainDialog__addPlannerBtn",
                new Dialog({
                    dialogElementId: "addPlannerDialog",
                    htmlFabricator: this._fabricateAddPlannerDialog,
                    onRenderedCallback: () => { console.info("Rendered"); },
                    dialogOptions: { width: 700 }
                })
            ],
            [
                "mainPlannerDialog__newTimePlan",
                new Dialog({
                    dialogElementId: "newTimePlanDialog",
                    htmlFabricator: this._fabricateNewTimePlanDialog,
                    onRenderedCallback: () => { console.info("Rendered"); },
                    dialogOptions: { width: 700 }
                })
            ],
            [
                "mainPlannerDialog__newSimpleActivity",
                new Dialog({
                    dialogElementId: "newSimpleActivityDialog",
                    htmlFabricator: this._fabricateNewSimpleActivityDialog,
                    onRenderedCallback: () => { console.info("Rendered") },
                    dialogOptions: { width: 500 }
                })
            ],
            [
                "mainPlannerDialog__showInCalendarForm",
                new Dialog({
                    dialogElementId: "calendarFormDialog",
                    htmlFabricator: this._fabricateCalendarFormDialog,
                    onRenderedCallback: () => { console.info("Rendered") },
                    dialogOptions: { width: 1200, height: 700 }
                })
            ],
            [
                "mainPlannerDialog__promotePlannerBtn",
                new Dialog({
                    dialogElementId: "promotePlannerDialog",
                    htmlFabricator: this._fabricatePromotePlannerDialog,
                    onRenderedCallback: () => { console.info("Rendered") },
                    dialogOptions: { width: 500 },
                })
            ],
            [
                "mainPlannerDialog__newNoteBtn",
                new Dialog({
                    dialogElementId: "newNoteDialog",
                    htmlFabricator: this._fabricateNewNoteDialog,
                    onRenderedCallback: () => { console.info("Rendered") },
                    dialogOptions: { width: 500 },
                })
            ],
            [
                "mainPlannerDialog__addPlannerBtn",
                new Dialog({
                    dialogElementId: "addPlannerDialog",
                    htmlFabricator: this._fabricateAddPlannerDialog,
                    onRenderedCallback: () => { console.info("Rendered") },
                    dialogOptions: { width: 500 }
                })
            ],
        ])
    }

    _listenForRepopRequest() {
        document.addEventListener("arrangementPlannerDialogs.repop", () => {
            this.repop();
        })
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
        this._dialogRepository.get("_mainDialog").render(arrangement);

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
            $("#" + key).on('click', () => {
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