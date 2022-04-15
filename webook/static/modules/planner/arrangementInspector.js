import { DialogManager, Dialog } from "./dialog_manager/dialogManager.js";

const MANAGER_NAME = "arrangementInspector"

const MAIN_DIALOG = Symbol("mainDialog")
const ADD_PLANNER_DIALOG = Symbol("addPlannerDialog")

export class ArrangementInspector {
    constructor () {
        this.dialogManager = this._createDialogManager();
    }

    inspect( arrangement ) {
        this.dialogManager.setContext({ arrangement: arrangement });
        this.dialogManager.openDialog( "mainDialog" );
    }

    _listenToOrderRoomForSingleEventBtnClick() {
        $('.orderRoomForSingleEventBtn').on('click', (e) => {
            this.dialogManager.setContext({ arrangement: this.dialogManager.context.arrangement, event: { pk: e.currentTarget.value } });
            this.dialogManager.openDialog( "orderRoomForOneEventDialog" );
        })
    }

    _listenToOrderPersonForSingleEventeBtnClick() {
        $('.orderPersonForSingleEventBtn').on('click', (e) => {
            this.dialogManager.setContext({ arrangement: this.dialogManager.context.arrangement, event: { pk: e.currentTarget.value } });
            this.dialogManager.openDialog( "orderPersonForOneEventDialog" );
        })
    }

    _listenToOrderRoomForSerieBtnClick() {
        $('.orderRoomBtn').on('click', (e) => {
            this.dialogManager.setContext({ arrangement: this.dialogManager.context.arrangement, serie: { guid: e.currentTarget.value } });
            this.dialogManager.openDialog( "orderRoomDialog" );
        })
    }

