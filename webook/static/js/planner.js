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
    Top level "manager" class for the planner and interfacing with it. Highest abstraction level,
    and probably will serve all use cases.
*/
class Planner {
    constructor({ onClickEditButton, onClickInfoButton } = {}) {
        this.local_context = new LocalPlannerContext(this)
        this.renderer_manager = new RendererManager(
            /*context:PlannerContext*/this.local_context,
            /*renderers:Array*/undefined,
            onClickEditButton,
            onClickInfoButton,
        )

        this.local_context.onSeriesChanged = function (events, planner) {
            console.log("series added")
        }

        this.local_context.onEventsCreated = function (events, planner) {
            planner.init();
        }

        this.local_context.onEventUpdated = function (event, planner) {
            planner.init();
        }

        this.local_context.onEventsDeleted = function (event, planner) {
            planner.init();
        }

        this.local_context.onEventDeleted = function (event, planner) {
            planner.init();
        }
    }

    init() {
        this.renderer_manager.render(this.local_context.events);
    }
}

/* handle synchronizing data between multiple contexts */
class ContextSynchronicityManager {

}

class UpstreamPlannerContext {
    constructor(planner_backref) {

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
        this.series = [];
        this.events = [];

        this.planner = planner_backref

        this.onEventsChanged = function (events) { };
        this.onSeriesChanged = function (events) { };
    }

    add_serie(serie) {
        let id = (this.series.push(serie) -1);
        this.add_events(this.SeriesUtil.calculate_serie(serie), id);
        this.onSeriesChanged(this.events, this.planner);
    }

    add_event(event) {
        this.events.push(event);
        this.onEventsCreated(this.events, this.planner);
    }

    update_event(event, index) {
        this.events[index] = event;
        this.onEventUpdated(this.events, this.planner);
    }

    add_events(events, serie_id=undefined) {
        if (serie_id !== undefined) {
            events.forEach(function (event) {
                event.serie_id = serie_id;
            })
        }

        this.events = this.events.concat(events);
        this.onEventsCreated(this.events, this.planner);
    }

    remove_event(index) {
        this.events.splice(index, 1);
        this.onEventDeleted(this.events, this.planner);
    }

