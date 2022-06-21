import { CollisionsUtil } from "./collisions_util.js";
import { convertObjToFormData } from "./commonLib.js";
import { Dialog, DialogManager } from "./dialog_manager/dialogManager.js";
import { PopulateCreateSerieDialogFromManifest } from "./form_populating_routines.js";
import { QueryStore } from "./querystore.js";


const MANAGER_NAME = "arrangementInspector"

const MAIN_DIALOG = Symbol("mainDialog")
const ADD_PLANNER_DIALOG = Symbol("addPlannerDialog")


export class ArrangementInspector {
    constructor () {
        this.dialogManager = this._createDialogManager();
    }

    async inspect( arrangement ) {
        this.dialogManager.setContext({ arrangement: arrangement });
        this.dialogManager.openDialog( "mainDialog" );
    }

    async _getRecurringInfo(arrangementPk) {
        return await fetch(`/arrangement/arrangement/${arrangementPk}/detail`).then( response => response.json() );
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

    async saveSerieWithCollisionResolutions (serie, csrf_token, arrangement_pk, collision_resolution_map) {
        var solutionEventFormDatas = [];

        for (var entry of collision_resolution_map) {
            var solution = entry[1].solution;

            if (solution === undefined) {
                continue;
            }

            solutionEventFormDatas.push(solution);
        }

        return await Promise.all([
            QueryStore.SaveSerie(serie, csrf_token, arrangement_pk),
            QueryStore.SaveEvents(solutionEventFormDatas, csrf_token),
        ])
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
                        dialogOptions: { width: 800, height: 800  }
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
                        onUpdatedCallback: ( ) => {
                            this.dialogManager.reloadDialog("mainDialog");
                            this.dialogManager.closeDialog("addPlannerDialog");
                            toastr.success("Planlegger(e) har blitt lagt til")
                        },
                        dialogOptions: { width: 700 }
                    })
                ],
                [
                    "uploadFilesToArrangementDialog",
                    new Dialog({
                        dialogElementId: "uploadFilesToArrangementDialog",
                        triggerElementId: "mainDialog__uploadFilesBtn",
                        htmlFabricator: async (context) => {
                            return await fetch("/arrangement/planner/dialogs/upload_files_to_arrangement?arrangement_slug=" + context.arrangement.slug)
                                .then(response => response.text());
                        },
                        onRenderedCallback: () => { console.info("Rendered"); },
                        onUpdatedCallback: () => { this.dialogManager.reloadDialog("mainDialog"); this.dialogManager.closeDialog("addPlannerDialog"); },
                        dialogOptions: { width: 400 }
                    })
                ],
                [
                    "uploadFilesToEventSerieDialog",
                    new Dialog({
                        dialogElementId: "uploadFilesToEventSerieDialog",
                        triggerElementId: undefined,
                        triggerByEvent: true,
                        htmlFabricator: async (context) => {
                            return await fetch("/arrangement/planner/dialogs/upload_files_to_event_serie?event_serie_pk=" + context.lastTriggererDetails.event_serie_pk)
                                .then(response => response.text());
                        },
                        onRenderedCallback: () => { console.info("Upload files to event serie dialog rendered") },
                        onUpdatedCallback: () => { this.dialogManager.reloadDialog("mainDialog"); this.dialogManager.closeDialog("uploadFilesToEventSerieDialog"); },
                        dialogOptions: { width: 400 },
                    })
                ],
                [
                    "newTimePlanDialog",
                    new Dialog({
                        dialogElementId: "newTimePlanDialog",
                        triggerElementId: "mainPlannerDialog__newTimePlan",
                        dialogElementId: "newTimePlanDialog",
                        htmlFabricator: async (context) => {
                            return await fetch("/arrangement/planner/dialogs/create_serie?slug=" + context.arrangement.slug + "&dialog=newTimePlanDialog&managerName=" + MANAGER_NAME + "&orderRoomDialog=nestedOrderRoomDialog&orderPersonDialog=nestedOrderPersonDialog")
                                .then(response => response.text());
                        },
                        onRenderedCallback: async (dialogManager, context) => {
                            var info = await this._getRecurringInfo( context.arrangement.arrangement_pk );
                            $('#serie_title').attr('value', info.title);
                            $('#serie_title_en').attr('value', info.title_en);
                            $('#serie_ticket_code').attr('value', info.ticket_code);
                            $('#serie_expected_visitors').attr('value', info.expected_visitors);

                            info.display_layouts.forEach(display_layout => {
                                $('#id_display_layouts_serie_planner_' + ( display_layout - 1))
                                    .prop( "checked", true );
                            })
                        },
                        onUpdatedCallback: () => {
                            this.dialogManager.reloadDialog("mainDialog");
                            this.dialogManager.closeDialog("newTimePlanDialog");
                        },
                        dialogOptions: { width: 700, modal:true },
                        onSubmit: async (context, details) => {
                            context.serie = details.serie;
                            context.collision_resolution = new Map();

                            var isInCollisionResolutionState = await CollisionsUtil.FireCollisionsSwal(
                                details.serie,
                                context.collision_resolution,
                                details.csrf_token,
                                "arrangementInspector.breakOutActivityDialog.trigger",
                                context.arrangement.arrangement_pk,
                                this.saveSerieWithCollisionResolutions,
                                () => { this.dialogManager.closeDialog("newTimePlanDialog") }
                            );

                            if (isInCollisionResolutionState) {
                                context.active_collision_route_parent_dialog_id = "newTimePlanDialog";
                                return false;
                            }

                            QueryStore.SaveSerie(details.serie, details.csrf_token, context.arrangement.arrangement_pk).then(_ => {
                                document.dispatchEvent(new Event("plannerCalendar.refreshNeeded"));
                            });
                        }
                    })
                ],
                [
                    "breakOutActivityDialog",
                    new Dialog({
                        dialogElementId: "breakOutActivityDialog",
                        triggerElementId: "breakOutActivityDialog",
                        triggerByEvent: true,
                        htmlFabricator: async (context) => {
                            return await fetch('/arrangement/planner/dialogs/create_simple_event?slug=0&managerName=arrangementInspector&dialog=breakOutActivityDialog&orderRoomDialog=orderRoomForLocalEventDialog&orderPersonDialog=orderPersonDialog&dialogTitle=Kollisjonshåndtering&dialogIcon=fa-code-branch')
                                .then(response => response.text());
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
                            context._lastTriggererDetails.serie = context.serie;
                            var serie = context.serie;

                            var collision_uuid = context._lastTriggererDetails.collision_uuid;
                            var resolution_bundle = context.collision_resolution.get(collision_uuid);
                            var collision_record = resolution_bundle.collision;

                            $('#ticket_code').val(serie.time.ticket_code).trigger('change');
                            $('#title').val(serie.time.title).trigger('change');
                            $('#title_en').attr('value', serie.time.title_en).trigger('change');
                            $('#expected_visitors').attr('value', serie.time.expected_visitors).trigger('change');

                            serie.display_layouts.split(",")
                                .forEach(checkboxElement => {
                                    $(`#${checkboxElement.value}_dlcheck`)
                                        .prop( "checked", true );
                                })

                            // document.querySelectorAll("input[name='display_layouts']:checked")
                            //     .forEach(checkboxElement => {
                            //         $(`#${checkboxElement.value}_dlcheck`)
                            //             .prop( "checked", true );
                            //     })

                            var splitDateFunc = function (strToDateSplit) {
                                var date_str = strToDateSplit.split("T")[0];
                                var time_str = new Date(strToDateSplit).toTimeString().split(' ')[0];
                                return [ date_str, time_str ];
                            }

                            var startTimeArtifacts = splitDateFunc(collision_record.event_a_start);
                            var endTimeArtifacts = splitDateFunc(collision_record.event_a_end);
                            $('#fromDate').val(startTimeArtifacts[0]).trigger('change');
                            $('#fromTime').val(startTimeArtifacts[1]).trigger('change');
                            $('#toDate').val(endTimeArtifacts[0]).trigger('change');
                            $('#toTime').val(endTimeArtifacts[1]).trigger('change');

                            // NOT USED This ensures that english title is only obligatory IF a display layout has been selected.
                            // dialogCreateEvent__evaluateEnTitleObligatory();

                            if (serie.people.length > 0) {
                                var peopleSelectContext = Object();
                                peopleSelectContext.people = serie.people.join(",");
                                peopleSelectContext.people_name_map = serie.people_name_map;
                                document.dispatchEvent(new CustomEvent(
                                    "arrangementInspector.d1_peopleSelected",
                                    { detail: {
                                        context: peopleSelectContext
                                    } }
                                ));
                            }
                            if (serie.rooms.length > 0) {
                                var roomSelectContext = Object();
                                roomSelectContext.rooms = serie.rooms.join(",");
                                roomSelectContext.room_name_map = serie.room_name_map;
                                document.dispatchEvent(new CustomEvent(
                                    "arrangementInspector.d1_roomsSelected",
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
                        onUpdatedCallback: async (context) => {
                        },
                        onSubmit: async (context, details) => {
                            context.csrf_token = details.csrf_token;

                            if (context.events === undefined) {
                                context.events = new Map();
                            }
                            if (details.event._uuid === undefined) {
                                details.event._uuid = crypto.randomUUID();
                            }

                            details.event.is_resolution = true;
                            details.event.associated_serie_internal_uuid = context._lastTriggererDetails.serie._uuid;

                            var collision_state = context.collision_resolution.get(context._lastTriggererDetails.collision_uuid);

                            details.event.fromDate = new Date(details.event.start).toISOString();
                            details.event.toDate = new Date(details.event.end).toISOString();
                            details.event.arrangement = context.arrangement.arrangement_pk;

                            var formData = new FormData();
                            for (var key in details.event) {
                                formData.append(key, details.event[key])
                            }

                            var collisions_on_solution = await CollisionsUtil.GetCollisionsForEvent(formData, details.csrf_token);

                            if (collisions_on_solution.length > 0) {
                                CollisionsUtil.FireOneToOneCollisionWarningSwal(collisions_on_solution[0])
                                    .then( async (_) => {
                                        await CollisionsUtil.FireCollisionsSwal(
                                            context.serie,
                                            context.collision_resolution,
                                            context.csrf_token,
                                            "arrangementInspector.breakOutActivityDialog.trigger",
                                            context.arrangement.arrangement_pk,
                                            this.saveSerieWithCollisionResolutions,
                                            () => { this.dialogManager.closeDialog(context.active_collision_route_parent_dialog_id); }
                                        )
                                        this.dialogManager.closeDialog("breakOutActivityDialog");
                                    } );

                                return false;
                            }

                            collision_state.collision.is_resolved = true;
                            collision_state.solution = details.event;

                            await CollisionsUtil.FireCollisionsSwal(
                                context.serie,
                                context.collision_resolution,
                                context.csrf_token,
                                "arrangementInspector.breakOutActivityDialog.trigger",
                                context.arrangement.arrangement_pk,
                                this.saveSerieWithCollisionResolutions,
                                () => { this.dialogManager.closeDialog(context.active_collision_route_parent_dialog_id); }

                            )

                            this.dialogManager.closeDialog("breakOutActivityDialog");

                            document.dispatchEvent(new CustomEvent(this.dialogManager.managerName + ".contextUpdated", { detail: { context: context } }))
                        },
                        dialogOptions: { width: 700 }
                    })
                ],
                [
                    "newSimpleActivityDialog",
                    new Dialog({
                        dialogElementId: "newSimpleActivityDialog",
                        triggerElementId: "mainPlannerDialog__newSimpleActivity",
                        htmlFabricator: async (context) => {
                            return await fetch('/arrangement/planner/dialogs/create_simple_event?slug=' + context.arrangement.slug + "&managerName=" + MANAGER_NAME + "&orderRoomDialog=nestedOrderRoomDialog&orderPersonDialog=nestedOrderPersonDialog&dialog=newSimpleActivityDialog")
                                .then(response => response.text());
                        },
                        onRenderedCallback: () => {
                            document.querySelectorAll('.form-outline').forEach((formOutline) => {
                                new mdb.Input(formOutline).init();
                            });
                        },
                        onUpdatedCallback: () => {
                            this.dialogManager.reloadDialog("mainDialog");
                            this.dialogManager.closeDialog("newSimpleActivityDialog");
                        },
                        dialogOptions: { width: 500 },
                        onSubmit: async (context, details) => {
                            details.event.startDate = (new Date(details.event.start)).toISOString();
                            details.event.endDate = (new Date(details.event.end)).toISOString();
                            details.event.arrangement = context.arrangement.arrangement_pk;
                            details.event.id = 0;

                            details.event.collisions = await CollisionsUtil.GetCollisionsForEvent(convertObjToFormData(details.event), details.csrf_token);

                            if (details.event.collisions.length > 0) {
                                CollisionsUtil.FireOneToOneCollisionWarningSwal(details.event.collisions[0]);
                                return false;
                            }

                            QueryStore.SaveEvents([ details.event ], details.csrf_token).then(_ => {
                                document.dispatchEvent(new Event("plannerCalendar.refreshNeeded"));
                            })
                        }
                    })
                ],
                [
                    "editEventSerieDialog",
                    new Dialog({
                        dialogElementId: "editEventSerieDialog",
                        customTriggerName: "editEventSerieDialog",
                        triggerElementId: undefined,
                        triggerByEvent: true,
                        htmlFabricator: async (context) => {
                            return await fetch("/arrangement/planner/dialogs/create_serie?managerName=arrangementInspector&dialog=editEventSerieDialog&orderRoomDialog=nestedOrderRoomDialog&orderPersonDialog=nestedOrderPersonDialog")
                                .then(response => response.text());
                        },
                        onRenderedCallback:  async (dialogManager, context) => {
                            var manifest = await fetch(`/arrangement/eventSerie/${context.lastTriggererDetails.event_serie_pk}/manifest`, {
                                method: "GET"
                            }).then(response => response.json())

                            PopulateCreateSerieDialogFromManifest(manifest, context.lastTriggererDetails.event_serie_pk);
                         },
                        onUpdatedCallback: () => {
                            this.dialogManager.reloadDialog("mainDialog");
                            this.dialogManager.closeDialog("editEventSerieDialog");
                        },
                        onSubmit: async (context, details) => {
                            details.serie.event_serie_pk = context.lastTriggererDetails.event_serie_pk;

                            context.serie = details.serie;
                            context.collision_resolution = new Map();

                            var isInCollisionResolutionState = await CollisionsUtil.FireCollisionsSwal(
                                details.serie,
                                context.collision_resolution,
                                details.csrf_token,
                                "arrangementInspector.breakOutActivityDialog.trigger",
                                context.arrangement.arrangement_pk,
                                this.saveSerieWithCollisionResolutions,
                                () => { this.dialogManager.closeDialog("editEventSerieDialog"); },
                            );

                            if (isInCollisionResolutionState) {
                                context.active_collision_route_parent_dialog_id = "editEventSerieDialog";
                                return false;
                            }

                            return QueryStore.SaveSerie(details.serie, details.csrf_token, context.arrangement.arrangement_pk).then(_ => {
                                document.dispatchEvent(new Event("plannerCalendar.refreshNeeded"));
                            });
                        },
                        dialogOptions: { width: 700 }
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
                        onUpdatedCallback: () => {
                            this.dialogManager.reloadDialog("mainDialog");
                            this.dialogManager.closeDialog("promotePlannerDialog");
                        },
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
                        onUpdatedCallback: () => {
                            this.dialogManager.reloadDialog("mainDialog");
                            this.dialogManager.closeDialog("newNoteDialog");
                        },
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
                            return await fetch(`/arrangement/planner/dialogs/order_person?serie_guid=${context.serie.guid}&manager=arrangementInspector&dialog=orderPersonDialog`)
                                .then(response => response.text());
                        },
                        onRenderedCallback: () => { this.dialogManager._makeAware(); },
                        dialogOptions: { width: 500 },
                        onSubmit: async (context, details) => {
                            fetch("/arrangement/planner/dialogs/order_people_form", {
                                method: "POST",
                                body: details.formData,
                                headers: {
                                    "X-CSRFToken": details.csrf_token
                                }
                            }).then(_ => {
                                this.dialogManager.reloadDialog("mainDialog");
                                this.dialogManager.closeDialog("orderPersonDialog");
                            });
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
                            return await fetch("/arrangement/planner/dialogs/order_room?serie_guid=" + context.serie.guid + "&manager=arrangementInspector&dialog=orderRoomDialog")
                                .then(response => response.text());
                        },
                        onRenderedCallback: () => { this.dialogManager._makeAware(); },
                        dialogOptions: { width: 500 },
                        onUpdatedCallback: () => {
                            this.dialogManager.reloadDialog("mainDialog");
                            this.dialogManager.closeDialog("orderRoomDialog");
                        },
                        onSubmit: async (context, details) => {
                            fetch("/arrangement/planner/dialogs/order_rooms_form", {
                                method: "POST",
                                body: details.formData,
                                headers: {
                                    "X-CSRFToken": details.csrf_token
                                }
                            }).then(_ => {
                                this.dialogManager.reloadDialog("mainDialog");
                                this.dialogManager.closeDialog("orderRoomDialog");
                            });
                        }
                    })
                ],
                [
                    "orderRoomForLocalEventDialog",
                    new Dialog({
                        dialogElementId: "orderRoomForLocalEventDialog",
                        triggerElementId: undefined,
                        triggerByEvent: true,
                        htmlFabricator: async (context) => {
                            return await fetch(`/arrangement/planner/dialogs/order_room?event_pk=0&manager=${MANAGER_NAME}&dialog=orderRoomForLocalEventDialog`)
                                .then(response => response.text());
                        },
                        onRenderedCallback: () => {},
                        dialogOptions: { width: 500 },
                        onUpdatedCallback: () => {
                            toastr.success("Rom lagt til");
                            this.dialogManager.closeDialog("orderRoomForLocalEventDialog");
                        },
                        onSubmit: (context, details) => {
                            context.rooms = details.formData.get("room_ids");
                            context.room_name_map = details.room_name_map;

                            document.dispatchEvent(new CustomEvent(
                                `${MANAGER_NAME}.d1_roomsSelected`,
                                { detail: { context: context } }
                            ));
                        }
                    })
                ],
                [
                    "orderRoomForOneEventDialog",
                    new Dialog({
                        dialogElementId: "orderRoomForOneEventDialog",
                        triggerElementId: undefined,
                        triggerByEvent: true,
                        htmlFabricator: async (context) => {
                            return await fetch(`/arrangement/planner/dialogs/order_room?event_pk=${context.event.pk}&manager=arrangementInspector&dialog=orderRoomForOneEventDialog`)
                                .then(response => response.text());
                        },
                        onRenderedCallback: () => { this.dialogManager._makeAware(); },
                        onUpdatedCallback: () => { this.dialogManager.reloadDialog("mainDialog"); },
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
                        dialogElementId: "orderPersonForOneEventDialog",
                        triggerElementId: undefined,
                        triggerByEvent: true,
                        htmlFabricator: async (context) => {
                            return await fetch(`/arrangement/planner/dialogs/order_person?event_pk=${context.event.pk}&manager=arrangementInspector&dialog=orderPersonForOneEventDialog`)
                                .then(response => response.text());
                        },
                        onRenderedCallback: () => { this.dialogManager._makeAware(); },
                        dialogOptions: { width: 500 },
                        onUpdatedCallback: () => { this.dialogManager.reloadDialog("mainDialog"); },
                        onSubmit: async (context, details) => {
                            fetch("/arrangement/planner/dialogs/order_people_for_event_form", {
                                method: "POST",
                                body: details.formData,
                                headers: {
                                    "X-CSRFToken": details.csrf_token
                                }
                            }).then(_ => { this.dialogManager.reloadDialog("mainDialog"); this.dialogManager.closeDialog("orderPersonForOneEventDialog"); });;
                        }
                    })
                ],
                [
                    "nestedOrderRoomDialog",
                    new Dialog({
                        dialogElementId: "nestedOrderRoomDialog",
                        triggerElementId: undefined,
                        triggerByEvent: true,
                        htmlFabricator: async (context) => {
                            return await fetch(`/arrangement/planner/dialogs/order_room?event_pk=0&manager=arrangementInspector&dialog=nestedOrderRoomDialog`)
                                .then(response => response.text());
                        },
                        onRenderedCallback: () => { },
                        dialogOptions: { width: 500 },
                        onUpdatedCallback: () => {
                            this.dialogManager.closeDialog("nestedOrderRoomDialog");
                            toastr.success("Rom har blitt lagt til");
                        },
                        onSubmit: (context, details) => {
                            context.rooms = details.formData.get("room_ids");
                            context.room_name_map = details.room_name_map;

                            document.dispatchEvent(new CustomEvent(
                                `arrangementInspector.d1_roomsSelected`,
                                { detail: { context: context } }
                            ));
                            document.dispatchEvent(new CustomEvent(
                                `arrangementInspector.d2_roomsSelected`,
                                { detail: { context: context } }
                            ));
                        }
                    })
                ],
                [
                    "nestedOrderPersonDialog",
                    new Dialog({
                        dialogElementId: "nestedOrderPersonDialog",
                        triggerElementId: undefined,
                        triggerByEvent: true,
                        htmlFabricator: async (context) => {
                            return await fetch(`/arrangement/planner/dialogs/order_person?event_pk=0&manager=arrangementInspector&dialog=nestedOrderPersonDialog&orderRoomDialog=orderRoomDialog&orderPersonDialog=orderPersonDialog`)
                            .then(response => response.text());
                        },
                        onRenderedCallback: () => { },
                        dialogOptions: { width: 500 },
                        onUpdatedCallback: () => {
                            this.dialogManager.closeDialog("nestedOrderPersonDialog");
                            toastr.success("Personer har blitt lagt til");
                        },
                        onSubmit: (context, details) => {
                            var people_ids = details.formData.get("people_ids");
                            context.people = people_ids;
                            context.people_name_map = details.people_name_map;

                            document.dispatchEvent(new CustomEvent(
                                "arrangementInspector.d1_peopleSelected",
                                { detail: {
                                    context: context
                                } }
                            ));
                            document.dispatchEvent(new CustomEvent(
                                "arrangementInspector.d2_peopleSelected",
                                { detail: {
                                    context: context
                                } }
                            ));
                        }
                    })
                ]
            ]}
        )
    }
}