    _listenToOrderPersonForSerieBtnClick() {
        $('.orderPersonBtn').on('click', (e) => {
            this.dialogManager.setContext({ arrangement: this.dialogManager.context.arrangement, serie: { guid: e.currentTarget.value } });
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
                            return await fetch('/arrangement/planner/dialogs/arrangement_information/' + context.arrangement.slug + "?managerName=" + MANAGER_NAME)
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
                            this._listenToOrderRoomForSingleEventBtnClick();
                            this._listenToOrderPersonForSingleEventeBtnClick();
                        },
                        onSubmit: async (context, details) => { 
                            
                            var getArrangementHtml = async function (slug, formData) {
                                var response = await fetch("/arrangement/planner/dialogs/arrangement_information/" + slug, {
                                    method: 'POST',
                                    body: formData,
                                    credentials: 'same-origin',
                                    headers: {
                                        "X-CSRFToken": formData.get("csrfmiddlewaretoken")
                                    }
                                });
                                return await response.text();
                            }
    
                            var somehtml = await getArrangementHtml(context.arrangement.slug, details.formData);
                            this.dialogManager.reloadDialog("mainDialog", somehtml);
    
                            document.dispatchEvent(new Event("plannerCalendar.refreshNeeded"));
                        },
                        onUpdatedCallback: () => { this.dialogManager.reloadDialog("mainDialog"); },
                        dialogOptions: { width: 800, height: 800 }
                    }),
                ],
                [
                    "addPlannerDialog",
                    new Dialog({
                        dialogElementId: "addPlannerDialog",
                        triggerElementId: "mainDialog__addPlannerBtn",
                        htmlFabricator: async (context) => {
                            return await fetch("/arrangement/planner/dialogs/add_planner?slug=" + context.arrangement.slug + "&managerName=" + MANAGER_NAME)
                                .then(response => response.text());
                        },
                        onRenderedCallback: () => { console.info("Rendered"); },
                        onUpdatedCallback: ( ) => { this.dialogManager.reloadDialog("mainDialog"); this.dialogManager.closeDialog("addPlannerDialog"); },
                        dialogOptions: { width: 700 }
                    })
                ],
                [
                    "uploadFilesToArrangementDialog",
                    new Dialog({
                        dialogElementId: "uploadFilesToArrangementDialog",
                        triggerElementId: "mainDialog__uploadFilesBtn",
                        htmlFabricator: async (context) => {
                            console.log("context", context)
                            return await fetch("/arrangement/planner/dialogs/upload_files_to_arrangement?arrangement_slug=" + context.arrangement.slug)
                                .then(response => response.text());
                        },
                        onRenderedCallback: () => { console.info("Rendered"); },
                        onUpdatedCallback: ( ) => { this.dialogManager.reloadDialog("mainDialog"); this.dialogManager.closeDialog("addPlannerDialog"); },
                        dialogOptions: { width: 400 }
                    })
                ],
                [
                    "newTimePlanDialog",
                    new Dialog({
                        dialogElementId: "newTimePlanDialog",
                        triggerElementId: "mainPlannerDialog__newTimePlan",
                        htmlFabricator: async (context) => {
                            return await fetch("/arrangement/planner/dialogs/create_serie?slug=" + context.arrangement.slug + "&managerName=" + MANAGER_NAME)
                                .then(response => response.text());
                        },
                        onRenderedCallback: () => { 
                            $('#serie_title').attr('value', $('#id_name').val() );
                            $('#serie_title_en').attr('value', $('#id_name_en').val() );
                        },
                        onUpdatedCallback: () => { this.dialogManager.reloadDialog("mainDialog"); this.dialogManager.closeDialog("newTimePlanDialog"); },
                        dialogOptions: { width: 700 },
                        onSubmit: () => { }
                    })
                ],
                [
                    "newSimpleActivityDialog",
                    new Dialog({
                        dialogElementId: "newSimpleActivityDialog",
                        triggerElementId: "mainPlannerDialog__newSimpleActivity",
                        htmlFabricator: async (context) => {
                            return await fetch('/arrangement/planner/dialogs/create_simple_event?slug=' + context.arrangement.slug + "&managerName=" + MANAGER_NAME)
                                .then(response => response.text());
                        },
                        onRenderedCallback: () => { console.info("Rendered") },
                        onUpdatedCallback: () => { this.dialogManager.reloadDialog("mainDialog"); this.dialogManager.closeDialog("newSimpleActivityDialog"); },
                        dialogOptions: { width: 500 }
                    })
                ],
                [
                    "calendarFormDialog",
                    new Dialog({
                        dialogElementId: "calendarFormDialog",
                        triggerElementId: "mainPlannerDialog__showInCalendarForm",
                        htmlFabricator: async (context) => {
                            return await fetch('/arrangement/planner/dialogs/arrangement_calendar_planner/' + context.arrangement.slug + "&managerName=" + MANAGER_NAME)
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
                            return await fetch("/arrangement/planner/dialogs/promote_main_planner?slug=" + context.arrangement.slug + "&managerName=" + MANAGER_NAME)
                                .then(response => response.text());
                        },
                        onRenderedCallback: () => { console.info("Rendered") },
                        onUpdatedCallback: () => { this.dialogManager.reloadDialog("mainDialog"); this.dialogManager.closeDialog("promotePlannerDialog"); },
                        dialogOptions: { width: 500 },
                    })
                ],
                [
                    "newNoteDialog",
                    new Dialog({
                        dialogElementId: "newNoteDialog",
                        triggerElementId: "mainPlannerDialog__newNoteBtn",
                        htmlFabricator: async (context) => {
                            return await fetch("/arrangement/planner/dialogs/new_note?slug=" + context.arrangement.slug + "&managerName=" + MANAGER_NAME)
                                .then(response => response.text());
                        },
                        onRenderedCallback: () => { console.info("Rendered") },
                        onUpdatedCallback: () => { this.dialogManager.reloadDialog("mainDialog"); this.dialogManager.closeDialog("newNoteDialog");  },
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
                            return await fetch("/arrangement/planner/dialogs/order_person?serie_guid=" + context.serie.guid)
                                .then(response => response.text());
                        },
                        onRenderedCallback: () => { this.dialogManager._makeAware(); },
                        dialogOptions: { width: 500 },
                        onSubmit: async (context, details) => {
                            console.log(">> OnSubmit ", details);

                            fetch("/arrangement/planner/dialogs/order_people_form", {
                                method: "POST",
                                body: details.formData,
                                headers: {
                                    "X-CSRFToken": details.csrf_token
                                }
                            }).then(_ => { this.dialogManager.reloadDialog("mainDialog"); this.dialogManager.closeDialog("orderPersonDialog"); });
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
                            return await fetch("/arrangement/planner/dialogs/order_room?serie_guid=" + context.serie.guid)
                                .then(response => response.text());
                        },
                        onRenderedCallback: () => { this.dialogManager._makeAware(); },
                        dialogOptions: { width: 500 },
                        onUpdatedCallback: () => { this.dialogManager.reloadDialog("mainDialog"); this.dialogManager.closeDialog("orderRoomDialog");  },
                        onSubmit: async (context, details) => {
                            console.log("OnSubmit", details)
                            fetch("/arrangement/planner/dialogs/order_rooms_form", {
                                method: "POST",
                                body: details.formData,
                                headers: {
                                    "X-CSRFToken": details.csrf_token
                                }
                            }).then(_ => { this.dialogManager.reloadDialog("mainDialog"); this.dialogManager.closeDialog("orderRoomDialog"); });

                        }
                    })
                ],
                [
                    "orderRoomForOneEventDialog",
                    new Dialog({
                        dialogElementId: "orderRoomDialog",
                        triggerElementId: undefined,
                        triggerByEvent: true,
                        htmlFabricator: async (context) => {
                            return await fetch("/arrangement/planner/dialogs/order_room?event_pk=" + context.event.pk)
                                .then(response => response.text());
                        },
                        onRenderedCallback: () => { this.dialogManager._makeAware(); },
                        onUpdatedCallback: () => { console.log("seville"); this.dialogManager.reloadDialog("mainDialog"); },
                        dialogOptions: { width: 500 },
                        onSubmit: async (context, details) => {
                            fetch("/arrangement/planner/dialogs/order_rooms_for_event_form", {
                                method: "POST",
                                body: details.formData,
                                headers: {
                                    "X-CSRFToken": details.csrf_token
                                }
                            }).then(_ => { this.dialogManager.reloadDialog("mainDialog"); this.dialogManager.closeDialog("orderRoomForOneEventDialog"); });;
                        }
                    })
                ],
                [
                    "orderPersonForOneEventDialog",
                    new Dialog({
                        dialogElementId: "orderPersonDialog",
                        triggerElementId: undefined,
                        triggerByEvent: true,
                        htmlFabricator: async (context) => {
                            return await fetch("/arrangement/planner/dialogs/order_person?event_pk=" + context.event.pk)
                                .then(response => response.text());
                        },
                        onRenderedCallback: () => { this.dialogManager._makeAware(); },
                        dialogOptions: { width: 500 },
                        onUpdatedCallback: () => { this.dialogManager.reloadDialog("mainDialog"); },
                        onSubmit: async (context, details) => {
                            console.log("OnSubmit", details)
                            fetch("/arrangement/planner/dialogs/order_people_for_event_form", {
                                method: "POST",
                                body: details.formData,
                                headers: {
                                    "X-CSRFToken": details.csrf_token
                                }
                            }).then(_ => { this.dialogManager.reloadDialog("mainDialog"); this.dialogManager.closeDialog("orderPersonForOneEventDialog"); });;
                        }
                    })
                ]
            ]}
        )
    }
}