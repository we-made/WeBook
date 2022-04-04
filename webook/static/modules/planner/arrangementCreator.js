import { DialogManager, Dialog } from "./dialog_manager/dialogManager.js";
import { SeriesUtil } from "./seriesutil.js"


export class ArrangementCreator {
    constructor () {
        this.dialogManager = new DialogManager({
            managerName: "arrangementCreator",  
            dialogs: [
                [
                    "createArrangementDialog",
                    new Dialog({
                        dialogElementId: "createArrangementDialog",
                        triggerElementId: "_createArrangementDialog",
                        htmlFabricator: async (context) => {
                            return await fetch('/arrangement/planner/dialogs/create_arrangement?managerName=arrangementCreator')
                                    .then(response => response.text());
                        },
                        onPreRefresh: (dialog) => {
                            dialog._active_tab = active;
                        },
                        onRenderedCallback: (dialog) => {
                            if (this.dialogManager.context.series !== undefined) {
                                this.dialogManager.context.series = [];
                            }
                            this.dialogManager._makeAware();
                        },
                        onSubmit: async (context, details) => { 
                            var csrf_token = details.formData.get("csrf_token");
                            var createArrangement = async function (formData, csrf_token) {
                                console.log(csrf_token)
                                var response = await fetch("/arrangement/arrangement/ajax/create", {
                                    method: 'POST',
                                    body: formData,
                                    headers: {
                                        "X-CSRFToken": csrf_token
                                    },
                                    credentials: 'same-origin',
                                });

                                var json = await response.text();
                                console.log(json)
                                var obj = JSON.parse(json);
                                console.log(obj);
                                return obj.arrangementPk;
                            };
                            var registerSerie = async function (serie, arrangementId, csrf_token) {
                                var events = SeriesUtil.calculate_serie(serie);
                                var formData = new FormData();

                                console.log(arrangementId)

                                for (let i = 0; i < events.length; i++) {
                                    var event = events[i];
                                    event.arrangement=arrangementId;
                                    event.start = event.from.toISOString();
                                    event.end=event.to.toISOString();

                                    for (var key in event) {
                                        formData.append("events[" + i + "]." + key, event[key]);
                                    }
                                }

                                await fetch("/arrangement/planner/create_events/", {
                                    method:"POST",
                                    body: formData,
                                    headers: {
                                        "X-CSRFToken": csrf_token
                                    },
                                    credentials: 'same-origin',
                                }).then(_ => { 
                                    document.dispatchEvent(new Event("plannerCalendar.refreshNeeded"));
                                })
                            }

                            createArrangement(details.formData, csrf_token)
                                .then(arrId => {
                                    details.series.forEach(async (serie) => {
                                        await registerSerie(serie, arrId, csrf_token);
                                    });
                                });
                        },
                        onUpdatedCallback: () => { this.reloadDialog("createArrangementDialog"); },
                        dialogOptions: { width: 600 }
                    }),
                ],
                [
                    "newTimePlanDialog",
                    new Dialog({
                        dialogElementId: "newTimePlanDialog",
                        triggerElementId: "createArrangementDialog_createSerie",
                        htmlFabricator: async (context) => {
                            return await fetch("/arrangement/planner/dialogs/create_serie?managerName=arrangementCreator")
                                .then(response => response.text());
                        },
                        onRenderedCallback: () => { console.info("Rendered"); },
                        onUpdatedCallback: () => { this.reloadDialog("mainDialog"); this.closeDialog("newTimePlanDialog"); },
                        onSubmit: async (context, details) => {
                            console.log("newTimePlanDialog >> onSubmit")
                            if (context.series === undefined) {
                                context.series = []
                            }
                            context.series.push(details.serie);
                            console.log(this.dialogManager.managerName + ".contextUpdated")
                            console.log(context);
                            document.dispatchEvent(new CustomEvent(this.dialogManager.managerName + ".contextUpdated", { detail: { context: context } }))
                        },
                        dialogOptions: { width: 700 }
                    })
                ],
            ]            
        })
    }

    open() {
        this.dialogManager.openDialog( "createArrangementDialog" );
    }    
}