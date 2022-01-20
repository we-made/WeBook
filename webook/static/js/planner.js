class DateExtensions {
    /* Overwrite the time values for one Date instance with the value of a time field (as a str) */
    static OverwriteDateTimeWithTimeInputValue(date_to_write_time_to, time_input_val_as_str) {

        let times = time_input_val_as_str.split(':');
        let date = new Date(date_to_write_time_to);

        date.setHours(times[0]);
        date.setMinutes(times[1]);

        return date;
    }
}


Date.prototype.addDays = function(days) {
    var date = new Date(this.valueOf());
    date.setDate(date.getDate() + days);
    return date;
}
/*
    Top level.
*/
class Planner {
    constructor({ onClickEditButton, onClickInfoButton, csrf_token, arrangement_id, texts = undefined } = {}) {
        this.local_context = new LocalPlannerContext(this)
        
        this.renderer_manager = new RendererManager({
            context: this.local_context,
            renderers: undefined,
            onClickEditButton: onClickEditButton,
            onClickInfoButton: onClickInfoButton,
            planner:this
        });
        
        this.textLib = new Map([
            ["create", "Create"],
            ["delete", "Delete"],
            ["edit", "Edit"],
            ["info", "Info"]
        ]);

        if (texts !== undefined) {
            this.textLib = new Map([...this.textLib, ...texts ]);
        }

        this.csrf_token = csrf_token
        this.synchronizer = new ContextSynchronicityManager(csrf_token, arrangement_id, this)
        this.synchronizer.getEventsOnSource();
        
        this.local_context.onSeriesChanged = function ({ planner, eventsAffected, changeType } = {}) {
            console.log("=> Serie added")
        }

        this.local_context.onEventCreated = function ({ createdEvent, planner} = {}) {
            console.log("=> Event created")
            planner.synchronizer.pushEvent(createdEvent);

            planner.init();
        }

        this.local_context.onEventsCreated = function ({eventsCreated, planner} = {}) {
            console.log("=> Events created")
            for (let i = 0; i < eventsCreated.length; i++) {
                planner.synchronizer.pushEvent(eventsCreated[i]);
            }
            
            planner.init();
        }

        this.local_context.onEventUpdated = function ({ eventAfterUpdate, planner } = {}) {
            console.log("==> Event updated")
            planner.synchronizer.pushEvent(eventAfterUpdate);
            planner.init();
        }

        this.local_context.onEventsDeleted = function ({ deletedEvents, planner } = {}) {
            console.log("=> Events deleted")
            for (let i = 0; i < deletedEvents.length; i++) {
                planner.synchronizer.deleteEvent(deletedEvents[i]);
            }

            planner.init();
        }

        this.local_context.onEventDeleted = function ({ deletedEvent, planner } = {}) {
            console.log("=> Event deleted")
            planner.synchronizer.deleteEvent(deletedEvent);
            planner.init();
        }
    }

    init() {
        this.renderer_manager.render(Array.from(this.local_context.events.values()));
    }
}


/* handle synchronizing data between multiple contexts */
class ContextSynchronicityManager {
    constructor (csrf_token, arrangement_id, planner) {
        this.uuid_to_id_map = new Map();

        let wrap = document.createElement("span");
        wrap.innerHTML = csrf_token
        this.csrf_token = wrap.children[0].value;
        this.planner = planner;
        this.arrangement_id = arrangement_id;
    }

    /* Retrieve all events from upstream, and push into planner */
    getEventsOnSource () {
        let planner = this.planner;
        let id_map = this.uuid_to_id_map;
        fetch('/arrangement/planner/get_events?arrangement_id=' + this.arrangement_id)
            .then(response => response.json())
            .then(data => {
                let events = JSON.parse(data);
                events.forEach(function (ev) {
                    let converted_event = {
                        title: ev.fields.title,
                        from: new Date(ev.fields.start),
                        to: new Date(ev.fields.end),
                        color: (ev.fields.color !== undefined &&  ev.fields.color !== null && ev.fields.color !== "" ? ev.fields.color : "blue")
                    };
                    let uuid = planner.local_context.add_event(converted_event, false);
                    id_map.set(uuid, ev.pk);
                });
            })
            .then(a => planner.init())
    }

