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
                        onRenderedCallback: () => { this.dialogManager._makeAware(); },
                        dialogOptions: { width: 600 },
                        onSubmit: async (context, details) => {
                            console.log("Context", context)
                            console.log("Details", details)
                            var pk = details.event_pk;

                            console.log("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOOOOOOOO")

                            await fetch('/arrangement/planner/update_event/113', {
                                method: "POST",
                                body: details.formData,
                                headers: {
                                    "X-CSRFToken": details.csrf_token
                                }
                            })
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