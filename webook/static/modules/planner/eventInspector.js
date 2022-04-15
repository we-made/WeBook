import { Dialog, DialogManager } from "./dialog_manager/dialogManager.js";

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
                            this._listenToAddPeople();
                            this._listenToAddRooms();
                        },
                        dialogOptions: { width: 600 },
                        onSubmit: async (context, details) => {
                            await fetch('/arrangement/planner/update_event/' + context.event.pk, {
                                method: "POST",
                                body: details.formData,
                                headers: {
                                    "X-CSRFToken": details.csrf_token
                                }
                            })
                        }
                    }),
                ],
                [
                    "orderPersonDialog",
                    new Dialog({
                        dialogElementId: "orderPersonDialog",
                        triggerElementId: "inspectEventDialog_addPeopleBtn",
                        htmlFabricator: async (context) => {
                            return await fetch("/arrangement/planner/dialogs/order_person?event_pk=" + context.event.pk)
                                .then(response => response.text());
                        },
                        onRenderedCallback: () => { this.dialogManager._makeAware(); },
                        dialogOptions: { width: 500 },
                        onUpdatedCallback: () => {  },
                    })
                ],
                [
                    "orderRoomDialog",
                    new Dialog({
                        dialogElementId: "orderRoomDialog",
                        triggerElementId: "inspectEventDialog_addRoomsBtn",
                        htmlFabricator: async (context) => {
                            return await fetch("/arrangement/planner/dialogs/order_room?event_pk=" + context.event.pk)
                                .then(response => response.text());
                        },
                        onRenderedCallback: () => { this.dialogManager._makeAware(); },
                        dialogOptions: { width: 500 },
                        onUpdatedCallback: () => {  },
                    })
                ]
            ]            
        })
    }

    _listenToAddPeople() {
        $('#inspectEventDialog_addPeopleBtn').on('click', () => {
            console.log(this.dialogManager)
            this.dialogManager.openDialog( "orderPersonDialog" );
        })
    }

    _listenToAddRooms() {
        $('#inspectEventDialog_addRoomsBtn').on('click', () => {
            this.dialogManager.openDialog( "orderRoomDialog" );
        })
    }

    inspect(pk) {
        this.dialogManager.setContext({ event: { pk: pk } });
        this.dialogManager.openDialog( "inspectEventDialog" );
    }    
}