    pushEvent (event) {
        let id = this.uuid_to_id_map.get(event.id);

        if (id !== undefined) {
            let data = new FormData();

            data.append("id", id);
            data.append("title", event.title);
            data.append("start", event.from.toISOString());
            data.append("end", event.to.toISOString());
            data.append("color", event.color);
            data.append("arrangement", this.arrangement_id);
            data.append('csrfmiddlewaretoken', this.csrf_token);

            console.log(data);

            fetch('/arrangement/planner/update_event/' + id, {
                method: 'POST',
                body: data,
                credentials: 'same-origin',
            });
        }
        else {
            let data = new FormData();

            data.append("title", event.title);
            data.append("start", event.from.toISOString());
            data.append("end", event.to.toISOString());
            data.append("arrangement", this.arrangement_id);
            data.append("color", event.color);
            data.append('csrfmiddlewaretoken', this.csrf_token);
            
            console.log(data);

            fetch('/arrangement/planner/create_event', {
                method: 'POST',
                body: data,
                credentials: 'same-origin',
            }).then(response => response.json())
              .then(data => {
                  this.uuid_to_id_map.set(event.id, data.id);
              });

        }
    }

    deleteEvent (event) {
        let id = this.uuid_to_id_map.get(event.id);

        if (id === undefined) {
            throw "Event does not exist upstream, or we do not know about it.";
        }
        
        let data = new FormData();
        data.append('csrfmiddlewaretoken', this.csrf_token);

        fetch("/arrangement/planner/delete_event/" + id, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': this.csrf_token
            },
            credentials: "same-origin"
        });
    }
}


class StrategyExecutorAbstraction {
    constructor ({function_to_run, parameter_obj}={}) {
        this.function_to_run = function_to_run
        
        this.parameters = {}
        if (parameter_obj !== undefined) {
            this.add_object_keyvals_as_params(parameter_obj);
        }
    }

    add_object_keyvals_as_params(obj) {
        for (let [key, value] of Object.entries(obj)) {
            this.parameters[key] = value;
        }
    }

    run(extra_params=undefined) {
        if (extra_params !== undefined) {
            this.add_object_keyvals_as_params(extra_params);
        }

        return this.function_to_run(this.parameters);
    }
}

/* local context on the client. serves as master */
class LocalPlannerContext {
    constructor(planner_backref) {
        this.series = new Map();
        this.events = new Map();

        this.planner = planner_backref

        this.onEventsChanged = function (events) { };
        this.onSeriesChanged = function (events) { };
    }

    add_serie(serie) {
        let serie_uuid = crypto.randomUUID();
        serie.id = serie_uuid;
        this.series.set(serie_uuid, serie);
        let generatedEvents = this.SeriesUtil.calculate_serie(serie);
        this.add_events(generatedEvents, serie_uuid);
        this.onSeriesChanged({planner: this.planner, eventsAffected: this.generatedEvents, changeType: "create" });
    }

    add_event(event, triggerEvent=true) {
        let uuid = crypto.randomUUID();
        event.id = uuid;
        this.events.set(uuid, event);
        if (triggerEvent === true) {
            this.onEventCreated({ createdEvent: event, planner: this.planner });
        }
        return uuid;
    }

    update_event(event, uuid) {
        this.events.set(uuid, event);
        event.id = uuid;
        this.onEventUpdated({ eventAfterUpdate: event, planner: this.planner });
    }

    add_events(events, serie_uuid=undefined) {
        if (serie_uuid !== undefined) {
            events.forEach(function (event) {
                event.serie_uuid = serie_uuid;
            })
        }

        for (let i = 0; i < events.length; i++) {
            let event_uuid = crypto.randomUUID();
            let ev = events[i];
            ev.id = event_uuid;
            this.events.set(event_uuid, ev);
        }

        this.onEventsCreated({ eventsCreated: events, planner: this.planner });
    }

