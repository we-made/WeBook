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
                        },
                        dialogOptions: { width: 600, height: 700 },
                        onUpdatedCallback: () => {
                            this.dialogManager.closeDialog("inspectEventDialog");
                        },
                        onSubmit: async (context, details) => {
                            var url = '/arrangement/planner/update_event/' + context.event.pk;
                            await fetch(url, {
                                method: "POST",
                                body: details.formData,
                                headers: {
                                    "X-CSRFToken": details.csrf_token
                                }
                            }).then(_ => document.dispatchEvent(new Event("plannerCalendar.refreshNeeded")));
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
                        onUpdatedCallback: () => {  },
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
                        onUpdatedCallback: () => { this.dialogManager.closeDialog("orderRoomDialog"); },
                        onSubmit: (context, details) => { 
                            context.rooms = details.formData.get("room_ids");
                            context.room_name_map = details.room_name_map;
                            
                            document.dispatchEvent(new CustomEvent("eventInspector.roomsUpdated", { detail: { context: context } }))
                        }
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