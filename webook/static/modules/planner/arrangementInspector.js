import { CollisionsUtil } from "./collisions_util.js";
import { convertObjToFormData } from "./commonLib.js";
import { Dialog, DialogManager } from "./dialog_manager/dialogManager.js";
import { PopulateCreateSerieDialogFromManifest } from "./form_populating_routines.js";
import { QueryStore } from "./querystore.js";


const MANAGER_NAME = "arrangementInspector"


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
        let solutionEventFormDatas = [];

        for (let entry of collision_resolution_map) {
            let solution = entry[1].solution;

            if (solution === undefined)
                continue;

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
                            return await this.dialogManager.loadDialogHtml({
                                url: '/arrangement/planner/dialogs/arrangement_information/' + context.arrangement.slug,
                                managerName: MANAGER_NAME,
                                dialogId: 'mainDialog',
                            });
                        },
                        onPreRefresh: (dialog) => {
                            dialog._active_tab = $('#tabs').tabs ( "option", "active" );
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
                            for (const pair of details.formData){
                                console.log(pair[0], pair[1]);
                            }

                            let html = await fetch("/arrangement/planner/dialogs/arrangement_information/" + context.arrangement.slug + "?managerName=arrangementInspector&dialogId=mainDialog", {
                                method: 'POST',
                                body: details.formData,
                                credentials: 'same-origin',
                                headers: {
                                    "X-CSRFToken": details.formData.get("csrfmiddlewaretoken")
                                }
                            })
                            .then(response => response.text())
                            .then(a => {
                                this.dialogManager.reloadDialog("mainDialog");
                            });
                        },
                        onUpdatedCallback: () => { this.dialogManager.reloadDialog("mainDialog"); },
                        dialogOptions: { width: 800, height: 800, dialogClass: 'no-titlebar'  }
                    }),
                ],
                [
                    "addPlannerDialog",
                    new Dialog({
                        dialogElementId: "addPlannerDialog",
                        triggerElementId: "mainDialog__addPlannerBtn",
                        triggerByEvent: true,
                        htmlFabricator: async (context) => {
                            return await this.dialogManager.loadDialogHtml(
                                {
                                    url: "/arrangement/planner/dialogs/add_planner",
                                    managerName: 'arrangementInspector',
                                    dialogId: 'addPlannerDialog', 
                                    customParameters: {
                                        slug: context.arrangement.slug   
                                    }
                                },
                            );
                        },
                        onRenderedCallback: () => {},
                        onUpdatedCallback: ( ) => {
                            this.dialogManager.reloadDialog("mainDialog");
                            this.dialogManager.closeDialog("addPlannerDialog");
                            toastr.success("Planlegger(e) har blitt lagt til")
                        },
                        onSubmit: async (context, details) => {
                            let formData = new FormData();
                            formData.append("planner_ids", details.plannerIds);
                            formData.append("arrangement_slug", details.arrangementSlug);

                            fetch('/arrangement/planner/add_planners', {
                                method: 'POST',
                                body: formData,
                                headers: {
                                    "X-CSRFToken": details.csrf_token
                                }
                            });
                        },
                        dialogOptions: { width: 700 }
                    })
                ],
                [
                    "uploadFilesToArrangementDialog",
                    new Dialog({
                        dialogElementId: "uploadFilesToArrangementDialog",
                        triggerElementId: "mainDialog__uploadFilesBtn",
                        triggerByEvent: true,
                        htmlFabricator: async (context) => {
                            return this.dialogManager.loadDialogHtml({
                                url: '/arrangement/planner/dialogs/upload_files_dialog',
                                managerName: 'arrangementInspector',
                                dialogId: 'uploadFilesToArrangementDialog'
                            });
                        },
                        onRenderedCallback: () => {},
                        onUpdatedCallback: () => { 
                            this.dialogManager.reloadDialog("mainDialog"); 
                            this.dialogManager.closeDialog("uploadFilesToArrangementDialog"); 
                        },
                        onSubmit: async (context, details) => {
                            details.formData.append("slug", context.arrangement.slug);
                            await fetch(`/arrangement/arrangement/files/upload`, {
                                method: 'POST',
                                body: details.formData,
                                headers: {
                                    'X-CSRFToken': details.csrf_token
                                }
                            });
                        },
                        dialogOptions: { 
                            width: 400,
                            dialogClass: 'no-titlebar',
                        }
                    })
                ],
                [
                    "uploadFilesToEventSerieDialog",
                    new Dialog({
                        dialogElementId: "uploadFilesToEventSerieDialog",
                        triggerElementId: undefined,
                        triggerByEvent: true,
                        htmlFabricator: async (context) => {
                            return await this.dialogManager.loadDialogHtml({
                                url: '/arrangement/planner/dialogs/upload_files_dialog',
                                managerName: 'arrangementInspector',
                                dialogId: 'uploadFilesToEventSerieDialog',
                            });
                        },
                        onRenderedCallback: () => { console.info("Upload files to event serie dialog rendered") },
                        onUpdatedCallback: () => { 
                            this.dialogManager.reloadDialog("mainDialog"); 
                            this.dialogManager.closeDialog("uploadFilesToEventSerieDialog"); 
                        },
                        onSubmit: async (context, details) => {
                            details.formData.append("pk", context.lastTriggererDetails.event_serie_pk);
                            await fetch(`/arrangement/eventSerie/${context.lastTriggererDetails.event_serie_pk}/files/upload`, {
                                method: 'POST',
                                body: details.formData,
                                headers: {
                                    'X-CSRFToken': details.csrf_token
                                }
                            });
                        },
                        dialogOptions: { width: 400 },
                    })
                ],
                [
                    "newTimePlanDialog",
                    new Dialog({
                        triggerElementId: "mainPlannerDialog__newTimePlan",
                        dialogElementId: "newTimePlanDialog",
                        triggerByEvent: true,
                        htmlFabricator: async (context) => {
                            return await this.dialogManager.loadDialogHtml({
                                url: '/arrangement/planner/dialogs/create_serie',
                                dialogId: 'newTimePlanDialog',
                                managerName: 'arrangementInspector',
                                customParameters: {
                                    slug: context.arrangement.slug,
                                    orderRoomDialog: "nestedOrderRoomDialog",
                                    orderPersonDialog: "nestedOrderPersonDialog",
                                }
                            })
                        },
                        onRenderedCallback: async (dialogManager, context) => {
                            let info = await this._getRecurringInfo( context.arrangement.arrangement_pk );

                            let $newTimePlanDialog = this.dialogManager.$getDialogElement("newTimePlanDialog");
                            $newTimePlanDialog.find('#serie_title').attr('value', info.title);
                            $newTimePlanDialog.find('#serie_title_en').attr('value', info.title_en);
                            $newTimePlanDialog.find('#serie_ticket_code').attr('value', info.ticket_code);
                            $newTimePlanDialog.find('#serie_expected_visitors').attr('value', info.expected_visitors);

                            info.display_layouts.forEach(display_layout => {
                                $newTimePlanDialog.find('#id_display_layouts_serie_planner_' + ( display_layout - 1))
                                    .prop( "checked", true );
                            });

                            document.querySelectorAll('.form-outline').forEach((formOutline) => {
                                new mdb.Input(formOutline).init();
                            });
                        },
                        onUpdatedCallback: () => {
                            this.dialogManager.reloadDialog("mainDialog");
                            this.dialogManager.closeDialog("newTimePlanDialog");
                        },
                        dialogOptions: { 
                            width: 700,
                            dialogClass: 'no-titlebar',
                        },
                        onSubmit: async (context, details) => {
                            context.serie = details.serie;
                            context.collision_resolution = new Map();

                            let isInCollisionResolutionState = await CollisionsUtil.FireCollisionsSwal(
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
                            return this.dialogManager.loadDialogHtml({
                                url: "/arrangement/planner/dialogs/create_simple_event",
                                managerName: "arrangementInspector",
                                dialogId: "breakOutActivityDialog",
                                customParameters: {
                                    slug: 0,
                                    orderPersonDialog: "orderPersonDialog",
                                    orderRoomDialog: "orderRoomForLocalEventDialog",
                                }
                            });
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
                            let serie = context.serie;

                            let collision_uuid = context._lastTriggererDetails.collision_uuid;
                            let resolution_bundle = context.collision_resolution.get(collision_uuid);
                            let collision_record = resolution_bundle.collision;

                            $('#ticket_code').val(serie.time.ticket_code).trigger('change');
                            $('#title').val(serie.time.title).trigger('change');
                            $('#title_en').attr('value', serie.time.title_en).trigger('change');
                            $('#expected_visitors').attr('value', serie.time.expected_visitors).trigger('change');

                            serie.display_layouts.split(",")
                                .forEach(checkboxElement => {
                                    $(`#${checkboxElement.value}_dlcheck`)
                                        .prop( "checked", true );
                                });

                            let { fromDate, fromTime }  = Utils.splitDateFunc(collision_record.event_a_start);
                            let { toDate, toTime }      = Utils.splitDateFunc(collision_record.event_a_end);

                            $('#fromDate').val(fromDate).trigger('change');
                            $('#fromTime').val(fromTime).trigger('change');
                            $('#toDate').val(toDate).trigger('change');
                            $('#toTime').val(toTime).trigger('change');

                            if (serie.people.length > 0) {
                                let peopleSelectContext = Object();
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
                                let roomSelectContext = Object();
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

                            this.dialogManager.setTitle("breakOutActivityDialog", "Bryt ut aktivitet");
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

                            let collision_state = context.collision_resolution.get(context._lastTriggererDetails.collision_uuid);

                            details.event.fromDate = new Date(details.event.start).toISOString();
                            details.event.toDate = new Date(details.event.end).toISOString();
                            details.event.arrangement = context.arrangement.arrangement_pk;

                            let formData = new FormData();
                            for (let key in details.event) {
                                formData.append(key, details.event[key])
                            }

                            let collisions_on_solution = await CollisionsUtil.GetCollisionsForEvent(formData, details.csrf_token);

                            if (collisions_on_solution.length > 0) {
                                CollisionsUtil.FireOneToOneCollisionWarningSwal(collisions_on_solution[0])
                                    .then(async (_) => {
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
                                    });

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
                        triggerByEvent: true,
                        htmlFabricator: async (context) => {
                            return this.dialogManager.loadDialogHtml({
                                url: "/arrangement/planner/dialogs/create_simple_event",
                                dialogId: "newSimpleActivityDialog",
                                managerName: "arrangementInspector",
                                customParameters: {
                                    slug: context.arrangement.slug,
                                    orderRoomDialog: "nestedOrderRoomDialog",
                                    orderPersonDialog: "nestedOrderPersonDialog",
                                }
                            });
                        },
                        onRenderedCallback: async (dialogManager, context) => {
                            let info = await this._getRecurringInfo( context.arrangement.arrangement_pk );
                            
                            this.dialogManager.setTitle("newSimpleActivityDialog", "Opprett aktivitet");
                            let $newSimpleActivityDialog = this.dialogManager.$getDialogElement("newSimpleActivityDialog");
                            $newSimpleActivityDialog.find("#title").attr("value", info.title);
                            $newSimpleActivityDialog.find("#title_en").attr("value", info.title_en);
                            $newSimpleActivityDialog.find("#ticket_code").attr("value", info.ticket_code);
                            $newSimpleActivityDialog.find("#expected_visitors").attr("value", info.expected_visitors);

                            info.display_layouts.forEach(display_layout => {
                                $newSimpleActivityDialog.find('#' + display_layout + "_dlcheck")
                                    .prop("checked", true);
                            });

                            document.querySelectorAll('.form-outline').forEach((formOutline) => {
                                new mdb.Input(formOutline).init();
                            });
                        },
                        onUpdatedCallback: () => {
                            this.dialogManager.reloadDialog("mainDialog");
                            this.dialogManager.closeDialog("newSimpleActivityDialog");
                        },
                        dialogOptions: { width: 500, dialogClass: 'no-titlebar' },
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
                            return this.dialogManager.loadDialogHtml({
                                url: '/arrangement/planner/dialogs/create_serie',
                                managerName: "arrangementInspector",
                                dialogId: 'editEventSerieDialog',
                                customParameters: {
                                    orderRoomDialog: 'nestedOrderRoomDialog',
                                    orderPersonDialog: 'orderPersonDialog',
                                }
                            });
                        },
                        onRenderedCallback: async (dialogManager, context) => {
                            context.editing_serie_pk = context.lastTriggererDetails.event_serie_pk;

                            let $dialogElement = $(this.dialogManager.$getDialogElement("editEventSerieDialog"));
                            let manifest = await QueryStore.GetSerieManifest(context.editing_serie_pk);
                            PopulateCreateSerieDialogFromManifest(manifest, context.editing_serie_pk, $dialogElement);
                            document.querySelectorAll('.form-outline').forEach((formOutline) => {
                                new mdb.Input(formOutline).init();
                            });
                         },
                        onUpdatedCallback: () => {
                            this.dialogManager.reloadDialog("mainDialog");
                            this.dialogManager.closeDialog("editEventSerieDialog");
                        },
                        onSubmit: async (context, details) => {
                            console.log(context);

                            details.serie.event_serie_pk = context.editing_serie_pk;

                            context.serie = details.serie;
                            context.collision_resolution = new Map();

                            let isInCollisionResolutionState = await CollisionsUtil.FireCollisionsSwal(
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
                        dialogOptions: { 
                            width: 700,
                            dialogClass: 'no-titlebar',
                        }
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
                            return await this.dialogManager.loadDialogHtml({
                                url: '/arrangement/planner/dialogs/promote_main_planner',
                                managerName: 'arrangementInspector',
                                dialogId: 'promotePlannerDialog',
                                customParameters: {
                                    slug: context.arrangement.slug,
                                }
                            });
                        },
                        onRenderedCallback: () => { console.info("Rendered") },
                        onUpdatedCallback: () => {
                            this.dialogManager.reloadDialog("mainDialog");
                            this.dialogManager.closeDialog("promotePlannerDialog");
                        },
                        onSubmit: async (context, details) => {
                            await fetch("/arrangement/arrangement/promote_to_main", {
                                method: 'POST',
                                body: Utils.convertObjToFormData(details),
                                credentials: 'same-origin',
                                headers: {
                                    'X-CSRFToken': details.csrf_token
                                }
                            });
                        },
                        dialogOptions: { width: 500 },
                    })
                ],
                [
                    "newNoteDialog",
                    new Dialog({
                        dialogElementId: "newNoteDialog",
                        triggerElementId: "mainPlannerDialog__newNoteBtn",
                        triggerByEvent: true,
                        htmlFabricator: async (context) => {
                            return await this.dialogManager.loadDialogHtml(
                                {
                                    url: '/arrangement/planner/dialogs/new_note',
                                    managerName: 'arrangementInspector',
                                    dialogId: 'newNoteDialog',
                                    customParameters: {
                                        slug: context.arrangement.slug,
                                        entityType: 'arrangement',
                                    }
                                }
                            )
                        },
                        onRenderedCallback: () => { console.info("Rendered") },
                        onUpdatedCallback: () => {
                            this.dialogManager.reloadDialog("mainDialog");
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
                        dialogOptions: { width: 500, dialogClass: 'no-titlebar' },
                    })
                ],
                [
                    "editNoteDialog",
                    new Dialog({
                        dialogElementId: "editNoteDialog",
                        triggerElementId: undefined,
                        triggerByEvent: true,
                        htmlFabricator: async (context) => {
                            return await this.dialogManager.loadDialogHtml({
                                url: "/arrangement/planner/dialogs/edit_note/" + context.lastTriggererDetails.note_pk,
                                managerName: "arrangementInspector",
                                dialogId: "editNoteDialog",
                            });
                        },
                        onRenderedCallback: () => { console.info("Rendered"); },
                        onUpdatedCallback: () => {
                            this.dialogManager.reloadDialog("mainDialog");
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
                ],
                [
                    "orderPersonDialog",
                    new Dialog({
                        dialogElementId: "orderPersonDialog",
                        triggerElementId: undefined,
                        triggerByEvent: true,
                        htmlFabricator: async (context) => {
                            return this.loadDialogHtml({
                                url: '/arrangement/planner/dialogs/order_person',
                                dialogId: 'orderPersonDialog',
                                managerName: 'arrangementInspector',
                                customParameters: {
                                    serie_guid: context.serie_guid
                                }
                            });
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
                            return await this.dialogManager.loadDialogHtml({
                                url: '/arrangement/planner/dialogs/order_room',
                                managerName: 'arrangementInspector',
                                dialogId: 'orderRoomDialog',
                                customParameters: {
                                    serie_guid: context.serie_guid
                                }
                            });
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
                        onUpdatedCallback: () => { 
                            this.dialogManager.closeDialog("orderRoomForOneEventDialog");
                            this.dialogManager.reloadDialog("mainDialog"); 
                        },
                        dialogOptions: { width: 500 },
                        onSubmit: async (context, details) => {
                            fetch("/arrangement/planner/dialogs/order_rooms_for_event_form", {
                                method: "POST",
                                body: details.formData,
                                headers: {
                                    "X-CSRFToken": details.csrf_token
                                }
                            }).then(_ => { 
                                this.dialogManager.reloadDialog("mainDialog"); 
                                this.dialogManager.closeDialog("orderRoomForOneEventDialog"); 
                            });
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
                        onUpdatedCallback: () => { 
                            this.dialogManager.closeDialog("orderPersonForOneEventDialog");
                            this.dialogManager.reloadDialog("mainDialog"); 
                        },
                        onSubmit: async (context, details) => {
                            fetch("/arrangement/planner/dialogs/order_people_for_event_form", {
                                method: "POST",
                                body: details.formData,
                                headers: {
                                    "X-CSRFToken": details.csrf_token
                                }
                            }).then(_ => { 
                                this.dialogManager.reloadDialog("mainDialog"); 
                                this.dialogManager.closeDialog("orderPersonForOneEventDialog"); 
                            });
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
                            return await this.dialogManager.loadDialogHtml({
                                url: '/arrangement/planner/dialogs/order_room',
                                managerName: 'arrangementInspector',
                                dialogId: 'nestedOrderRoomDialog',
                                customParameters: {
                                    event_pk: 0
                                }
                            });
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
                            return this.dialogManager.loadDialogHtml({
                                url: '/arrangement/planner/dialogs/order_person',
                                dialogId: 'nestedOrderPersonDialog',
                                managerName: 'arrangementInspector',
                                customParameters: {
                                    event_pk:0,
                                    orderRoomDialog: 'orderRoomDialog',
                                    orderPersonDialog: 'orderPersonDialog',
                                }
                            });
                        },
                        onRenderedCallback: () => { },
                        dialogOptions: { width: 500 },
                        onUpdatedCallback: () => {
                            this.dialogManager.closeDialog("nestedOrderPersonDialog");
                            toastr.success("Personer har blitt lagt til");
                        },
                        onSubmit: (context, details) => {
                            let people_ids = details.formData.get("people_ids");
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
                ],
            ]}
        )
    }
}