    delete_serie(serie_uuid) {
        for (let i = 0; i < this.events.values().length; i++) {
            let event = this.events.values()[i];
            if (event.serie_uuid === serie_uuid) {
                this.remove_event(i.id);
            }
        }

        this.series.delete(serie_uuid, 1);
        this.onSeriesChanged({ planner: this.planner, eventsAffected: this.events, changeType: "delete" });
        this.onEventsDeleted({ deletedEvents: this.events, planner: this.planner });
    }

    remove_event(uuid) {
        let delete_event = this.events.get(uuid);
        this.events.delete(uuid);
        this.onEventDeleted({ deletedEvent: delete_event, planner: this.planner });
    }

    remove_events(uuids) {
        indices.forEach(function (uuid) {
            remove_event(uuid);
        });
    }

    SeriesUtil = class SeriesUtil {

        static calculate_serie (serie) {
            const pattern_strategies = new Map();
            pattern_strategies.set(
                "daily__every_x_day", 
                new StrategyExecutorAbstraction({
                    function_to_run: this.daily__every_x_day,
                    parameter_obj: serie.pattern
                })
            );
            pattern_strategies.set(
                "daily__every_weekday",
                new StrategyExecutorAbstraction({
                    function_to_run: this.daily__every_weekday,
                    parameter_obj: {},
                })
            );
            pattern_strategies.set(
                "weekly__standard",
                new StrategyExecutorAbstraction({
                    function_to_run: this.weekly_standard,
                    parameter_obj: serie.pattern,
                })
            );
            pattern_strategies.set(
                "month__every_x_day_every_y_month",
                new StrategyExecutorAbstraction({
                    function_to_run: this.month__every_x_day_every_y_month,
                    parameter_obj: serie.pattern,
                })
            );
            pattern_strategies.set(
                "month__every_arbitrary_date_of_month", 
                new StrategyExecutorAbstraction({
                    function_to_run: this.month__every_arbitrary_date_of_month,
                    parameter_obj: serie.pattern,
                }));
            pattern_strategies.set(
                "yearly__every_x_of_month", 
                new StrategyExecutorAbstraction({
                    function_to_run: this.yearly__every_x_of_month,
                    parameter_obj: serie.pattern,
                })
            );
            pattern_strategies.set(
                "yearly__every_arbitrary_weekday_in_month",
                new StrategyExecutorAbstraction({
                    function_to_run: this.yearly__every_arbitrary_weekday_in_month,
                    parameter_obj: serie.pattern,
                })
            );

            const area_strategies = new Map();
            area_strategies.set(
                "StopWithin", 
                new StrategyExecutorAbstraction(
                    {
                        function_to_run: this.area__stop_within, 
                        parameter_obj: {
                            stop_within_date: DateExtensions.OverwriteDateTimeWithTimeInputValue(serie.time_area.stop_within, "23:59")
                        }
                    }
                )
            );
            area_strategies.set(
                "StopAfterXInstances", 
                new StrategyExecutorAbstraction(
                    {
                        function_to_run: this.area__stop_after_x_instances,
                        parameter_obj: serie.time_area,
                    }
                )    
            );
            area_strategies.set(
                "NoStopDate", 
                new StrategyExecutorAbstraction(
                    {
                        function_to_run: this.area__no_stop_date,
                        parameter_obj: serie.time_area,
                    }
                )
            );

            let area_strategy = area_strategies.get(serie.time_area.method_name);
            let scope = area_strategy.run({ start_date: serie.time_area.start_date });
            
            let pattern_strategy = pattern_strategies.get(serie.pattern.pattern_routine);

            let events = [];

            let date_cursor = scope.start_date;
            let instance_cursor = 0;
            let cycle_cursor = 0;

            let event_sample = {
                title: serie.time.title,
                start: serie.time.start,
                end: serie.time.end,
                color: serie.time.color,
            }
            while ((scope.stop_within_date !== undefined && date_cursor < scope.stop_within_date) || (scope.instance_limit !== 0 && scope.instance_limit >= instance_cursor)) {

                /* 
                    There are two ways we monitor our "progress" here. One is by the date cursor, and one is by instances.
                    In some cases we only want to do the repetition pattern until a set date, other times we wish do it X times. 
                    Hence we need to have this "cycle manager" to handle the repeating for us - and alleviate the strategies from 
                    having to concern themselves with this. This in turn means that a repetition pattern/strategy is run in cycles - as one may see in their
                    respective implementations, and this does to some degree dictate implementations.
                    This does put the onus of managing the end of the series/repetition on the cycle manager (which is what this is.)
                */
                event_sample = Object.assign({}, event_sample);
                let result = pattern_strategy.run({cycle: cycle_cursor, start_date: date_cursor, event: event_sample});

                if (result === undefined || (Array.isArray(result) && result.length == 0)) {
                    cycle_cursor++;
                    continue;
                }

                if (scope.stop_within_date !== undefined) {
                    if (result.from > scope.stop_within_date) {
                        break;
                    }
                }
                if (scope.instance_limit !== undefined &&  scope.instance_limit !== undefined) {
                    if (instance_cursor > scope.instance_limit) {
                        break;
                    }
                }

                let move_cursor_to = date_cursor
                if (Array.isArray(result)) {
                    move_cursor_to = result[result.length - 1].to
                }
                else {
                    move_cursor_to = result.to
                }

                date_cursor = move_cursor_to
                date_cursor = date_cursor.addDays(1)

                if (scope.instance_limit !== 0) {
                    instance_cursor++;
                }

                if (Array.isArray(result)) {
                    events = events.concat(result);
                }
                else {
                    events.push(result);
                }

                cycle_cursor++;
            }

            return events;
        }

        static area__stop_within({start_date, stop_within_date} = {}) {
            return {
                start_date: new Date(start_date),
                stop_within_date: new Date(stop_within_date),
                instance_limit: 0,
            }
        }

        static area__stop_after_x_instances({start_date, instances} = {}) {
            return {
                start_date: new Date(start_date),
                stop_within_date: undefined,
                instance_limit: instances,
            }
        }

        static area__no_stop_date({start_date, projectionDistanceInMonths} = {}) {
            start_date = new Date(start_date)

            let stop_within_date = new Date(start_date)
            let month = start_date.getMonth();
            stop_within_date.setMonth(parseInt(month) + parseInt(projectionDistanceInMonths));
            return {
                start_date: start_date,
                stop_within_date: stop_within_date,
                instance_limit: 0
            }
        }

        static daily__every_x_day({cycle, start_date, event, interval}={}) {

            if (cycle != 0) {
                start_date = start_date.addDays(interval - 1); // -1 to account for the "move-forward" padding done in cycler
            }

            event.from = DateExtensions.OverwriteDateTimeWithTimeInputValue(start_date, event.start);
            event.to = DateExtensions.OverwriteDateTimeWithTimeInputValue(start_date, event.end);

            return event;
        }

        static daily__every_weekday({cycle, event, start_date}={}) {
            while ([0,6].includes(start_date.getDay())) {
                start_date = start_date.addDays(1);
            }

            event.from = DateExtensions.OverwriteDateTimeWithTimeInputValue(start_date, event.start);
            event.to = DateExtensions.OverwriteDateTimeWithTimeInputValue(start_date, event.end);

            return event;
        }

        static weekly_standard({cycle, start_date, event, week_interval, days}={}) {
            if (cycle != 0) {
                /* 
                We need to make sure that we always work with monday as base excepting when we are running the first cycle (0), as
                the user can specify a start_date in the middle of a week. The end, as is the standard in the other strategies, is 
                the responsibility of the cycle runner, so we don't care about that here.
                */
                if (start_date.getDay() !== 1) {
                    if (start_date.getDay != 0) {
                        start_date = start_date.addDays( (start_date.getDay() - 1) * -1)
                    }
                    else if (start_date.getDay == 0) {
                        start_date = start_date.addDays(1)
                    }
                }

                start_date = start_date.addDays(7 * week_interval)
            }

            let events = [];
            let y = 0;
            for (let i = start_date.getDay(); i < 6; i++) {
                let day = days.get(i)
                if (day === true) {
                    let adjusted_date = (new Date(start_date)).addDays(y);
                    let ev_copy = Object.assign({}, event);
                    ev_copy.from = DateExtensions.OverwriteDateTimeWithTimeInputValue(adjusted_date, event.start)
                    ev_copy.to = DateExtensions.OverwriteDateTimeWithTimeInputValue(adjusted_date, event.end);

                    events.push(ev_copy);
                }

                y++;
            }

            return events;
        }

        static month__every_x_day_every_y_month({cycle, start_date, day_of_month, event, interval}={}) {
            if (cycle !== 0)  {
                start_date.setMonth(start_date.getMonth() + parseInt(interval))
                start_date.setDate(1);
            }

            if (day_of_month > start_date.getDate()) {
                return;
            }

            let adjusted_date = (new Date(start_date)).setDate(day_of_month);
            event.from = DateExtensions.OverwriteDateTimeWithTimeInputValue(adjusted_date, event.start);
            event.to = DateExtensions.OverwriteDateTimeWithTimeInputValue(adjusted_date, event.end);

            return event;
        }

        static arbitrator_find(start_date, arbitrator, weekday) {
           // helps us parse from 1,2,3,4,5,6,7 to 0,1,2,3,4,5,6 that JS uses
           let weekDayParseReverseMap = new Map([
               [0, 7],
               [6, 6],
               [5, 5],
               [4, 4],
               [3, 3],
               [2, 2],
               [1, 1],
           ]);

           // Before we can do anything we need to find the first occurrence of weekday 
           // in the month

           let month = start_date.getMonth();

           let date = new Date(start_date);
           date.setDate(1);
           let first_weekday_of_month = date.getDay();
           if (weekDayParseReverseMap.get(first_weekday_of_month) > weekday) { // not present in first week, go to second
               date = date.addDays(7);
           }

           // go to the first instance of weekday
           let weekdaydiff = parseInt(weekDayParseReverseMap.get(date.getDay())) - parseInt(weekday);
           if (weekdaydiff > 0) {
               date = date.addDays(weekdaydiff * -1);
           }
           else {
               date = date.addDays(weekdaydiff * 1);
           }

           // go to the desired position, as determined by the arbitrator (is that even the right word? :D)
           date = date.addDays(arbitrator * 7);
           if (arbitrator == 5) {
               if (date.getMonth() !== month) { // last instance of weekday is in week 4
                   date = date.addDays(4 * 7);
               }
           }

           return date;
        }

        static month__every_arbitrary_date_of_month({cycle, event, start_date, arbitrator, weekday, interval}={}) {
            if (cycle != 0) {
                start_date.setDate(1);
                let month = start_date.getMonth();
                start_date.setMonth(month + parseInt(interval));
            }

            let date = SeriesUtil.arbitrator_find(start_date, arbitrator, weekday);
            event.from = DateExtensions.OverwriteDateTimeWithTimeInputValue(date, event.start);
            event.to = DateExtensions.OverwriteDateTimeWithTimeInputValue(date, event.end)

            return event;
        }

        static yearly__every_x_of_month ({cycle, start_date, event, day_index, year_interval, month}={}) {
            if (cycle !== 0)  {
                start_date.setFullYear ( start_date.getFullYear() + parseInt(year_interval) )
            }

            let date = new Date(start_date.getFullYear() + "-" + month + "-" + day_index);
            event.from = DateExtensions.OverwriteDateTimeWithTimeInputValue(date, event.start);
            event.to = DateExtensions.OverwriteDateTimeWithTimeInputValue(date, event.end);

            return event;
        }
        
        static yearly__every_arbitrary_weekday_in_month ({cycle, start_date, event, arbitrator, weekday, year_interval, month}={}) {
            if (cycle != 0) {
                start_date.setFullYear ( start_date.getFullYear() + parseInt(year_interval) )
            }

            let date = new Date(start_date.getFullYear() + "-" + month + "-01");
            
            // use the "day-seek" algo to find the correct day, according to the arbitrator
            date = SeriesUtil.arbitrator_find(date, arbitrator, weekday);
            
            event.from = DateExtensions.OverwriteDateTimeWithTimeInputValue(date, event.start);
            event.to = DateExtensions.OverwriteDateTimeWithTimeInputValue(date, event.end);

            return event;
        }
    };
}

