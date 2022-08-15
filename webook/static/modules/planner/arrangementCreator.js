import { CollisionsUtil } from "./collisions_util.js";
import { Dialog, DialogManager } from "./dialog_manager/dialogManager.js";
import { PopulateCreateEventDialog, PopulateCreateSerieDialogFromSerie } from "./form_populating_routines.js";
import { QueryStore } from "./querystore.js";
import { serieConvert } from "./serieConvert.js";
import { SerieMetaTranslator } from "./serie_meta_translator.js";


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
                            return this.dialogManager.loadDialogHtml({
                                url: '/arrangement/planner/dialogs/create_arrangement',
                                dialogId: "createArrangementDialog",
                                managerName: "arrangementCreator",
                            });
                        },
                        onPreRefresh: (dialog) => {
                            dialog._active_tab = active;
                        },
                        onRenderedCallback: (dialog) => {
                            if (this.dialogManager.context.series !== undefined) {
                                this.dialogManager.context.series = new Map();
                            }
                            if (this.dialogManager.context.events !== undefined) {
                                this.dialogManager.context.events = new Map();
                            }

                            this.dialogManager._makeAware();
                        },
                        onSubmit: async (context, details) => {
                            let csrf_token = details.formData.get("csrf_token");

                            await fetch("/arrangement/arrangement/ajax/create", {
                                method: 'POST',
                                body: details.formData,
                                headers: {
                                    "X-CSRFToken": csrf_token
                                },
                                credentials: 'same-origin',
                            }).then(async response => await response.json())
                              .then(async (arrId) => {
                                for (let serie of details.series) {
                                    await QueryStore.SaveSerie(
                                        serie,
                                        csrf_token,
                                        arrId.arrangementPk,
                                    );
                                }
                                
                                if (details.events !== undefined) {
                                    details.events.forEach((event) => event.arrangement = arrId.arrangementPk);
                                    await QueryStore.SaveEvents(details.events, csrf_token);
                                }
                              })
                              .then(_ => {
                                document.dispatchEvent(new Event("plannerCalendar.refreshNeeded"));
                              });
                        },
                        onUpdatedCallback: () => {
                            toastr.success("Arrangement opprettet");
                            this.dialogManager.closeDialog("createArrangementDialog");
                        },
                        dialogOptions: { width: 900 }
                    }),
                ],
                [
                    "newTimePlanDialog",
                    new Dialog({
                        dialogElementId: "newTimePlanDialog",
                        triggerElementId: "createArrangementDialog_createSerie",
                        triggerByEvent: true,
                        htmlFabricator: async (context) => {
                            return await fetch("/arrangement/planner/dialogs/create_serie?managerName=arrangementCreator&dialog=newTimePlanDialog&orderRoomDialog=orderRoomDialog&orderPersonDialog=orderPersonDialog")
                                .then(response => response.text());
                        },
                        onRenderedCallback: (dialogManager, context) => {
                            if (context.lastTriggererDetails === undefined) {
                                let $thisDialog = this.dialogManager.$getDialogElement("newTimePlanDialog");
                                let $mainDialog = this.dialogManager.$getDialogElement("createArrangementDialog");

                                $thisDialog.find('#serie_ticket_code')
                                    .attr('value', $mainDialog.find('#id_ticket_code')[0].value);
                                $thisDialog.find('#serie_title')
                                    .attr('value', $mainDialog.find('#id_name')[0].value);
                                $thisDialog.find('#serie_title_en')
                                    .attr('value', $mainDialog.find('#id_name_en')[0].value);
                                $thisDialog.find('#serie_expected_visitors')
                                    .attr('value', $mainDialog.find('#id_expected_visitors')[0].value);

                                document.querySelectorAll("#createArrangementDialog input[name='display_layouts']:checked")
                                    .forEach(checkboxElement => {
                                        $thisDialog.find('#id_display_layouts_serie_planner_' + checkboxElement.value)
                                            .prop( "checked", true );
                                    })

                                $thisDialog.find('#serie_uuid').val(crypto.randomUUID());

                                document.querySelectorAll('.form-outline').forEach((formOutline) => {
                                    new mdb.Input(formOutline).init();
                                });
                            }
                            else {
                                if (context.series !== undefined) {
                                    let serie = context.series.get(context.lastTriggererDetails.serie_uuid);
                                    PopulateCreateSerieDialogFromSerie(serie);
                                }
                            }
                            
                            document.querySelectorAll('.form-outline').forEach((formOutline) => {
                                new mdb.Input(formOutline).init();
                            });
                        },
                        onUpdatedCallback: () => {
                            toastr.success("Tidsplan lagt til eller oppdatert i planen");
                            this.dialogManager.closeDialog("newTimePlanDialog");
                        },
                        onSubmit: async (context, details) => {
                            details.serie.friendlyDesc = SerieMetaTranslator.generate(details.serie);

                            if (context.series === undefined) {
                                context.series = new Map();
                            }
                            if (details.serie._uuid === undefined) {
                                details.serie._uuid = crypto.randomUUID();
                            }

                            details.serie.collisions = await CollisionsUtil.GetCollisionsForSerie(serieConvert(details.serie, new FormData(), ""), details.csrf_token);
                            context.series.set(details.serie._uuid, details.serie);
                            document.dispatchEvent(new CustomEvent(this.dialogManager.managerName + ".contextUpdated", { detail: { context: context } }))
                        },
                        dialogOptions: { width: 700 }
                    })
                ],
                [
                    "breakOutActivityDialog",
                    new Dialog({
                        dialogElementId: "breakOutActivityDialog",
                        triggerElementId: "breakOutActivityDialog",
                        triggerByEvent: true,
                        htmlFabricator: async (context) => {
                            return this.dialogManager.loadDialogHtml({
                                url: "/arrangement/planner/dialogs/create_simple_event",
                                dialogId: "breakOutActivityDialog",
                                managerName: "arrangementCreator",
                                customParameters: {
                                    slug: 0,
                                    orderPersonDialog: "orderPersonDialog",
                                    orderRoomDialog: "orderRoomDialog",
                                }
                            })
                        },
                        onRenderedCallback: (dialogManager, context) => {
                            /*
                                LastTriggererDetails is set when the dialog is called for, and not available
                                in the subsequent callbacks versions of the context. We need to access this in
                                the OnSubmit callback so we set it as such. It might be more correct in the long
                                run to make this remembered for the entire lifetime of the dialog instance, as to avoid
                                these kinds of things.
                            */
                            context._lastTriggererDetails = context.lastTriggererDetails;

                            let serie = context.lastTriggererDetails.serie;
                            let collisionRecord = serie.collisions[context.lastTriggererDetails.collision_index];

                            $('#ticket_code').val(serie.time.ticket_code).trigger('change');
                            $('#title').val(serie.time.title).trigger('change');
                            $('#title_en').attr('value', serie.time.title_en).trigger('change');
                            $('#expected_visitors').attr('value', serie.time.expected_visitors).trigger('change');

                            serie.display_layouts.split(",")
                                .forEach(checkboxElement => {
                                    $(`#${checkboxElement.value}_dlcheck`)
                                        .prop( "checked", true );
                                })

                            $('#breakOutActivityDialog').prepend( $(
                                document.querySelector('.conflict_summary_'  + context.lastTriggererDetails.collision_index).outerHTML
                            ).addClass("mb-4"));

                            let { fromDate, fromTime }  = Utils.splitDateFunc(collisionRecord.event_a_start);
                            let { toDate, toTime }      = Utils.splitDateFunc(collisionRecord.event_a_end);

                            $('#fromDate').val(fromDate).trigger('change');
                            $('#fromTime').val(fromTime).trigger('change');
                            $('#toDate').val(toDate).trigger('change');
                            $('#toTime').val(toTime).trigger('change');

                            if (serie.people.length > 0) {
                                let peopleSelectContext = Object();
                                peopleSelectContext.people = serie.people.join(",");
                                peopleSelectContext.people_name_map = serie.people_name_map;
                                document.dispatchEvent(new CustomEvent(
                                    "arrangementCreator.d1_peopleSelected",
                                    { detail: {
                                        context: peopleSelectContext
                                    } }
                                ));
                            }
                            if (serie.rooms.length > 0) {
                                let roomSelectContext = Object();
                                roomSelectContext.rooms = serie.rooms.join(",");
                                roomSelectContext.room_name_map = serie.room_name_map;
                                document.dispatchEvent(new CustomEvent(
                                    "arrangementCreator.d1_roomsSelected",
                                    { detail: {
                                        context: roomSelectContext
                                    } }
                                ));
                            }

                            $('#event_uuid').val(crypto.randomUUID());
                            document.querySelectorAll('.form-outline').forEach((formOutline) => {
                                new mdb.Input(formOutline).init();
                            });
                        },
                        onUpdatedCallback: () => {
                            toastr.success("Kollisjon løst, enkel aktivitet har blitt opprettet");
                            this.dialogManager.closeDialog("breakOutActivityDialog");
                        },
                        onSubmit: async (context, details) => {
                            if (context.events === undefined) {
                                context.events = new Map();
                            }
                            if (details.event._uuid === undefined) {
                                details.event._uuid = crypto.randomUUID();
                            }

                            details.event.is_resolution = true;
                            details.event.associated_serie_internal_uuid = context._lastTriggererDetails.serie._uuid;

                            let formData = new FormData();
                            for (let key in details.event) {
                                formData.append(key, details.event[key])
                            }

                            let startDate = new Date(details.event.start);
                            let endDate = new Date(details.event.end);
                            formData.append("fromDate", startDate.toISOString());
                            formData.append("toDate", endDate.toISOString());

                            details.event.collisions = await CollisionsUtil.GetCollisionsForEvent(formData, details.csrf_token);

                            if (details.event.collisions.length > 0) {
                                let collision = details.event.collisions[0];
                                await CollisionsUtil.FireOneToOneCollisionWarningSwal(collision);

                                return false;
                            }

                            context._lastTriggererDetails.serie.collisions
                                .splice(context._lastTriggererDetails.collision_index, 1);

                            context.events.set(details.event._uuid, details.event);
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
                        triggerByEvent: true,
                        htmlFabricator: async (context) => {
                            return await this.dialogManager.loadDialogHtml({
                                url: "/arrangement/planner/dialogs/create_simple_event",
                                dialogId: "newSimpleActivityDialog",
                                managerName: "arrangementCreator",
                                customParameters: {
                                    slug: 0,
                                    orderPersonDialog: "orderPersonDialog",
                                    orderRoomDialog: "orderRoomDialog",
                                }
                            });
                        },
                        onRenderedCallback: (dialogManager, context) => {
                            document.querySelectorAll('.form-outline').forEach((formOutline) => {
                                new mdb.Input(formOutline).init();
                            });

                            if (context.lastTriggererDetails === undefined) {
                                let $mainDialog = this.dialogManager.$getDialogElement("createArrangementDialog");
                                let $simpleActivityDialog = this.dialogManager.$getDialogElement("newSimpleActivityDialog");

                                $simpleActivityDialog.find('#ticket_code').attr('value',         $mainDialog.find('#id_ticket_code').val() );
                                $simpleActivityDialog.find('#title').attr('value',               $mainDialog.find('#id_name').val() );
                                $simpleActivityDialog.find('#title_en').attr('value',            $mainDialog.find('#id_name_en').val() );
                                $simpleActivityDialog.find('#expected_visitors').attr('value',   $mainDialog.find('#id_expected_visitors').val() );

                                document.querySelectorAll("#createArrangementDialog input[name='display_layouts']:checked")
                                    .forEach(checkboxElement => {
                                        $simpleActivityDialog.find(`#${checkboxElement.value}_dlcheck`)
                                            .prop( "checked", true );
                                    })

                                $simpleActivityDialog.find('#event_uuid').val(crypto.randomUUID());

                                return;
                            }
                            
                            PopulateCreateEventDialog(context.events.get(context.lastTriggererDetails.event_uuid));

                            document.querySelectorAll('.form-outline').forEach((formOutline) => {
                                new mdb.Input(formOutline).init();
                            });
                        },
                        onUpdatedCallback: () => {
                            toastr.success("Enkel aktivitet lagt til eller oppdatert i planen");
                            this.dialogManager.closeDialog("newSimpleActivityDialog");
                        },
                        onSubmit: async (context, details) => {
                            if (context.events === undefined) {
                                context.events = new Map();
                            }
                            if (details.event._uuid === undefined) {
                                details.event._uuid = crypto.randomUUID();
                            }

                            let formData = new FormData();
                            for (let key in details.event) {
                                formData.append(key, details.event[key])
                            }

                            let startDate = new Date(details.event.start);
                            let endDate = new Date(details.event.end);
                            formData.append("fromDate", startDate.toISOString());
                            formData.append("toDate", endDate.toISOString());

                            details.event.collisions = await CollisionsUtil.GetCollisionsForEvent(formData, details.csrf_token);

                            if (details.event.collisions.length > 0) {
                                let collision = details.event.collisions[0];
                                await CollisionsUtil.FireOneToOneCollisionWarningSwal(collision);
                                return false;
                            }

                            context.events.set(details.event._uuid, details.event);
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
                            return await this.dialogManager.loadDialogHtml({
                                url: '/arrangement/planner/dialogs/order_room',
                                dialogId: 'orderRoomDialog',
                                managerName: 'arrangementCreator',
                                customParameters: {
                                    event_pk: 0
                                }
                            })
                        },
                        onRenderedCallback: () => { },
                        dialogOptions: { width: 500 },
                        onUpdatedCallback: () => {
                            toastr.success("Rom lagt til");
                            this.dialogManager.closeDialog("orderRoomDialog");
                        },
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
                            return this.dialogManager.loadDialogHtml({
                                url: '/arrangement/planner/dialogs/order_person',
                                managerName: 'arrangementCreator',
                                dialogId: 'orderPersonDialog',
                                customParameters: {
                                    event_pk: 0
                                }
                            });
                        },
                        onRenderedCallback: () => { },
                        dialogOptions: { width: 500 },
                        onUpdatedCallback: () => {
                            toastr.success("Personer lagt til");
                            this.dialogManager.closeDialog("orderPersonDialog");
                        },
                        onSubmit: (context, details) => {
                            let people_ids = details.formData.get("people_ids");
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
