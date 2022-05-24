import { Dialog, DialogManager } from "./dialog_manager/dialogManager.js";
import { serieConvert } from "./serieConvert.js";
import { SeriesUtil } from "./seriesutil.js";


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
                                this.dialogManager.context.series = new Map();
                            }
                            if (this.dialogManager.context.events !== undefined) {
                                this.dialogManager.context.events = new Map();
                            }

                            console.log("calling _makeAware")
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
                                    var displayLayoutCounter = 0;

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
                                
                                formData = serieConvert({ serie, formData });

                                for (let i = 0; i < events.length; i++) {
                                    var event = events[i];
                                    event.arrangement=arrangementId;
                                    event.start = event.from.toISOString();
                                    event.end=event.to.toISOString();
                                    event.ticket_code = ticket_code;
                                    event.expected_visitors = serie.time.expected_visitors;
                                    event.rooms = serie.rooms;
                                    event.people = serie.people;
                                    event.display_layouts = serie.display_layouts;

                                    for (var key in event) {
                                        formData.append("events[" + i + "]." + key, event[key]);
                                    }
                                }

                                formData.append("saveAsSerie", true);

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
                                $('#serie_ticket_code').attr('value', $('#id_ticket_code')[0].value );
                                $('#serie_title').attr('value', $('#id_name')[0].value );
                                $('#serie_title_en').attr('value', $('#id_name_en')[0].value );
                                $('#serie_expected_visitors').attr('value', $('#id_expected_visitors')[0].value );

                                document.querySelectorAll("input[name='display_layouts']:checked")
                                    .forEach(checkboxElement => {
                                        $('#id_display_layouts_serie_planner_' + parseInt(checkboxElement.value) - 1)
                                            .prop( "checked", true );
                                    })
                                    
                                // createSerieDialog__evaluateEnTitleObligatory();
                                
                                $('#serie_uuid').val(crypto.randomUUID());

                                return;
                            }
                            
                            var serie = context.series.get(context.lastTriggererDetails.serie_uuid);

                            $('#serie_uuid').val(serie._uuid);
                            $('#serie_title').val(serie.time.title);
                            $('#serie_title_en').val(serie.time.title_en);
                            $('#serie_start').val(serie.time.start);
                            $('#serie_end').val(serie.time.end);
                            $('#serie_ticket_code').val(serie.time.ticket_code);
                            $('#serie_expected_visitors').val(serie.time.expected_visitors);
                            $('#area_start_date').val(serie.time_area.start_date)

                            // This is fairly messy I am afraid, but the gist of what we're doing here is simulating that the user
                            // has "selected" rooms as they would through the dialog interface.
                            if (serie.people.length > 0) {
                                var peopleSelectContext = Object();
                                peopleSelectContext.people = serie.people.join(",");
                                peopleSelectContext.people_name_map = serie.people_name_map;
                                document.dispatchEvent(new CustomEvent(
                                    "arrangementCreator.d2_peopleSelected",
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
                                    "arrangementCreator.d2_roomsSelected",
                                    { detail: {
                                        context: roomSelectContext
                                    } }
                                ));
                            }

                            serie.display_layouts.split(",").forEach(element => {
                                $('#id_display_layouts_serie_planner_' + String(parseInt(element) - 1))
                                    .prop( "checked", true );
                            })

                            switch(serie.time_area.method_name) {
                                case "StopWithin":
                                    $('#radio_timeAreaMethod_stopWithin').prop("checked", true);
                                    $('#area_stopWithin').val(serie.time_area.stop_within);
                                    $('#area_stopWithin')[0].disabled = false;
                                    break;
                                case "StopAfterXInstances":
                                    $('#radio_timeAreaMethod_stopAfterXInstances').prop("checked", true);
                                    $('#area_stopAfterXInstances').val(serie.time_area.instances);
                                    $('#area_stopAfterXInstances')[0].disabled = false;
                                    break;
                                case "NoStopDate":
                                    $('#radio_timeAreaMethod_noStopDate').prop("checked", true);
                                    $('#area_noStop_projectXMonths').val(serie.time_area.projectionDistanceInMonths);
                                    $('#area_noStop_projectXMonths')[0].disabled = false;
                                    break;
                            }

                            switch(serie.pattern.pattern_type) {
                                case "daily":
                                    $('#radio_pattern_daily').prop("checked", true);
                                    switch(serie.pattern.pattern_routine) {
                                        case "daily__every_x_day":
                                            $('#radio_pattern_daily_every_x_day_subroute').prop("checked", true);
                                            $('#every_x_day__interval').val(parseInt(serie.pattern.interval));
                                            break;
                                        case "daily__every_weekday":
                                            $('#radio_pattern_daily_every_weekday_subroute')
                                                .prop("checked", true);
                                            break;
                                    }
                                    break;
                                case "weekly":
                                    $('#radio_pattern_weekly').prop("checked", true);
                                    $("#week_interval").val(serie.pattern.week_interval);

                                    var days = [
                                        $("#monday"),
                                        $("#tuesday"),
                                        $("#wednesday"),
                                        $("#thursday"),
                                        $("#friday"),
                                        $("#saturday"),
                                        $("#sunday"),
                                    ]

                                    for (let i = 1; i < 8; i++) {
                                        if (serie.pattern.days.get(i) === true) {
                                            days[i - 1].attr("checked", true);
                                        }
                                    }
                                    break;
                                case "monthly":
                                    $('#radio_pattern_monthly').prop("checked", true).click();
                                    
                                    switch(serie.pattern.pattern_routine) {
                                        case "month__every_x_day_every_y_month":
                                            $('#every_x_day_every_y_month__day_of_month_radio').prop("checked", true);
                                            $('#every_x_day_every_y_month__day_of_month').val(serie.pattern.day_of_month);
                                            $('#every_x_day_every_y_month__month_interval').val(serie.pattern.interval);
                                            break;
                                        case "month__every_arbitrary_date_of_month":
                                            $('#every_x_day_every_y_month__month_interval_radio').prop("checked", true);
                                            document.querySelector("#every_dynamic_date_of_month__arbitrator").setAttribute("init_value", serie.pattern.arbitrator);
                                            document.querySelector("#every_dynamic_date_of_month__weekday").setAttribute("init_value", serie.pattern.weekday);
                                            $("#every_dynamic_date_of_month__month_interval").val(serie.pattern.interval);
                                            break;
                                    }

                                    break;
                                case "yearly":
                                    $('#radio_pattern_yearly').prop("checked", true);
                                    $('#pattern_yearly_const__year_interval').val(serie.pattern.year_interval);

                                    switch(serie.pattern.pattern_routine) {
                                        case "yearly__every_x_of_month":
                                            $('#every_x_datemonth_of_year_radio').prop("checked", true);
                                            $('#every_x_of_month__date').val(serie.pattern.day_index);
                                            document.querySelector("#every_x_of_month__month").setAttribute("init_value", serie.pattern.month);
                                            break;
                                        case "yearly__every_arbitrary_weekday_in_month":
                                            $('#every_x_dynamic_day_in_month_radio').prop("checked", true);
                                            document.querySelector("#every_arbitrary_weekday_in_month__arbitrator").setAttribute("init_value", serie.pattern.arbitrator);
                                            document.querySelector("#every_arbitrary_weekday_in_month__weekday").setAttribute("init_value", serie.pattern.weekday);
                                            document.querySelector("#every_arbitrary_weekday_in_month__month").setAttribute("init_value", serie.pattern.month);

                                            $("#every_arbitrary_weekday_in_month__month").val(serie.pattern.month);
                                            break;
                                    }

                                    break;
                            }

                            // This is a bad solution to a pesky bug where the "daily" strategy choices appear when selecting
                            // weekly/monthly/yearly. Should be fixed on createSerieDialog when time allows.
                            if (serie.pattern.pattern_type !== "daily") {
                                $('#patternRoute_daily').hide();
                            }
                        },
                        onUpdatedCallback: () => { 
                            toastr.success("Tidsplan lagt til eller oppdatert i planen");
                            this.dialogManager.closeDialog("newTimePlanDialog"); 
                        },
                        onSubmit: async (context, details) => {
                            if (context.series === undefined) {
                                context.series = new Map();
                            }
                            if (details.serie._uuid === undefined) {
                                details.serie._uuid = crypto.randomUUID();
                            }
                            
                            var formData = new FormData();
                            formData = serieConvert(details.serie, formData, "");
                            fetch("/arrangement/analysis/analyzeNonExistentSerie", {
                                method: 'POST',
                                body: formData,
                                headers: {
                                    "X-CSRFToken": details.csrf_token
                                },
                                credentials: 'same-origin'
                            }).then(response => response.text()).then(text => console.log(text));

                            context.series.set(details.serie._uuid, details.serie);
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
                            return await fetch('/arrangement/planner/dialogs/create_simple_event?slug=0&managerName=arrangementCreator&dialog=newSimpleActivityDialog&orderRoomDialog=orderRoomDialog&orderPersonDialog=orderPersonDialog')
                                .then(response => response.text());
                        },
                        onRenderedCallback: (dialogManager, context) => { 
                            if (context.lastTriggererDetails === undefined) {
                                $('#ticket_code').attr('value', $('#id_ticket_code')[0].value );
                                $('#title').attr('value', $('#id_name')[0].value );
                                $('#title_en').attr('value', $('#id_name_en')[0].value );
                                $('#expected_visitors').attr('value', $('#id_expected_visitors')[0].value );
                                
                                document.querySelectorAll("input[name='display_layouts']:checked")
                                    .forEach(checkboxElement => {
                                        $(`#${checkboxElement.value}_dlcheck`)
                                            .prop( "checked", true );
                                    })
                                    
                                // This ensures that english title is only obligatory IF a display layout has been selected.
                                dialogCreateEvent__evaluateEnTitleObligatory();

                                $('#event_uuid').val(crypto.randomUUID());

                                return;
                            }

                            var event = context.events.get(context.lastTriggererDetails.event_uuid);
                            
                            var splitDateFunc = function (strToDateSplit) {
                                var date_str = strToDateSplit.split("T")[0];
                                var time_str = new Date(strToDateSplit).toTimeString().split(' ')[0];
                                return [ date_str, time_str ];
                            }
                            var startTimeArtifacts = splitDateFunc(event.start);
                            var endTimeArtifacts = splitDateFunc(event.end);

                            $('#event_uuid').val(event._uuid);
                            $('#title').val(event.title);
                            $('#title_en').val(event.title_en);
                            $('#ticket_code').val(event.ticket_code);
                            $('#expected_visitors').val(event.expected_visitors);
                            $('#fromDate').val(startTimeArtifacts[0]);
                            $('#fromTime').val(startTimeArtifacts[1]);
                            $('#toDate').val(endTimeArtifacts[0]);
                            $('#toTime').val(endTimeArtifacts[1]);

                            event.display_layouts.split(",").forEach(element => {
                                $(`#${String(parseInt(element))}_dlcheck`)
                                    .prop( "checked", true );
                            })

                            // This is fairly messy I am afraid, but the gist of what we're doing here is simulating that the user
                            // has "selected" rooms as they would through the dialog interface.
                            if (event.people.length > 0) {
                                var peopleSelectContext = Object();
                                peopleSelectContext.people = event.people.join(",");
                                peopleSelectContext.people_name_map = event.people_name_map;
                                document.dispatchEvent(new CustomEvent(
                                    "arrangementCreator.d1_peopleSelected",
                                    { detail: {
                                        context: peopleSelectContext
                                    } }
                                ));
                            }
                            if (event.rooms.length > 0) {
                                var roomSelectContext = Object();
                                roomSelectContext.rooms = event.rooms.join(",");
                                roomSelectContext.room_name_map = event.room_name_map;
                                document.dispatchEvent(new CustomEvent(
                                    "arrangementCreator.d1_roomsSelected",
                                    { detail: {
                                        context: roomSelectContext
                                    } }
                                ));
                            }
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
                            return await fetch(`/arrangement/planner/dialogs/order_room?event_pk=0&manager=arrangementCreator&dialog=orderRoomDialog`)
                                .then(response => response.text());
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
                            return await fetch(`/arrangement/planner/dialogs/order_person?event_pk=0&manager=arrangementCreator&dialog=orderPersonDialog`)
                            .then(response => response.text());
                        },
                        onRenderedCallback: () => { },
                        dialogOptions: { width: 500 },
                        onUpdatedCallback: () => { 
                            toastr.success("Personer lagt til");
                            this.dialogManager.closeDialog("orderPersonDialog");
                        },
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