class RendererManager {

    constructor({context, 
                renderers = undefined, 
                onClickEditButton = undefined, 
                onClickInfoButton = undefined, 
                planner=undefined} = {}) {

        if (typeof (renderers) !== "array") {
            renderers = [];
        }

        this.renderers = renderers;
        this.planner = planner;

        this.onClickEditButton = onClickEditButton;
        this.onClickInfoButton = onClickInfoButton;

        this.onClickDeleteSeriesButton = function (series_uuid) {
            context.delete_serie(series_uuid);
        }

        this.onClickDeleteButton = function (eventId) {
            context.remove_event(eventId)
        }

        context.onEventsChanged = function (events) {
            if (this.renderers !== undefined) {
                this.renderers.forEach(element => {
                    element.render(events);
                });
            }
        }
        context.onSeriesChanged = function (events) {
            if (this.renderers !== undefined) {
                this.renderers.forEach(element => {
                    element.render(events);
                });
            }
        }
    }

    add_renderer(renderer) {
        renderer.onClickEditButton = this.onClickEditButton;
        renderer.onClickDeleteButton = this.onClickDeleteButton;
        renderer.onClickDeleteSeriesButton = this.onClickDeleteSeriesButton;
        renderer.planner = this.planner;

        this.renderers.push(renderer);
    }

