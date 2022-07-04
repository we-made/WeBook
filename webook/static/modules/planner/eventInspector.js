import { Dialog, DialogManager } from "./dialog_manager/dialogManager.js";
import { QueryStore } from "./querystore.js";

export class EventInspector {
    constructor () {
        this.dialogManager = new DialogManager({
            managerName: "eventInspector",
            dialogs: [
                [
                    "inspectEventDialog",
                    new Dialog({
                        dialogElementId: "inspectEventDialog",
                        triggerElementId: "_inspectEventDialog",
                        htmlFabricator: async (context) => {
                            return await fetch("/arrangement/planner/dialogs/event_inspector/" + context.event.pk)
                                .then(response => response.text());
                        },
                        onRenderedCallback: () => { 
                            this.dialogManager._makeAware(); 
                            document.querySelectorAll('.form-outline').forEach((formOutline) => {
                                new mdb.Input(formOutline).init();
                            });
                        },
                        dialogOptions: { width: 700, heigth: 1000 },
                        onUpdatedCallback: () => {
                            this.dialogManager.closeDialog("inspectEventDialog");
                        },
                        onSubmit: async (context, details) => {
                            await QueryStore.UpdateEvents( [details.event], details.csrf_token )
                                .then(_ => document.dispatchEvent(new Event("plannerCalendar.refreshNeeded")));
                        }
                    }),
                ],
                [
                    "orderPersonDialog",
                    new Dialog({
                        dialogElementId: "orderPersonDialog",
                        triggerElementId: "inspectEventDialog_addPeopleBtn",
                        htmlFabricator: async (context) => {
                            return await fetch(`/arrangement/planner/dialogs/order_person?event_pk=${context.event.pk}&manager=eventInspector&dialog=orderPersonDialog`)
                                .then(response => response.text());
                        },
                        onRenderedCallback: () => { },
                        dialogOptions: { width: 500 },
                        onUpdatedCallback: () => { 
                            this.dialogManager.closeDialog("orderPersonDialog");
                        },
                        onSubmit: (context, details) => {
                            var people_ids = details.formData.get("people_ids");
                            context.people = people_ids;
                            context.people_name_map = details.people_name_map;
                            
                            document.dispatchEvent(new CustomEvent(
                                "eventInspector.peopleUpdated",
                                { detail: {
                                    context: context
                                } }
                            ));
                        }
                    })
                ],
                [
                    "orderRoomDialog",
                    new Dialog({
                        dialogElementId: "orderRoomDialog",
                        triggerElementId: "inspectEventDialog_addRoomsBtn",
                        htmlFabricator: async (context) => {
                            return await fetch(`/arrangement/planner/dialogs/order_room?event_pk=${context.event.pk}&manager=eventInspector&dialog=orderRoomDialog`)
                                .then(response => response.text());
                        },
                        onRenderedCallback: () => { },
                        dialogOptions: { width: 500 },
                        onUpdatedCallback: () => { 
                            this.dialogManager.closeDialog("orderRoomDialog"); 
                        },
                        onSubmit: (context, details) => { 
                            context.rooms = details.formData.get("room_ids");
                            context.room_name_map = details.room_name_map;
                            
                            document.dispatchEvent(new CustomEvent("eventInspector.roomsUpdated", { detail: { context: context } }))
                        }
                    })
                ],
                [
                    "uploadFilesDialog",
                    new Dialog({
                        dialogElementId: "uploadFilesDialog",
                        triggerElementId: "eventDialog_uploadFilesBtn",
                        htmlFabricator: async (context) => {
                            return await fetch(`/arrangement/planner/dialogs/upload_files_dialog?manager=eventInspector&dialog=uploadFilesDialog`)
                                .then(response => response.text());
                        },
                        onRenderedCallback: (dialogInstance, context) => {},
                        dialogOptions: { width: 600 },
                        onUpdatedCallback: () => { 
                            this.dialogManager.closeDialog("uploadFilesDialog"); 
                            this.dialogManager.reloadDialog("inspectEventDialog"); 
                        },
                        onSubmit: async (context, details) => {
                            details.formData.append("pk", context.event.pk);
                            await fetch(`/arrangement/event/${context.event.pk}/upload`, {
                                method: 'POST',
                                body: details.formData,
                                headers: {
                                    'X-CSRFToken': details.csrf_token
                                }
                            });
                        }
                    })
                ],
                [
                    "newNoteDialog",
                    new Dialog({
                        dialogElementId: 'newNoteDialog',
                        triggerElementId: 'inspectEventDialog__newNoteBtn',
                        htmlFabricator: async (context) => {
                            return await fetch("/arrangement/planner/dialogs/new_note?pk=" + context.event.pk + "&manager=eventInspector" + "&entityType=event")
                                .then(response => response.text());
                        },
                        onRenderedCallback: () => { console.info("Rendered") },
                        onUpdatedCallback: () => {
                            this.dialogManager.reloadDialog("inspectEventDialog");
                            this.dialogManager.closeDialog("newNoteDialog");
                        },
                        onSubmit: async (context, details) => {
                            await fetch('/arrangement/note/post', {
                                method: 'POST',
                                body: details.formData,
                                credentials: 'same-origin',
                            }).then(response => console.log("response", response));
                        },
                        dialogOptions: { width: 500 },
                    })
                ],
                [
                    "editNoteDialog",
                    new Dialog({
                        dialogElementId: "editNoteDialog",
                        triggerElementId: undefined,
                        triggerByEvent: true,
                        htmlFabricator: async (context) => {
                            return await fetch("/arrangement/planner/dialogs/edit_note/" + context.lastTriggererDetails.note_pk + "?manager=eventInspector" + "&dialog=editNoteDialog")
                                .then(response => response.text());
                        },
                        onRenderedCallback: () => { console.info("Rendered"); },
                        onUpdatedCallback: () => {
                            this.dialogManager.reloadDialog("inspectEventDialog");
                            this.dialogManager.closeDialog("editNoteDialog");
                        },
                        onSubmit: async (context, details) => {
                            await fetch('/arrangement/planner/dialogs/edit_note/' + details.formData.get("id"), {
                                method: 'POST',
                                body: details.formData, 
                                headers: {
                                    'X-CSRFToken': details.csrf_token,
                                }
                            })
                        },
                        dialogOptions: { width: 500 },
                    })
                ]
            ]            
        })
    }

    inspect(pk) {
        this.dialogManager.setContext({ event: { pk: pk } });
        this.dialogManager.openDialog( "inspectEventDialog" );
    }    
}