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
                        triggerByEvent: true,
                        htmlFabricator: async (context) => {
                            if (context.lastTriggererDetails !== undefined && context.lastTriggererDetails.pk !== undefined) {
                                context.event.pk = context.lastTriggererDetails.pk;
                            }   

                            return this.dialogManager.loadDialogHtml({
                                url: "/arrangement/planner/dialogs/event_inspector/" + context.event.pk,
                                managerName: "eventInspector",
                                dialogId: "inspectEventDialog",
                                dialogTitle: "Inspect event",
                            });
                        },
                        onRenderedCallback: () => { 
                            this.dialogManager._makeAware(); 
                            document.querySelectorAll('.form-outline').forEach((formOutline) => {
                                new mdb.Input(formOutline).init();
                            });
                        },
                        dialogOptions: { width: 1000, height: 900, dialogClass: 'no-titlebar', modal:true, },
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
                        triggerByEvent: true,
                        htmlFabricator: async (context) => {
                            let multiple = context.lastTriggererDetails.multiple;
                            if (multiple === undefined)
                                multiple = true
                                
                            return this.dialogManager.loadDialogHtml({
                                url: '/arrangement/planner/dialogs/order_person',
                                managerName: 'eventInspector',
                                dialogId: 'orderPersonDialog',
                                customParameters: {
                                    event_pk: context.event.pk,
                                    multiple: multiple,
                                    recipientDialogId: context.lastTriggererDetails.sendTo,
                                },
                            });
                        },
                        onRenderedCallback: () => { },
                        dialogOptions: { 
                            width: 500,
                            dialogClass: 'no-titlebar',
                        },
                        onUpdatedCallback: () => { 
                            this.dialogManager.closeDialog("orderPersonDialog");
                        },
                        onSubmit: (context, details, dialogManager, dialog) => {
                            const eventName = dialog.data.whenEventName || "peopleSelected";
                            dialogManager._dialogRepository.get(details.recipientDialog)
                                .communicationLane.send(eventName, details.selectedBundle);
                        }
                    })
                ],
                [
                    "orderRoomDialog",
                    new Dialog({
                        dialogElementId: "orderRoomDialog",
                        triggerElementId: "inspectEventDialog_addRoomsBtn",
                        triggerByEvent: true,
                        htmlFabricator: async (context) => {
                            return await this.dialogManager.loadDialogHtml({
                                url: '/arrangement/planner/dialogs/order_room',
                                managerName: 'eventInspector',
                                dialogId: 'orderRoomDialog',
                                customParameters: {
                                    event_pk: context.event.pk,
                                    recipientDialogId: context.lastTriggererDetails.sendTo,
                                }
                            });
                        },
                        onRenderedCallback: () => { },
                        dialogOptions: { 
                            width: 500,
                            dialogClass: 'no-titlebar',
                        },
                        onUpdatedCallback: () => { 
                            this.dialogManager.closeDialog("orderRoomDialog"); 
                        },
                        onSubmit: (context, details, dialogManager) => { 
                            dialogManager._dialogRepository.get(details.recipientDialog)
                                .communicationLane.send("roomsSelected", details.selectedBundle);
                        }
                    })
                ],
                [
                    "uploadFilesDialog",
                    new Dialog({
                        dialogElementId: "uploadFilesDialog",
                        triggerElementId: "eventDialog_uploadFilesBtn",
                        triggerByEvent: true,
                        htmlFabricator: async (context) => {
                            return await this.dialogManager.loadDialogHtml({
                                url: '/arrangement/planner/dialogs/upload_files_dialog',
                                dialogId: 'uploadFilesDialog',
                                managerName: 'eventInspector',
                            });
                        },
                        onRenderedCallback: (dialogInstance, context) => {},
                        dialogOptions: { 
                            width: 600, 
                            dialogClass: 'no-titlebar',
                        },
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
                        triggerByEvent: true,
                        htmlFabricator: async (context) => {
                            return await this.dialogManager.loadDialogHtml(
                                {
                                    url: '/arrangement/planner/dialogs/new_note',
                                    managerName: 'eventInspector',
                                    dialogId: 'newNoteDialog',
                                    customParameters: {
                                        pk: context.event.pk,
                                        entityType: "event",
                                    }
                                }
                            );
                        },
                        onRenderedCallback: () => { console.info("Rendered") },
                        onUpdatedCallback: () => {
                            this.dialogManager.reloadDialog("inspectEventDialog");
                            this.dialogManager.closeDialog("newNoteDialog");
                        },
                        onSubmit: async (context, details) => {
                            await fetch('/arrangement/note/post', {
                                method: 'POST',
                                body: Utils.convertObjToFormData(details),
                                credentials: 'same-origin',
                                headers: {
                                    "X-CSRFToken": details.csrf_token
                                }
                            }).then(response => console.log("response", response));
                        },
                        dialogOptions: { 
                            width: 500,
                            dialogClass: 'no-titlebar',
                        },
                    })
                ],
                [
                    "editNoteDialog",
                    new Dialog({
                        dialogElementId: "editNoteDialog",
                        triggerElementId: undefined,
                        triggerByEvent: true,
                        htmlFabricator: async (context) => {
                            return await this.dialogManager.loadDialogHtml(
                                {
                                    url: '/arrangement/planner/dialogs/edit_note/' + context.lastTriggererDetails.note_pk,
                                    managerName: 'eventInspector',
                                    dialogId: 'editNoteDialog',
                                }
                            );
                        },
                        onRenderedCallback: () => { console.info("Rendered"); },
                        onUpdatedCallback: () => {
                            this.dialogManager.reloadDialog("inspectEventDialog");
                            this.dialogManager.closeDialog("editNoteDialog");
                        },
                        onSubmit: async (context, details) => {
                            await fetch('/arrangement/planner/dialogs/edit_note/' + details.id, {
                                method: 'POST',
                                body: Utils.convertObjToFormData(details), 
                                headers: {
                                    'X-CSRFToken': details.csrf_token,
                                }
                            })
                        },
                        dialogOptions: { 
                            width: 500,
                            dialogClass: 'no-titlebar',
                        },
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