    render(events) {
        this.renderers.forEach(element => {
            element.render(events);
        });
    }

}

class RendererBase {
    constructor() {
        if (this.constructor == RendererManager) {
            throw new Error("Abstract classes can't be instantiated");
        }
    }

    /* 
        Force the renderer to render itself
    */
    render() {
        throw new Error("Method 'render()' must be implemented");
    }
}

/* 
    Provides utilities to wrap around and manage a FullCalendar calendar instance fluidly
*/

let focused_event_uuid = undefined;
let focused_serie_uuid = undefined;

class CalendarManager extends RendererBase {

    constructor(element_id, fc_options) {
        super(RendererBase);
        this.element_id = element_id;
        this.fc_options = fc_options;
        this.calendar = undefined;
        this.rememberedInitialView = "dayGridMonth";

        this.fc_options.eventContent = (arg) => {

            let rootNode = this.RenderingUtilities.renderEventForView(arg.view.type, arg);
            return { 
                html: rootNode.outerHTML
            };
        }

        this.fc_options.eventResize = (eventResizeInfo) => {
            let event = {
                id: eventResizeInfo.event.extendedProps.event_uuid,
                title: eventResizeInfo.event.title,
                from: eventResizeInfo.event.start,
                to: eventResizeInfo.event.end,
                color: eventResizeInfo.event.backgroundColor,
            };

            this.planner.local_context.update_event(event, event.id);
        }

        this.fc_options.eventDrop = (eventDropInfo) => {
            let event = {
                id: eventDropInfo.event.extendedProps.event_uuid,
                title: eventDropInfo.event.title,
                from: eventDropInfo.event.start,
                to: eventDropInfo.event.end,
                color: eventDropInfo.event.backgroundColor,
            };
            
            this.planner.local_context.update_event(event, event.id);
        }

        this.fc_options.eventDidMount = (arg) => {
            console.log(arg.event.extendedProps.event_uuid);
            const at_first = arg.event.extendedProps.event_uuid;
            focused_event_uuid = at_first;
            focused_serie_uuid = arg.event.extendedProps.serie_uuid;

            arg.el.addEventListener("contextmenu", (jsEvent) => {
                jsEvent.preventDefault();
                console.log(jsEvent)

                let argCopy = Object.assign({}, arg);
                focused_event_uuid= argCopy.event.extendedProps.event_uuid;
                let onClickEditButton = this.onClickEditButton;
                let onClickDeleteButton = this.onClickDeleteButton;
                let onClickDeleteSeriesButton = this.onClickDeleteSeriesButton;

                let callback = function () {
                    onClickEditButton(focused_event_uuid)
                }

                let items = {
                    edit: {
                        name: "<i class='fas fa-edit'></i> " + this.planner.textLib.get("edit"),
                        isHtmlName: true,
                        callback: callback
                    },
                    delete: {
                        name: "<i class='fas fa-trash'></i> " + this.planner.textLib.get("delete"),
                        isHtmlName: true,
                        callback: function (key, opt) {
                            onClickDeleteButton(focused_event_uuid);
                        }
                    },
                }

                $.contextMenu({
                    className: "webook-context-menu",
                    selector: '.fc-event-main, .fc-daygrid-event',
                    items: items,
                });
            })
        }
    }