    remove_events(indices) {
        indices.forEach(function (index) {
            remove_event(index);
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
                            stop_within_date: serie.time_area.stop_within
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

            while ((scope.stop_within_date !== undefined && date_cursor <= scope.stop_within_date) || (scope.instances !== 0 && scope.instances >= instance_cursor)) {

                /* 
                    There are two ways we monitor our "progress" here. One is by the date cursor, and one is by instances.
                    In some cases we only want to do the repetition pattern until a set date, other times we wish do it X times. 
                    Hence we need to have this "cycle manager" to handle the repeating for us - and alleviate the strategies from 
                    having to concern themselves with this. This in turn means that a repetition pattern/strategy is run in cycles - as one may see in their
                    respective implementations, and this does to some degree dictate implementations.
                    This does put the onus of managing the end of the series/repetition on the cycle manager (which is what this is.)
                */

                let result = pattern_strategy.run({cycle: cycle_cursor, start_date: date_cursor, event: event_sample});

                if (result === undefined || (Array.isArray(result) && result.length == 0)) {
                    cycle_cursor++;
                    continue;
                }

                if (result.from > scope.stop_within_date) {
                    break;
                }

                if (scope.stop_within_date !== undefined) {
                    let move_cursor_to = date_cursor
                    if (Array.isArray(result)) {
                        move_cursor_to = result[result.length - 1].to
                    }
                    else {
                        move_cursor_to = result.to
                    }

                    date_cursor = move_cursor_to
                    date_cursor = date_cursor.addDays(1)
                }

                if (scope.instances !== 0) {
                    if (typeof(result) == "array") {
                        instance_cursor += result.length;
                    }
                    else {
                        instance_cursor++;
                    }
                }

                if (Array.isArray(result)) {
                    events = events.concat(result);
                }
                else {
                    events.push(result);
                }

                cycle_cursor++;
            }


            console.log(events);

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

        static area__no_stop_date({start_date, project_x_months} = {}) {
            return {
                start_date: new Date(start_date),
                stop_within_date: new Date(start_date.setMonth(start_date.getMonth()+project_x_months)),
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
                    event.from = DateExtensions.OverwriteDateTimeWithTimeInputValue(adjusted_date, event.start)
                    event.to = DateExtensions.OverwriteDateTimeWithTimeInputValue(adjusted_date, event.end);

                    events.push(event);
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
           let weekDayParseReverseMap = new Map();
           weekDayParseReverseMap.set(0, 7);
           weekDayParseReverseMap.set(6, 6);
           weekDayParseReverseMap.set(5, 5);
           weekDayParseReverseMap.set(4, 4);
           weekDayParseReverseMap.set(3, 3);
           weekDayParseReverseMap.set(2, 2);
           weekDayParseReverseMap.set(1, 1)

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
                console.log(start_date)
                start_date.setDate(1);
                let month = start_date.getMonth();
                start_date.setMonth(month + interval);
            }

            date = SeriesUtil.arbitrator_find(start_date, arbitrator, weekday);
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

    constructor(context, renderers = undefined, onClickEditButton = undefined, onClickInfoButton = undefined) {
        if (typeof (renderers) !== "array") {
            renderers = [];
        }

        this.renderers = renderers;

        this.onClickEditButton = onClickEditButton;
        this.onClickInfoButton = onClickInfoButton;

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
class CalendarManager extends RendererBase {

    constructor(element_id, fc_options) {
        super(RendererBase);
        this.element_id = element_id;
        this.fc_options = fc_options;
        this.calendar = undefined;
        this.rememberedInitialView = "dayGridMonth";

        this.fc_options.eventDidMount = (arg) => {
            const eventId = arg.event.id
            const isRepeated = arg.event._def.extendedProps.serieIndex !== undefined;
            const isDeviatedFromRepetitionBase = arg.event._def.extendedProps.altered;

            console.log(arg.event._def);

            arg.el.addEventListener("contextmenu", (jsEvent) => {
                jsEvent.preventDefault();

                let onClickEditButton = this.onClickEditButton;
                let onClickDeleteButton = this.onClickDeleteButton;

                let items = {
                    edit: {
                        name: "<i class='fas fa-edit'></i> Rediger",
                        isHtmlName: true,
                        callback: function (key, opt){
                            onClickEditButton(arg.event._def.extendedProps.eventIndex);
                        }
                    },
                    delete: {
                        name: "<i class='fas fa-trash'></i> Slett",
                        isHtmlName: true,
                        callback: function (key, opt) {
                            onClickDeleteButton(arg.event._def.extendedProps.eventIndex);
                        }
                    },
                }

                if (isRepeated === true) {
                    items.delete_repetition = {
                        name: "<i class='fas fa-trash'></i> Kanseller gjentagende hendelse",
                        isHtmlName: true,
                    }
                }

                let ctx_menu = $.contextMenu({
                    className: "webook-context-menu",
                    selector: '.fc-event-main',
                    items: items,
                });
            })
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
                    "eventIndex": i,
                    "serieIndex": event.serie_id
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

    stringify_date(date_obj) {
        
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

        console.log(onClickEditButton)

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

    convert_event_to_row(event, index) {
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
        edit_button.onclick = function () { onClickEditButton(index); }
        edit_button.innerText = "Edit";
        let delete_button = document.createElement('button');
        delete_button.classList.add('btn', 'btn-danger', 'btn-sm','btn-block')
        delete_button.onclick = function () { onClickDeleteButton(index); }
        delete_button.innerText = "Delete";
        let info_button = document.createElement('button')
        info_button.classList.add('btn', 'btn-primary', 'btn-sm', 'btn-block')
        info_button.onclick = function () { onClickInfoButton(index); }
        info_button.innerText = "Info"

        options_col.append(edit_button, delete_button, info_button);

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
            this.add_row(this.convert_event_to_row(events[i], i));
        }
    }
}

/*
    Represents a Serie; an instruction on how to generate a collection of events in series 
*/
class Serie {
    constructor({time, pattern, time_area} = {}) {
        self.time = time
        self.pattern = pattern
        self.time_area = time_area
    }
}


/* 
    Represents an event; something that happens
*/
class CalendarEvent {
    constructor(title, start, end) {
        this.title = title;
        this.start = start;
        this.end = end;
    }
}