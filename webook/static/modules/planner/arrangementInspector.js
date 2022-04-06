import { DialogManager, Dialog } from "./dialog_manager/dialogManager.js";

const MANAGER_NAME = "arrangementInspector"

const MAIN_DIALOG = Symbol("mainDialog")
const ADD_PLANNER_DIALOG = Symbol("addPlannerDialog")

export class ArrangementInspector {
    constructor () {
        this.dialogManager = this._createDialogManager();
    }

    inspect( arrangement ) {
        console.log("Here we are: ", arrangement)
        this.dialogManager.setContext(arrangement);
        console.log(this.dialogManager.context)

        this.dialogManager.openDialog( "mainDialog" );
    }

    _listenToOrderRoomForSerieBtnClick() {
        $('.orderRoomBtn').on('click', (e) => {
            // this.openRoomFilterDialog(e.currentTarget.value);
            // this.dialogManager.setContext({ serie: { guid: e.currentTarget.value } });
            this.dialogManager.openDialog( "orderRoomDialog" );
        })
    }

    _listenToOrderPersonForSerieBtnClick() {
        $('.orderPersonBtn').on('click', (e) => {
            // this.openRoomFilterDialog(e.currentTarget.value);
            // this.dialogManager.setContext({ serie: { guid: e.currentTarget.value } });
            this.dialogManager.openDialog( "orderPersonDialog" );
        })
    }

    _createDialogManager () {
        return new DialogManager({
            managerName: MANAGER_NAME,
            dialogs: [
                [ 
                    "mainDialog",
                    new Dialog({
                        dialogElementId: "mainDialog",
                        triggerElementId: "_mainDialog",
                        htmlFabricator: async (context) => {
                            return await fetch('/arrangement/planner/dialogs/arrangement_information/' + context.slug + "?managerName=" + MANAGER_NAME)
                                    .then(response => response.text());
                        },
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

                            this.dialogManager._makeAware();
                            this._listenToOrderPersonForSerieBtnClick();
                            this._listenToOrderRoomForSerieBtnClick();
                        },
                        onSubmit: async (context, formData) => { 
                            var getArrangementHtml = async function (slug, formData, csrf_token) {
                                var response = await fetch("/arrangement/planner/dialogs/arrangement_information/" + slug, {
                                    method: 'POST',
                                    body: formData,
                                    headers: {
                                        "X-CSRFToken": csrf_token
                                    },
                                    credentials: 'same-origin',
                                });
                                return await response.text();
                            }
    
                            var somehtml = await getArrangementHtml(context.slug, formData, this.csrf_token);
                            this.reloadDialog("mainDialog", somehtml);
    
                            document.dispatchEvent(new Event("plannerCalendar.refreshNeeded"));
                        },
                        onUpdatedCallback: () => { this.reloadDialog("mainDialog"); },
                        dialogOptions: { width: 600 }
                    }),
                ],
                [
                    "addPlannerDialog",
                    new Dialog({
                        dialogElementId: "addPlannerDialog",
                        triggerElementId: "mainDialog__addPlannerBtn",
                        htmlFabricator: async (context) => {
                            return await fetch("/arrangement/planner/dialogs/add_planner?slug=" + context.slug + "&managerName=" + MANAGER_NAME)
                                .then(response => response.text());
                        },
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
                        htmlFabricator: async (context) => {
                            return await fetch("/arrangement/planner/dialogs/create_serie?slug=" + context.slug + "&managerName=" + MANAGER_NAME)
                                .then(response => response.text());
                        },
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
                        htmlFabricator: async (context) => {
                            return await fetch('/arrangement/planner/dialogs/create_simple_event?slug=' + context.slug + "&managerName=" + MANAGER_NAME)
                                .then(response => response.text());
                        },
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
                        htmlFabricator: async (arrangement) => {
                            return await fetch('/arrangement/planner/dialogs/arrangement_calendar_planner/' + arrangement.slug + "&managerName=" + MANAGER_NAME)
                                    .then(response => response.text())
                        },
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
                        htmlFabricator: async (context) => {
                            return await fetch("/arrangement/planner/dialogs/promote_main_planner?slug=" + context.slug + "&managerName=" + MANAGER_NAME)
                                .then(response => response.text());
                        },
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
                        htmlFabricator: async (arrangement) => {
                            return await fetch("/arrangement/planner/dialogs/new_note?slug=" + arrangement.slug + "&managerName=" + MANAGER_NAME)
                                .then(response => response.text());
                        },
                        onRenderedCallback: () => { console.info("Rendered") },
                        onUpdatedCallback: () => { this.reloadDialog("mainDialog"); this.closeDialog("newNoteDialog");  },
                        dialogOptions: { width: 500 },
                    })
                ],
                [
                    "orderPersonDialog",
                    new Dialog({
                        dialogElementId: "orderPersonDialog",
                        triggerElementId: undefined,
                        triggerByEvent: true,
                        htmlFabricator: async (context) => {
                            return await fetch("/arrangement/planner/dialogs/order_person")
                                .then(response => response.text());
                        },
                        onRenderedCallback: () => { this.dialogManager._makeAware(); },
                        dialogOptions: { width: 500 },
                        onSubmit: async (context, details) => {
                        }
                    })
                ],
                [
                    "orderRoomDialog",
                    new Dialog({
                        dialogElementId: "orderRoomDialog",
                        triggerElementId: undefined,
                        triggerByEvent: true,
                        htmlFabricator: async (context) => {
                            return await fetch("/arrangement/planner/dialogs/order_room")
                                .then(response => response.text());
                        },
                        onRenderedCallback: () => { this.dialogManager._makeAware(); },
                        dialogOptions: { width: 500 },
                        onSubmit: async (context, details) => {
                        }
                    })
                ]
            ]}
        )
    }
}