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
                                var response = await fetch("/arrangement/arrangement/ajax/create", {
                                    method: 'POST',
                                    body: formData,
                                    headers: {
                                        "X-CSRFToken": csrf_token
                                    },
                                    credentials: 'same-origin',
                                });

                                var json = await response.text();
                                var obj = JSON.parse(json);
                                return obj.arrangementPk;
                            };

                            var registerEvents = async function (events, arrangementId, csrf_token, ticket_code) {
                                var formData = new FormData();
                                for (let i = 0; i < events.length; i++) {
                                    var event = events[i];
                                    event.arrangement = arrangementId;
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

                            var registerSerie = async function (serie, arrangementId, csrf_token, ticket_code) {
                                var events = SeriesUtil.calculate_serie(serie);
                                var formData = new FormData();

                                for (let i = 0; i < events.length; i++) {
                                    var event = events[i];
                                    event.arrangement=arrangementId;
                                    event.start = event.from.toISOString();
                                    event.end=event.to.toISOString();
                                    event.ticket_code = ticket_code;
                                    event.expected_visitors = serie.time.expected_visitors;
                                    event.rooms = serie.rooms;
                                    event.people = serie.people;
                                    
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
                                        await registerSerie(serie, arrId, csrf_token, details.formData.get("ticket_code"));
                                    });
                                    
                                    if (details.events !== undefined) {
                                        registerEvents(details.events, arrId, csrf_token, details.formData.get("ticked_code"));
                                    }
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
                            return await fetch("/arrangement/planner/dialogs/create_serie?managerName=arrangementCreator&dialog=newTimePlanDialog&orderRoomDialog=orderRoomDialog&orderPersonDialog=orderPersonDialog")
                                .then(response => response.text());
                        },
                        onRenderedCallback: () => { 
                            $('#serie_ticket_code').attr('value', $('#id_ticket_code')[0].value );
                            $('#serie_title').attr('value', $('#id_name')[0].value );
                            $('#serie_title_en').attr('value', $('#id_name_en')[0].value );
                            $('#serie_expected_visitors').attr('value', $('#id_expected_visitors')[0].value );

                        },
                        onUpdatedCallback: () => { this.reloadDialog("mainDialog"); this.closeDialog("newTimePlanDialog"); },
                        onSubmit: async (context, details) => {
                            if (context.series === undefined) {
                                context.series = []
                            }
                            context.series.push(details.serie);
                            document.dispatchEvent(new CustomEvent(this.dialogManager.managerName + ".contextUpdated", { detail: { context: context } }))
                        },
                        dialogOptions: { width: 700 }
                    })
                ],
                [
                    "newSimpleActivityDialog",
                    new Dialog({
                        dialogElementId: "newSimpleActivityDialog",
                        triggerElementId: "createArrangementDialog_createSimpleActivity",
                        htmlFabricator: async (context) => {
                            return await fetch('/arrangement/planner/dialogs/create_simple_event?slug=0&managerName=arrangementCreator&dialog=newSimpleActivityDialog&orderRoomDialog=orderRoomDialog&orderPersonDialog=orderPersonDialog')
                                .then(response => response.text());
                        },
                        onRenderedCallback: () => { 
                            $('#ticket_code').attr('value', $('#id_ticket_code')[0].value );
                            $('#title').attr('value', $('#id_name')[0].value );
                            $('#title_en').attr('value', $('#id_name_en')[0].value );
                            $('#expected_visitors').attr('value', $('#id_expected_visitors')[0].value );
                        },
                        onUpdatedCallback: () => { this.reloadDialog("mainDialog"); this.closeDialog("newSimpleActivityDialog"); },
                        onSubmit: async (context, details) => {
                            if (context.events === undefined) {
                                context.events = [];
                            }
                            context.events.push(details.event);
                            document.dispatchEvent(new CustomEvent(this.dialogManager.managerName + ".contextUpdated", { detail: { context: context } }))
                        },
                        dialogOptions: { width: 700 }
                    })
                ],
                [
                    "orderRoomDialog",
                    new Dialog({
                        dialogElementId: "orderRoomDialog",
                        triggerElementId: undefined,
                        triggerByEvent: true,
                        htmlFabricator: async (context) => {
                            return await fetch(`/arrangement/planner/dialogs/order_room?event_pk=0&manager=arrangementCreator&dialog=orderRoomDialog`)
                                .then(response => response.text());
                        },
                        onRenderedCallback: () => { },
                        dialogOptions: { width: 500 },
                        onUpdatedCallback: () => {  },
                        onSubmit: (context, details) => { 
                            context.rooms = details.formData.get("room_ids");
                            context.room_name_map = details.room_name_map;
                            
                            document.dispatchEvent(new CustomEvent(
                                `arrangementCreator.d1_roomsSelected`, 
                                { detail: { context: context } }
                            ));
                            document.dispatchEvent(new CustomEvent(
                                `arrangementCreator.d2_roomsSelected`, 
                                { detail: { context: context } }
                            ));
                        }
                    })
                ],
                [
                    "orderPersonDialog",
                    new Dialog({
                        dialogElementId: "orderPersonDialog",
                        triggerElementId: undefined,
                        triggerByEvent: true,
                        htmlFabricator: async (context) => {
                            return await fetch(`/arrangement/planner/dialogs/order_person?event_pk=0&manager=arrangementCreator&dialog=orderPersonDialog`)
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
                                "arrangementCreator.d1_peopleSelected",
                                { detail: {
                                    context: context
                                } }
                            ));
                            document.dispatchEvent(new CustomEvent(
                                "arrangementCreator.d2_peopleSelected",
                                { detail: {
                                    context: context
                                } }
                            ));
                        }
                    })
                ]
            ]            
        })
    }

    open() {
        this.dialogManager.openDialog( "createArrangementDialog" );
    }    
}