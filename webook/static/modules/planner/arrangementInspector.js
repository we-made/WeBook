import { DialogManager, Dialog } from "./dialog_manager/dialogManager.js";
import { SeriesUtil } from "./seriesutil.js"


const MANAGER_NAME = "arrangementInspector"

const MAIN_DIALOG = Symbol("mainDialog")
const ADD_PLANNER_DIALOG = Symbol("addPlannerDialog")

export class ArrangementInspector {
    constructor () {
        this.dialogManager = this._createDialogManager();
    }

    inspect( arrangement ) {
        this.dialogManager.setContext({ arrangement: arrangement });
        this.dialogManager.openDialog( "mainDialog" );
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
                        htmlFabricator: async (context) => {
                            return await fetch("/arrangement/planner/dialogs/create_serie?slug=" + context.arrangement.slug + "&managerName=" + MANAGER_NAME + "&orderRoomDialog=nestedOrderRoomDialog&orderPersonDialog=nestedOrderPersonDialog")
                                .then(response => response.text());
                        },
                        onRenderedCallback: () => { 
                            $('#serie_title').attr('value', $('#id_name').val() );
                            $('#serie_title_en').attr('value', $('#id_name_en').val() );
                        },
                        onUpdatedCallback: () => { 
                            this.dialogManager.reloadDialog("mainDialog"); 
                            this.dialogManager.closeDialog("newTimePlanDialog"); 
                        },
                        dialogOptions: { width: 700 },
                        onSubmit: async (context, details) => { 

                            var registerSerie = async function (serie, arrangementId, csrf_token, ticket_code) {
                                var events = SeriesUtil.calculate_serie(serie);
                                var formData = new FormData();

                                formData.append("saveAsSerie", true); // Special parameter to instruct to save event batch as a serie.
                                formData.append("manifest.pattern", serie.pattern.pattern_type);
                                formData.append("manifest.patternRoutine", serie.pattern.pattern_routine);
                                formData.append("manifest.timeAreaMethod", serie.time_area.method_name);
                                formData.append("manifest.startDate", serie.time_area.start_date);
                                formData.append("manifest.startTime", serie.time.start);
                                formData.append("manifest.endTime", serie.time.end);
                                formData.append("manifest.ticketCode", serie.time.ticket_code);
                                formData.append("manifest.expectedVisitors", serie.time.expected_visitors);
                                formData.append("manifest.title", serie.time.title);
                                formData.append("manifest.title_en", serie.time.title_en);
                                formData.append("manifest.rooms", serie.rooms);
                                formData.append("manifest.people", serie.people);
                                formData.append("manifest.displayLayouts", serie.display_layouts);

                                switch(serie.pattern.pattern_type) {
                                    case "daily":
                                        if (serie.pattern.pattern_routine === "daily__every_x_day") {
                                            formData.append("manifest.interval", serie.pattern.interval);
                                        }
                                        break;
                                    case "weekly":
                                        formData.append("manifest.interval", serie.pattern.week_interval);
                                        var count = 0;
                                        for (var day of ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]) {
                                            formData.append(`manifest.${day}`, serie.pattern.days.get(count));
                                            count++;
                                        }
                                        break;
                                    case "monthly":
                                        switch (serie.pattern.pattern_routine) {
                                            case "month__every_x_day_every_y_month":
                                                formData.append("manifest.interval", serie.pattern.interval);
                                                formData.append("manifest.day_of_month", serie.pattern.day_of_month);
                                                break;
                                            case "month__every_arbitrary_date_of_month":
                                                formData.append("manifest.arbitrator", serie.pattern.arbitrator);
                                                formData.append("manifest.day_of_week", serie.pattern.weekday);
                                                formData.append("manifest.interval", serie.pattern.interval);
                                                break;
                                        }
                                        break;
                                    case "yearly":
                                        formData.append("manifest.interval", serie.pattern.year_interval);
                                        switch (serie.pattern.pattern_routine) {
                                            case "yearly__every_x_of_month":
                                                formData.append("manifest.day_of_month", serie.pattern.day_index);
                                                formData.append("manifest.month", serie.pattern.month);
                                                break;
                                            case "yearly__every_arbitrary_weekday_in_month":
                                                formData.append("manifest.day_of_week", serie.pattern.weekday);
                                                formData.append("manifest.month", serie.pattern.month);
                                                formData.append("manifest.arbitrator", serie.pattern.arbitrator);
                                                break;
                                        }
                                        break;
                                }

                                if (serie.time_area.stop_within !== undefined) {
                                    formData.append("manifest.stopWithin", serie.time_area.stop_within);
                                }
                                if (serie.time_area.instances !== undefined) {
                                    formData.append("manifest.stopAfterXInstances", serie.time_area.instances);
                                }
                                if (serie.time_area.projectionDistanceInMonths !== undefined) {
                                    formData.append("manifest.projectionDistanceInMonths", serie.time_area.projectionDistanceInMonths);
                                }

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

                            await registerSerie( details.serie, context.arrangement.arrangement_pk, details.csrf_token )
                        }
                    })
                ],
                [
                    "newSimpleActivityDialog",
                    new Dialog({
                        dialogElementId: "newSimpleActivityDialog",
                        triggerElementId: "mainPlannerDialog__newSimpleActivity",
                        htmlFabricator: async (context) => {
                            return await fetch('/arrangement/planner/dialogs/create_simple_event?slug=' + context.arrangement.slug + "&managerName=" + MANAGER_NAME + "&orderRoomDialog=nestedOrderRoomDialog&orderPersonDialog=nestedOrderPersonDialog")
                                .then(response => response.text());
                        },
                        onRenderedCallback: () => { console.info("Rendered") },
                        onUpdatedCallback: () => { 
                            this.dialogManager.reloadDialog("mainDialog"); 
                            this.dialogManager.closeDialog("newSimpleActivityDialog"); 
                        },
                        dialogOptions: { width: 500 },
                        onSubmit: (context, details) => {
                            var events = [] 
                            events.push(details.event)

                            var registerEvents = async function (events, arrangementId, csrf_token, ticket_code) {
                                var formData = new FormData();
                                for (let i = 0; i < events.length; i++) {
                                    var event = events[i];
                                    event.arrangement = arrangementId;
                                    event.id = 0;
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

                            registerEvents(events, context.arrangement.arrangement_pk, details.csrf_token);
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
                            
                            $('#serie_uuid').attr("value", context.lastTriggererDetails.event_serie_pk);
                            $('#serie_title').val(manifest.title);
                            $('#serie_title_en').attr("value", manifest.title_en);
                            $('#serie_expected_visitors').attr("value", manifest.expected_visitors);
                            $('#serie_ticket_code').attr("value", manifest.ticket_code);
                            $('#area_start_date').attr("value", manifest.start_date);
                            $('#serie_start').attr("value", manifest.start_time);
                            $('#serie_end').attr("value", manifest.end_time);

                            if (manifest.rooms.length > 0) {
                                var roomSelectContext = Object();
                                roomSelectContext.rooms = manifest.rooms.map(a => a.id).join(",");
                                roomSelectContext.room_name_map = new Map();

                                for (let i = 0; i < manifest.rooms.length; i++) {
                                    let room = manifest.rooms[i];
                                    roomSelectContext.room_name_map.set(String(room.id), room.name);
                                }

                                document.dispatchEvent(new CustomEvent(
                                    "arrangementInspector.d2_roomsSelected",
                                    { detail: {
                                        context: roomSelectContext
                                    } }
                                ));
                            }
                            if (manifest.people.length > 0) {
                                var peopleSelectContext = Object();
                                peopleSelectContext.people = manifest.people.map(a => a.id).join(",");
                                peopleSelectContext.people_name_map = new Map();

                                for (let i = 0; i < manifest.people.length; i++) {
                                    let person = manifest.people[i];
                                    peopleSelectContext.people_name_map.set(String(person.id), person.name);
                                }

                                document.dispatchEvent(new CustomEvent(
                                    "arrangementInspector.d2_peopleSelected",
                                    { detail: {
                                        context: peopleSelectContext
                                    } }
                                ));
                            }

                            manifest.display_layouts.forEach(display_layout => {
                                $('#id_display_layouts_serie_planner_' + String(parseInt(display_layout.id)))
                                    .prop( "checked", true );
                            })

                            switch(manifest.recurrence_strategy) {
                                case "StopWithin":
                                    $('#radio_timeAreaMethod_stopWithin').prop("checked", true).click();
                                    $('#area_stopWithin').val(manifest.stop_within);
                                    $('#area_stopWithin').removeAttr("disabled");
                                    break;
                                case "StopAfterXInstances":
                                    $('#radio_timeAreaMethod_stopAfterXInstances').prop("checked", true).click();
                                    $('#area_stopAfterXInstances').val(manifest.stop_after_x_occurences);
                                    $('#area_stopAfterXInstances').removeAttr("disabled");
                                    break;
                                case "NoStopDate":
                                    $('#radio_timeAreaMethod_noStopDate').prop("checked", true).click();
                                    $('#area_noStop_projectXMonths').val(manifest.project_x_months_into_future);
                                    $('#area_noStop_projectXMonths').removeAttr("disabled");
                                    break;
                            }

                            switch (manifest.pattern) {
                                case "daily":
                                    $('#radio_pattern_daily').prop("checked", true).click();

                                    switch(manifest.pattern_strategy) {
                                        case "daily__every_x_day":
                                            $('#radio_pattern_daily_every_x_day_subroute').prop("checked", true);
                                            $('#every_x_day__interval').val(parseInt(manifest.strategy_specific.interval));
                                            $('#every_x_day__interval').removeAttr("disabled");
                                            break;
                                        case "daily__every_weekday":
                                            $('#radio_pattern_daily_every_weekday_subroute').prop("checked", true);
                                            break;
                                    }
                                    break;
                                case "weekly":
                                    $('#radio_pattern_weekly').prop("checked", true).click();
                                    $("#week_interval").val(parseInt(manifest.strategy_specific.interval));
                                    
                                    var days = [
                                        $("#monday"),
                                        $("#tuesday"),
                                        $("#wednesday"),
                                        $("#thursday"),
                                        $("#friday"),
                                        $("#saturday"),
                                        $("#sunday"),
                                    ]

                                    for (var i = 0; i < manifest.strategy_specific.days.length; i++) {
                                        if (manifest.strategy_specific.days[i] == true) {
                                            days[i].attr("checked", true);
                                        }
                                    }

                                    break;
                                case "monthly":
                                    $('#radio_pattern_monthly').prop("checked", true).click();
                                    switch(manifest.pattern_strategy) {
                                        case "month__every_x_day_every_y_month":
                                            $('#every_x_day_every_y_month__day_of_month_radio').prop("checked", true);
                                            $('#every_x_day_every_y_month__day_of_month').val(manifest.strategy_specific.day_of_month);
                                            $("#every_x_day_every_y_month__month_interval").val(parseInt(manifest.strategy_specific.interval));
                                            break;
                                        case "month__every_arbitrary_date_of_month":
                                            $('#every_x_day_every_y_month__month_interval_radio').prop("checked", true);
                                            $('#every_dynamic_date_of_month__arbitrator').val(manifest.strategy_specific.arbitrator);
                                            $('#every_dynamic_date_of_month__weekday').val(manifest.strategy_specific.day_of_week);
                                            $('#every_dynamic_date_of_month__month_interval').val(manifest.strategy_specific.interval);
                                            break;
                                    }
                                    break;
                                case "yearly":
                                    $('#radio_pattern_yearly').prop("checked", true).click();
                                    $('#pattern_yearly_const__year_interval').val(manifest.strategy_specific.interval);
                                    switch(manifest.pattern_strategy) {
                                        case "yearly__every_x_of_month":
                                            $('#every_x_datemonth_of_year_radio').prop("checked", true);
                                            $('#every_x_of_month__date').val(manifest.strategy_specific.day_of_month);
                                            $('#every_x_of_month__month').val(manifest.strategy_specific.month);
                                            break;
                                        case "yearly__every_arbitrary_weekday_in_month":
                                            $('#every_x_dynamic_day_in_month_radio').prop("checked", true);
                                            $('#every_arbitrary_weekday_in_month__arbitrator').val(manifest.strategy_specific.arbitrator);
                                            $('#every_arbitrary_weekday_in_month__weekday').val(manifest.strategy_specific.day_of_week);
                                            $('#every_arbitrary_weekday_in_month__month').val(manifest.strategy_specific.month);                         
                                            break;
                                    }
                                    break;
                            }

                            if (manifest.pattern !== "daily") {
                                $('#patternRoute_daily').hide();
                            }
                         },
                        onUpdatedCallback: () => {
                            this.dialogManager.reloadDialog("mainDialog");
                            this.dialogManager.closeDialog("editEventSerieDialog");
                        },
                        onSubmit:  async (context, details) => { 
                            var registerSerie = async function (serie, arrangementId, csrf_token, ticket_code) {
                                var events = SeriesUtil.calculate_serie(serie);
                                var formData = new FormData();

                                formData.append("saveAsSerie", true); // Special parameter to instruct to save event batch as a serie.
                                formData.append("predecessorSerie", serie._uuid); // The preceding serie must be removed.
                                formData.append("manifest.pattern", serie.pattern.pattern_type);
                                formData.append("manifest.patternRoutine", serie.pattern.pattern_routine);
                                formData.append("manifest.timeAreaMethod", serie.time_area.method_name);
                                formData.append("manifest.startDate", serie.time_area.start_date);
                                formData.append("manifest.startTime", serie.time.start);
                                formData.append("manifest.endTime", serie.time.end);
                                formData.append("manifest.ticketCode", serie.time.ticket_code);
                                formData.append("manifest.expectedVisitors", serie.time.expected_visitors);
                                formData.append("manifest.title", serie.time.title);
                                formData.append("manifest.title_en", serie.time.title_en);
                                formData.append("manifest.rooms", serie.rooms);
                                formData.append("manifest.people", serie.people);
                                formData.append("manifest.displayLayouts", serie.display_layouts);

                                switch(serie.pattern.pattern_type) {
                                    case "daily":
                                        if (serie.pattern.pattern_routine === "daily__every_x_day") {
                                            formData.append("manifest.interval", serie.pattern.interval);
                                        }
                                        break;
                                    case "weekly":
                                        formData.append("manifest.interval", serie.pattern.week_interval);
                                        var count = 0;
                                        for (var day of ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]) {
                                            formData.append(`manifest.${day}`, serie.pattern.days.get(count));
                                            count++;
                                        }
                                        break;
                                    case "monthly":
                                        switch (serie.pattern.pattern_routine) {
                                            case "month__every_x_day_every_y_month":
                                                formData.append("manifest.interval", serie.pattern.interval);
                                                formData.append("manifest.day_of_month", serie.pattern.day_of_month);
                                                break;
                                            case "month__every_arbitrary_date_of_month":
                                                formData.append("manifest.arbitrator", serie.pattern.arbitrator);
                                                formData.append("manifest.day_of_week", serie.pattern.weekday);
                                                formData.append("manifest.interval", serie.pattern.interval);
                                                break;
                                        }
                                        break;
                                    case "yearly":
                                        formData.append("manifest.interval", serie.pattern.year_interval);
                                        switch (serie.pattern.pattern_routine) {
                                            case "yearly__every_x_of_month":
                                                formData.append("manifest.day_of_month", serie.pattern.day_index);
                                                formData.append("manifest.month", serie.pattern.month);
                                                break;
                                            case "yearly__every_arbitrary_weekday_in_month":
                                                formData.append("manifest.day_of_week", serie.pattern.weekday);
                                                formData.append("manifest.month", serie.pattern.month);
                                                formData.append("manifest.arbitrator", serie.pattern.arbitrator);
                                                break;
                                        }
                                        break;
                                }

                                if (serie.time_area.stop_within !== undefined) {
                                    formData.append("manifest.stopWithin", serie.time_area.stop_within);
                                }
                                if (serie.time_area.instances !== undefined) {
                                    formData.append("manifest.stopAfterXInstances", serie.time_area.instances);
                                }
                                if (serie.time_area.projectionDistanceInMonths !== undefined) {
                                    formData.append("manifest.projectionDistanceInMonths", serie.time_area.projectionDistanceInMonths);
                                }

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

                            await registerSerie( details.serie, context.arrangement.arrangement_pk, details.csrf_token )
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
                            }).then(_ => { this.dialogManager.reloadDialog("mainDialog"); this.dialogManager.closeDialog("orderPersonDialog"); });
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
                            }).then(_ => { this.dialogManager.reloadDialog("mainDialog"); this.dialogManager.closeDialog("orderRoomDialog"); });

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