    RenderingUtilities = class RenderingUtilities {

        static renderEventForView(view_name, ev_info) {
            let viewsToRendererMap = new Map([
                ["dayGridMonth", this.renderDayGridMonth_Event],
                ["timeGridWeek", this.renderWeek_Event],
                ["timeGridDay", this.renderWeek_Event]
            ]);
            this.viewsToRendererMap = viewsToRendererMap;

            let renderer_function = this.viewsToRendererMap.get(view_name)
            if (renderer_function === undefined) {
                throw "No event renderer for this view -> (" + view_name + ")";
            }

            return renderer_function(ev_info, this.get_icons_html(ev_info))
        }

        static get_icons_html(info) {
            let icons_wrapper = document.createElement('div');

            if (info.event.extendedProps.serie_uuid !== undefined) {
                let icon = document.createElement('i');
                icon.classList.add('fas', 'fa-link');
                icons_wrapper.appendChild(icon);
            }

            return icons_wrapper.outerHTML;
        }

        static renderDayGridMonth_Event(info, icons_html) {
            let rootWrapperNode = document.createElement("span");
            rootWrapperNode.style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;"
            rootWrapperNode.innerHTML = "&nbsp;<span><i class='fas fa-circle' style='color: " + info.backgroundColor + "'></i></span>&nbsp; <strong>(" + info.timeText + ")</strong> " + info.event.title + "&nbsp;&nbsp; <span style='text-align:right;'><i class='fas fa-ellipsis-v'></i></span>";
            return rootWrapperNode;
        }

        static renderWeek_Event(info, icons_html) {
            let rootWrapperNode = document.createElement("span");

            rootWrapperNode.innerHTML = "<strong>" + info.timeText + "</strong>" + icons_html + "<div>" + info.event.title + "</div>"
            
            return rootWrapperNode;
        }
    }

    convert_events(events) {
        let fc_events = []
        for (let i = 0; i < events.length; i++) {
            let event = events[i];
            fc_events.push({
                "title": event.title,
                "start": event.from,
                "end": event.to,
                "extendedProps": {
                    "event_uuid": event.id,
                    "serie_uuid": event.serie_uuid
                },
                "backgroundColor": event.color,
            })
        }

        return fc_events;
    }

    render(events) {
        let calendar_element = document.getElementById(this.element_id);

        let fc_events = this.convert_events(events);
        this.fc_options.events = fc_events;

        if (this.calendar !== undefined) {
            this.fc_options.initialView = this.calendar.view.type;
            this.fc_options.initialDate = this.calendar.getDate();
        }

        this.calendar = new FullCalendar.Calendar(calendar_element, this.fc_options);
        this.calendar.render();
    }
}

class TimeLineManager extends RendererBase {

    constructor(timeline_element_id) {
        super(RendererBase);
        this.timeline_element = document.getElementById(timeline_element_id);
        this.options = {};
        this.timeline = undefined;   
        this.dataset = new vis.DataSet();
    }

    flush_dataset() {
        this.dataset.clear();
    }

    read_in_events(events) {
        let events_converted = [];

        for (let i = 0; i < events.length; i++) {
            let event = events[i];
            events_converted.push({
                id: i,
                content: event.title,
                start: event.from.toISOString(),
                end: event.to.toISOString(),
                style: "background-color:" + event.color + ";",
            })
        }

        this.flush_dataset();
        this.dataset.add(events_converted);
    }

    render (events) {
        this.read_in_events(events);
        if (this.timeline === undefined) {
            this.timeline = new vis.Timeline(this.timeline_element, this.dataset, this.options);
        }
        else {
            this.timeline.redraw();
            this.timeline.fit();
        }
    }
}

/* 
    Provides utilities to wrap around and manage a simple HTML table
*/
class SimpleTableManager extends RendererBase {

    constructor(table_element_id, onClickDeleteButton, onClickEditButton, onClickInfoButton) {
        super(RendererBase);
        this.table_element_id = table_element_id;
        this.table_element = document.getElementById(this.table_element_id);
        this.tbody_element = this.table_element.getElementsByTagName('tbody')[0];

        this.onClickDeleteButton = onClickDeleteButton;
        this.onClickEditButton = onClickEditButton;
        this.onClickInfoButton = onClickInfoButton;

        this.primary_render()
    }

    /* 
        Gets all the rows in the current table (as elements)
    */
    get_rows() {
        return this.tbody_element.getElementsByTagName('tr');
    }

    /* 
        Removes all rows from the table
    */
    flush_rows() {
        let rows = this.get_rows();
        for (let i = rows.length; i >= 0; i--) {
            if (rows[i] !== undefined) {
                rows[i].remove();
            }
        }
    }

    add_row(row_element) {
        this.tbody_element.appendChild(row_element);
    }

    convert_event_to_row(event) {
        let row = document.createElement('tr');

        let color_col = document.createElement('td');
        color_col.innerHTML = "";
        color_col.style="background-color:" + event.color + ";";

        let name_col = document.createElement('td');
        name_col.innerText = event.title;

        let time_col = document.createElement('td');
        time_col.innerText = event.from + " " + event.to;

        let options_col = document.createElement('td');

        let onClickEditButton = this.onClickEditButton;
        let onClickDeleteButton = this.onClickDeleteButton;
        let onClickInfoButton = this.onClickInfoButton;

        let edit_button = document.createElement('button');
        edit_button.classList.add('btn', 'btn-success', 'btn-sm', 'btn-block')
        edit_button.onclick = function () { onClickEditButton(event.id); }
        edit_button.innerText = "Edit";
        let delete_button = document.createElement('button');
        delete_button.classList.add('btn', 'btn-danger', 'btn-sm','btn-block')
        delete_button.onclick = function () { onClickDeleteButton(event.id); }
        delete_button.innerText = "Delete";

        options_col.append(edit_button, delete_button);

        row.append(
            color_col,
            name_col,
            time_col,
            options_col
        );

        return row;
    }

    primary_render() {
        let thead_el = this.table_element.getElementsByTagName('thead')[0];
        let tbody_el = this.table_element.getElementsByTagName('tbody')[0];
        let tfoot_el = this.table_element.getElementsByTagName('tfoot')[0];

        let theadRow = document.createElement('tr');

        let theadColorCol = document.createElement('th');

        let theadNameCol = document.createElement('th');
        theadNameCol.innerText = "Name";

        let theadTimeCol = document.createElement('th');
        theadTimeCol.innerText = "Time";

        let theadOptionsCol = document.createElement('th');
        theadOptionsCol.innerText = "Options";

        theadRow.append(theadColorCol, theadNameCol, theadTimeCol, theadOptionsCol);
        thead_el.append(theadRow)
    }

    render(events) {
        this.flush_rows();

        for (let i = 0; i < events.length; i++) {
            this.add_row(this.convert_event_to_row(events[i]));
        }
    }
}